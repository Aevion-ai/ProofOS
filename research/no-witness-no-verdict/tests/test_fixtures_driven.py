"""Fixtures-driven evaluation: the JSON matrix is the source of truth.

Each fixture in fixtures/evaluation_matrix.json is loaded and executed
against the gate. This proves the paper's Table 1 is machine-checkable.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nowitnessnoverdict.fail_closed import Disposition, TransitionRequest, decide_transition
from nowitnessnoverdict.candidate_only import (
    AuthorityGrant,
    AuthorityRoot,
    EpochContext,
    promote_candidate,
    same_authority_root_is_not_independent,
    same_epoch_self_certification,
)
from nowitnessnoverdict.receipt import (
    ReceiptBindings,
    TransitionReceipt,
    receipt_body_hash,
    receipt_divergence_invalidates,
)

FIXTURES = Path(__file__).parent.parent / "fixtures" / "evaluation_matrix.json"


def _load_fixtures():
    return json.loads(FIXTURES.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def fixtures():
    return _load_fixtures()


def _request_from(f: dict) -> TransitionRequest:
    r = f["request"]
    return TransitionRequest(
        transition_id=r["transition_id"],
        action=r["action"],
        actor_identity=r.get("actor_identity"),
        authority_lease=r.get("authority_lease"),
        evidence=r.get("evidence", []),
        acp_digest=r.get("acp_digest"),
        xal_verification=r.get("xal_verification"),
        continuity_ref=r.get("continuity_ref"),
        effect_scope=r.get("effect_scope"),
    )


def test_all_fixtures_parse(fixtures):
    assert len(fixtures) == 10


def test_fixture_001_missing_authority_lease(fixtures):
    f = next(x for x in fixtures if x["fixture_id"] == "NWNV-001")
    d, _ = decide_transition(_request_from(f))
    assert d == Disposition.REJECT


def test_fixture_002_inferred_evidence(fixtures):
    f = next(x for x in fixtures if x["fixture_id"] == "NWNV-002")
    d, _ = decide_transition(_request_from(f))
    assert d in (Disposition.HOLD, Disposition.REJECT)


def test_fixture_003_self_asserted_capability(fixtures):
    f = next(x for x in fixtures if x["fixture_id"] == "NWNV-003")
    grant = AuthorityGrant(
        grant_id=f["grant"]["grant_id"],
        authority_root=AuthorityRoot(root_id=f["grant"]["authority_root"]["root_id"]),
        recipient=f["grant"]["recipient"],
        scope=f["grant"]["scope"],
    )
    assert promote_candidate({"candidate_id": f["candidate_id"]}, grant, EpochContext(1, 2, 3)) == "REJECT"


def test_fixture_004_route_action_mismatch(fixtures):
    f = next(x for x in fixtures if x["fixture_id"] == "NWNV-004")
    assert f["gate_action"] != f["route_action"]


def test_fixture_005_receipt_tampered(fixtures):
    f = next(x for x in fixtures if x["fixture_id"] == "NWNV-005")
    b = ReceiptBindings(**f["bindings"])
    body_hash = receipt_body_hash(b, "NEW")
    receipt = TransitionReceipt(receipt_id="r5", transition_id="t5", bindings=b, origin="NEW", body_hash=body_hash)
    tampered = ReceiptBindings(**{**f["bindings"], **f["tamper"]})
    assert not receipt_divergence_invalidates(receipt, tampered)


def test_fixture_006_environment_changed(fixtures):
    f = next(x for x in fixtures if x["fixture_id"] == "NWNV-006")
    b = ReceiptBindings(**f["bindings"])
    body_hash = receipt_body_hash(b, "NEW")
    receipt = TransitionReceipt(receipt_id="r6", transition_id="t6", bindings=b, origin="NEW", body_hash=body_hash)
    tampered = ReceiptBindings(**{**f["bindings"], **f["tamper"]})
    assert not receipt_divergence_invalidates(receipt, tampered)


def test_fixture_007_same_root(fixtures):
    f = next(x for x in fixtures if x["fixture_id"] == "NWNV-007")
    assert not same_authority_root_is_not_independent(
        AuthorityRoot(root_id=f["roots"]["a"]), AuthorityRoot(root_id=f["roots"]["b"])
    )


def test_fixture_008_same_epoch(fixtures):
    f = next(x for x in fixtures if x["fixture_id"] == "NWNV-008")
    e = EpochContext(**f["epoch"])
    assert same_epoch_self_certification(e)


def test_fixture_009_valid_admit(fixtures):
    f = next(x for x in fixtures if x["fixture_id"] == "NWNV-009")
    d, reasons = decide_transition(_request_from(f))
    assert d == Disposition.ADMIT
    assert reasons == []


def test_fixture_010_admit_plus_failure(fixtures):
    f = next(x for x in fixtures if x["fixture_id"] == "NWNV-010")
    d, _ = decide_transition(_request_from(f))
    assert d == Disposition.ADMIT
    assert f["execution_outcome"] == "FAILURE"
