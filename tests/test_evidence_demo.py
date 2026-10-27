"""Oct 29 customer-gate: evidence, policy, receipts, replay."""

from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path

import pytest

from aevion_runtime.attestation import Attestation, AttestationRejected
from aevion_runtime.canonical import CanonicalJson
from aevion_runtime.demo import DemoScenarios
from aevion_runtime.evidence import EvidenceVerifier
from aevion_runtime.ledger import Ledger
from aevion_runtime.receipt import Receipt
from aevion_runtime.replay import MISSING_ANCHORS_REASON, Replay


@pytest.fixture
def ledger_path(tmp_path: Path) -> Path:
    return tmp_path / "ledger.jsonl"


class TestAuthenticEvidence:
    def test_verify_pass(self) -> None:
        bundle = DemoScenarios.allow_bundle()
        verdict = EvidenceVerifier.verify(bundle)
        assert verdict.passed
        assert verdict.reason == "PASS"

    def test_attest_allow_writes_receipt(self, ledger_path: Path) -> None:
        receipt = Attestation.run(DemoScenarios.allow_bundle(), ledger_path)
        assert receipt["decision"] == "ALLOW"
        assert receipt["evidence_verdict"] == "PASS"
        assert Ledger.line_count(ledger_path) == 1


class TestForgedEvidence:
    def test_forged_rejects_no_ledger_write(self, ledger_path: Path) -> None:
        allow = DemoScenarios.allow_bundle()
        Attestation.run(allow, ledger_path)
        before = Ledger.line_count(ledger_path)
        for _label, bundle in DemoScenarios.forged_cases(allow):
            with pytest.raises(AttestationRejected):
                Attestation.run(bundle, ledger_path)
            assert Ledger.line_count(ledger_path) == before

    def test_attest_or_exit_nonzero(self, ledger_path: Path) -> None:
        from aevion_runtime.attestation import Attestation

        bad = dict(DemoScenarios.allow_bundle())
        bad["artifact_sha256"] = "f" * 64
        with pytest.raises(SystemExit) as exc:
            Attestation.run_or_exit(bad, ledger_path)
        assert exc.value.code == 1
        assert Ledger.line_count(ledger_path) == 0


class TestPolicyGated:
    def test_allow_on_safe_envelope(self, ledger_path: Path) -> None:
        receipt = Attestation.run(DemoScenarios.allow_bundle(), ledger_path)
        assert receipt["decision"] == "ALLOW"
        assert receipt["policy_version"] == "aevion-proofos-v1.0"

    def test_deny_on_verified_unsafe_deployable(self, ledger_path: Path) -> None:
        receipt = Attestation.run(DemoScenarios.deny_bundle(), ledger_path)
        assert receipt["decision"] == "DENY"
        assert receipt["evidence_verdict"] == "PASS"
        assert receipt["policy_version"] == "aevion-proofos-v1.0"
        assert "is_safe_deployable" in receipt["policy_reason"]

    def test_forged_byte_tamper_sha256_mismatch(self) -> None:
        allow = DemoScenarios.allow_bundle()
        label, bundle = DemoScenarios.forged_cases(allow)[0]
        assert label == "artifact byte tampered"
        verdict = EvidenceVerifier.verify(bundle)
        assert not verdict.passed
        assert "artifact_sha256 does not match" in verdict.reason


class TestReceiptChain:
    def test_receipt_id_is_sha256_of_canonical_body(self, ledger_path: Path) -> None:
        receipt = Attestation.run(DemoScenarios.allow_bundle(), ledger_path)
        assert Receipt.verify_id(receipt)

    def test_chained_prev_receipt_id(self, ledger_path: Path) -> None:
        first = Attestation.run(DemoScenarios.allow_bundle(), ledger_path)
        second = Attestation.run(DemoScenarios.deny_bundle(), ledger_path)
        assert second["prev_receipt_id"] == first["receipt_id"]


