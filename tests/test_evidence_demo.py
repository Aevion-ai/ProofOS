"""Oct 29 customer-gate: evidence, policy, receipts, replay."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from aevion_runtime.attestation import Attestation, AttestationRejected
from aevion_runtime.demo import _allow_bundle, _deny_bundle, _forged_cases, run_demo
from aevion_runtime.evidence import EvidenceVerifier
from aevion_runtime.ledger import Ledger
from aevion_runtime.receipt import Receipt
from aevion_runtime.replay import Replay


@pytest.fixture
def ledger_path(tmp_path: Path) -> Path:
    return tmp_path / "ledger.jsonl"


class TestAuthenticEvidence:
    def test_verify_pass(self) -> None:
        bundle = _allow_bundle()
        verdict = EvidenceVerifier.verify(bundle)
        assert verdict.passed
        assert verdict.reason == "PASS"

    def test_attest_allow_writes_receipt(self, ledger_path: Path) -> None:
        receipt = Attestation.run(_allow_bundle(), ledger_path)
        assert receipt["decision"] == "ALLOW"
        assert receipt["evidence_verdict"] == "PASS"
        assert Ledger.line_count(ledger_path) == 1


class TestForgedEvidence:
    def test_forged_rejects_no_ledger_write(self, ledger_path: Path) -> None:
        allow = _allow_bundle()
        Attestation.run(allow, ledger_path)
        before = Ledger.line_count(ledger_path)
        for _label, bundle in _forged_cases(allow):
            with pytest.raises(AttestationRejected):
                Attestation.run(bundle, ledger_path)
            assert Ledger.line_count(ledger_path) == before

    def test_attest_or_exit_nonzero(self, ledger_path: Path) -> None:
        from aevion_runtime.attestation import Attestation

        bad = dict(_allow_bundle())
        bad["artifact_sha256"] = "f" * 64
        with pytest.raises(SystemExit) as exc:
            Attestation.run_or_exit(bad, ledger_path)
        assert exc.value.code == 1
        assert Ledger.line_count(ledger_path) == 0


class TestPolicyGated:
    def test_allow_on_safe_envelope(self, ledger_path: Path) -> None:
        receipt = Attestation.run(_allow_bundle(), ledger_path)
        assert receipt["decision"] == "ALLOW"
        assert receipt["policy_version"] == "aevion-proofos-v1.0"

    def test_deny_on_verified_unsafe_deployable(self, ledger_path: Path) -> None:
        receipt = Attestation.run(_deny_bundle(), ledger_path)
        assert receipt["decision"] == "DENY"
        assert receipt["evidence_verdict"] == "PASS"
        assert "is_safe_deployable" in receipt["policy_reason"]


class TestReceiptChain:
    def test_receipt_id_is_sha256_of_canonical_body(self, ledger_path: Path) -> None:
        receipt = Attestation.run(_allow_bundle(), ledger_path)
        assert Receipt.verify_id(receipt)

    def test_chained_prev_receipt_id(self, ledger_path: Path) -> None:
        first = Attestation.run(_allow_bundle(), ledger_path)
        second = Attestation.run(_deny_bundle(), ledger_path)
        assert second["prev_receipt_id"] == first["receipt_id"]


class TestReplay:
    def _two_receipt_ledger(self, ledger_path: Path) -> None:
        Attestation.run(_allow_bundle(), ledger_path)
        second = Attestation.run(_deny_bundle(), ledger_path)
        Ledger.seal(ledger_path, receipt_count=2, tip_receipt_id=second["receipt_id"])

    def test_replay_matches_clean_ledger(self, ledger_path: Path) -> None:
        self._two_receipt_ledger(ledger_path)
        assert Replay.run(ledger_path) == 0

    def test_replay_fails_one_byte_changed(self, ledger_path: Path) -> None:
        self._two_receipt_ledger(ledger_path)
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        tampered = bytearray(lines[0].encode("utf-8"))
        tampered[10] ^= 0x01
        lines[0] = tampered.decode("utf-8")
        ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        assert Replay.run(ledger_path) == 1

    def test_replay_fails_line_deleted(self, ledger_path: Path) -> None:
        self._two_receipt_ledger(ledger_path)
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        # Drop the first receipt line; seal still claims receipt_count=2.
        ledger_path.write_text("\n".join(lines[1:]) + "\n", encoding="utf-8")
        assert Replay.run(ledger_path) == 1

    def test_replay_fails_lines_swapped(self, ledger_path: Path) -> None:
        self._two_receipt_ledger(ledger_path)
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        lines[0], lines[1] = lines[1], lines[0]
        ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        assert Replay.run(ledger_path) == 1


class TestDemoModule:
    def test_demo_exits_zero(self) -> None:
        assert run_demo() == 0

    def test_demo_cli(self) -> None:
        root = Path(__file__).resolve().parent.parent
        proc = subprocess.run(
            [sys.executable, "-m", "aevion_runtime.demo"],
            cwd=str(root),
            env={**dict(__import__("os").environ), "PYTHONPATH": "."},
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0
        assert "SUMMARY:" in proc.stdout
        assert "POLICY: ALLOW" in proc.stdout
        assert "POLICY: DENY" in proc.stdout
