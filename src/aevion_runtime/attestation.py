"""Attest verified evidence — receipt on success, exit 1 without ledger write on failure."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from aevion_runtime.evidence import EvidenceVerifier
from aevion_runtime.ledger import Ledger
from aevion_runtime.policy import PolicyGate
from aevion_runtime.receipt import Receipt


class AttestationRejected(Exception):
    """Evidence failed verification; no receipt was written."""

    def __init__(self, reason: str, exit_code: int = 1) -> None:
        super().__init__(reason)
        self.reason = reason
        self.exit_code = exit_code


class Attestation:
    """Verify evidence, apply policy, append receipt. Fail-closed on bad evidence."""

    @staticmethod
    def run(bundle: dict[str, Any], ledger_path: Path) -> dict[str, Any]:
        verdict = EvidenceVerifier.verify(bundle)
        if not verdict.passed:
            raise AttestationRejected(verdict.reason)

        policy = PolicyGate.evaluate(verdict)
        prev = ""
        if ledger_path.is_file():
            rows = Ledger.read_all(ledger_path)
            if rows:
                prev = str(rows[-1].get("receipt_id", ""))

        body = Receipt.build_body(
            prev_receipt_id=prev,
            evidence_bundle=bundle,
            bundle_digest=verdict.bundle_digest or "",
            evidence_verdict="PASS",
            decision=policy.decision,
            policy_version=policy.policy_version,
            policy_reason=policy.reason,
        )
        receipt = Receipt.with_id(body)
        Ledger.append(ledger_path, receipt)
        return receipt

    @staticmethod
    def run_or_exit(bundle: dict[str, Any], ledger_path: Path) -> dict[str, Any]:
        try:
            return Attestation.run(bundle, ledger_path)
        except AttestationRejected as exc:
            print(f"REJECT: {exc.reason}", file=sys.stderr)
            sys.exit(exc.exit_code)