class TestReplay:
    def _two_receipt_ledger(self, ledger_path: Path) -> tuple[str, int]:
        Attestation.run(DemoScenarios.allow_bundle(), ledger_path)
        second = Attestation.run(DemoScenarios.deny_bundle(), ledger_path)
        Ledger.seal(ledger_path, receipt_count=2, tip_receipt_id=second["receipt_id"])
        return second["receipt_id"], 2

    def test_replay_matches_clean_ledger(self, ledger_path: Path) -> None:
        tip, count = self._two_receipt_ledger(ledger_path)
        assert Replay.run(ledger_path, expect_tip=tip, expect_count=count) == 0

    def test_replay_fails_missing_anchors(self, ledger_path: Path) -> None:
        self._two_receipt_ledger(ledger_path)
        failure = Replay.check(ledger_path)
        assert failure is not None
        assert failure.ledger_index == 0
        assert failure.reason == MISSING_ANCHORS_REASON

    def test_replay_fails_wrong_expect_tip(self, ledger_path: Path) -> None:
        tip, count = self._two_receipt_ledger(ledger_path)
        failure = Replay.check(
            ledger_path, expect_tip="0" * 64, expect_count=count
        )
        assert failure is not None
        assert failure.reason.startswith("expect-tip mismatch:")
        assert tip in failure.reason

    def test_replay_fails_wrong_expect_count(self, ledger_path: Path) -> None:
        tip, count = self._two_receipt_ledger(ledger_path)
        failure = Replay.check(ledger_path, expect_tip=tip, expect_count=count + 1)
        assert failure is not None
        assert failure.reason == f"expect-count mismatch: expected {count + 1} got {count}"

    def test_replay_fails_seal_deleted(self, ledger_path: Path) -> None:
        tip, count = self._two_receipt_ledger(ledger_path)
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        ledger_path.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
        failure = Replay.check(ledger_path, expect_tip=tip, expect_count=count)
        assert failure is not None
        assert failure.reason == "missing SEAL terminal record"

    def test_replay_fails_last_receipt_and_seal_deleted(self, ledger_path: Path) -> None:
        tip, count = self._two_receipt_ledger(ledger_path)
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        ledger_path.write_text(lines[0] + "\n", encoding="utf-8")
        failure = Replay.check(ledger_path, expect_tip=tip, expect_count=count)
        assert failure is not None
        assert failure.reason == "missing SEAL terminal record"

    def test_replay_fails_handmade_seal_truncated(self, ledger_path: Path) -> None:
        tip, count = self._two_receipt_ledger(ledger_path)
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        receipt0 = json.loads(lines[0])
        fake_seal = CanonicalJson.dumps(
            {
                "record_type": "SEAL",
                "receipt_count": 1,
                "tip_receipt_id": receipt0["receipt_id"],
            }
        )
        ledger_path.write_text(lines[0] + "\n" + fake_seal + "\n", encoding="utf-8")
        failure = Replay.check(ledger_path, expect_tip=tip, expect_count=count)
        assert failure is not None
        assert failure.reason == f"expect-count mismatch: expected {count} got 1"

    def test_replay_fails_rehashed_policy_reason(self, ledger_path: Path) -> None:
        tip, count = self._two_receipt_ledger(ledger_path)
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        receipt = json.loads(lines[1])
        body = {k: v for k, v in receipt.items() if k != "receipt_id"}
        body["policy_reason"] = "policy checks passed"
        receipt = Receipt.with_id(body)
        lines[1] = CanonicalJson.dumps(receipt)
        seal = json.loads(lines[2])
        seal["tip_receipt_id"] = receipt["receipt_id"]
        lines[2] = CanonicalJson.dumps(seal)
        ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        failure = Replay.check(ledger_path, expect_tip=tip, expect_count=count)
        assert failure is not None
        assert failure.ledger_index == 1
        assert failure.reason == "policy_reason mismatch"

    def test_replay_fails_one_byte_changed(self, ledger_path: Path) -> None:
        tip, count = self._two_receipt_ledger(ledger_path)
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        tampered = bytearray(lines[0].encode("utf-8"))
        tampered[10] ^= 0x01
        lines[0] = tampered.decode("utf-8")
        ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        failure = Replay.check(ledger_path, expect_tip=tip, expect_count=count)
        assert failure is not None

    def test_replay_fails_receipt_id_sha256_on_digest_tamper(
        self, ledger_path: Path
    ) -> None:
        tip, count = self._two_receipt_ledger(ledger_path)
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        receipt = json.loads(lines[0])
        digest = receipt["bundle_digest"]
        last = digest[-1]
        receipt["bundle_digest"] = digest[:-1] + ("1" if last == "0" else "0")
        lines[0] = CanonicalJson.dumps(receipt)
        ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        failure = Replay.check(ledger_path, expect_tip=tip, expect_count=count)
        assert failure is not None
        assert failure.ledger_index == 0
        assert failure.reason == "receipt_id SHA-256 mismatch"

    def test_replay_fails_prev_link_after_receipt_id_recompute(
        self, ledger_path: Path
    ) -> None:
        tip, count = self._two_receipt_ledger(ledger_path)
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        receipt0 = json.loads(lines[0])
        receipt1 = json.loads(lines[1])
        original_id = receipt0["receipt_id"]
        body0 = {k: v for k, v in receipt0.items() if k != "receipt_id"}
        body0["audit_note"] = "tampered"
        receipt0 = Receipt.with_id(body0)
        assert receipt0["receipt_id"] != original_id
        assert receipt1["prev_receipt_id"] == original_id
        lines[0] = CanonicalJson.dumps(receipt0)
        ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        failure = Replay.check(ledger_path, expect_tip=tip, expect_count=count)
        assert failure is not None
        assert failure.ledger_index == 1
        assert failure.reason == "prev_receipt_id chain broken"

    def test_replay_fails_artifact_tamper_in_stored_bundle(
        self, ledger_path: Path
    ) -> None:
        tip, count = self._two_receipt_ledger(ledger_path)
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        receipt = json.loads(lines[0])
        body = {k: v for k, v in receipt.items() if k != "receipt_id"}
        bundle = dict(body["evidence_bundle"])
        raw = base64.standard_b64decode(bundle["artifact_b64"])
        tampered = bytearray(raw)
        tampered[0] ^= 0x01
        bundle["artifact_b64"] = base64.standard_b64encode(bytes(tampered)).decode(
            "ascii"
        )
        body["evidence_bundle"] = bundle
        receipt = Receipt.with_id(body)
        lines[0] = CanonicalJson.dumps(receipt)
        ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        failure = Replay.check(ledger_path, expect_tip=tip, expect_count=count)
        assert failure is not None
        assert failure.ledger_index == 0
        assert failure.reason.startswith("evidence re-verify failed:")
        assert "artifact_sha256 does not match" in failure.reason

    def test_replay_fails_line_deleted(self, ledger_path: Path) -> None:
        tip, count = self._two_receipt_ledger(ledger_path)
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        ledger_path.write_text("\n".join(lines[1:]) + "\n", encoding="utf-8")
        failure = Replay.check(ledger_path, expect_tip=tip, expect_count=count)
        assert failure is not None
        assert "seal receipt_count" in failure.reason

    def test_replay_fails_lines_swapped(self, ledger_path: Path) -> None:
        tip, count = self._two_receipt_ledger(ledger_path)
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        lines[0], lines[1] = lines[1], lines[0]
        ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        failure = Replay.check(ledger_path, expect_tip=tip, expect_count=count)
        assert failure is not None


class TestDemoModule:
    def test_demo_exits_zero(self) -> None:
        assert DemoScenarios.run_demo() == 0

    def test_demo_cli(self) -> None:
        root = Path(__file__).resolve().parent.parent
        proc = subprocess.run(
            [sys.executable, "-m", "aevion_runtime.demo"],
            cwd=str(root),
            env={**dict(__import__("os").environ), "PYTHONPATH": "src"},
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0
        assert "SUMMARY:" in proc.stdout
        assert "POLICY: ALLOW" in proc.stdout
        assert "POLICY: DENY" in proc.stdout
        assert "TIP:" in proc.stdout
        assert "RECEIPT_COUNT: 2" in proc.stdout
        assert "--expect-tip" in proc.stdout
        assert "--expect-count 2" in proc.stdout
