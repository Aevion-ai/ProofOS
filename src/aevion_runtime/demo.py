"""Oct 29 customer-gate demo — evidence, policy, receipts, replay."""

from __future__ import annotations

import argparse
import base64
import sys
import tempfile
from pathlib import Path
from typing import Any

from aevion_runtime.attestation import Attestation, AttestationRejected
from aevion_runtime.evidence import EvidenceVerifier
from aevion_runtime.ledger import Ledger
from aevion_runtime.model_access_envelope import (
    AccessTier,
    CapabilityClass,
    ModelAccessEnvelope,
    SafeguardMode,
)
from aevion_runtime.replay import Replay


class DemoScenarios:
    """Customer-gate demo fixtures and scripted run (deterministic, no LLM)."""

    @staticmethod
    def artifact() -> bytes:
        return b"proofos-oct29-evidence-artifact-v1"

    @staticmethod
    def allow_bundle() -> dict[str, Any]:
        env = ModelAccessEnvelope.aevion_proof_os("demo-model").to_dict()
        return EvidenceVerifier.build_bundle(
            env, DemoScenarios.artifact(), "BUSINESS", 10, 3
        )

    @staticmethod
    def deny_bundle() -> dict[str, Any]:
        """Verified envelope under Aevion policy that fails is_safe_deployable()."""
        env = ModelAccessEnvelope(
            model_id="demo-model-policy-deny",
            capability_class=CapabilityClass.MYTHOS_CLASS,
            access_tier=AccessTier.BUSINESS,
            safeguard_mode=SafeguardMode.FULL,
            fallback_model="safe-degraded-mode",
            retention_policy_days=90,
            receipt_required=False,
            human_gate_required=True,
            policy_version="aevion-proofos-v1.0",
        ).to_dict()
        return EvidenceVerifier.build_bundle(
            env, DemoScenarios.artifact(), "BUSINESS", 10, 3
        )

    @staticmethod
    def forged_cases(allow_bundle: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
        cases: list[tuple[str, dict[str, Any]]] = []

        raw = base64.standard_b64decode(allow_bundle["artifact_b64"])
        tampered = bytearray(raw)
        tampered[0] ^= 0x01
        bad_byte = dict(allow_bundle)
        bad_byte["artifact_b64"] = base64.standard_b64encode(bytes(tampered)).decode("ascii")
        cases.append(("artifact byte tampered", bad_byte))

        bad_padding = dict(allow_bundle)
        bad_padding["artifact_b64"] = bad_padding["artifact_b64"][:-1] + "A"
        cases.append(("malformed artifact_b64 padding", bad_padding))

        bad_hash = dict(allow_bundle)
        bad_hash["artifact_sha256"] = "0" * 64
        cases.append(("wrong artifact_sha256", bad_hash))

        missing = {k: v for k, v in allow_bundle.items() if k != "consensus_f"}
        cases.append(("missing consensus_f", missing))

        confused = dict(allow_bundle)
        confused["envelope"] = dict(confused["envelope"])
        confused["envelope"]["access_tier"] = "NOT_A_TIER"
        cases.append(("type-confused access_tier", confused))

        return cases

    @staticmethod
    def run_demo(ledger_path: Path | None = None) -> int:
        out_dir = tempfile.mkdtemp(prefix="proofos-demo-")
        ledger = ledger_path or Path(out_dir) / "ledger.jsonl"

        print("=== STEP 1: AUTHENTIC EVIDENCE (expect PASS + policy ALLOW + receipt) ===")
        allow = DemoScenarios.allow_bundle()
        verdict = EvidenceVerifier.verify(allow)
        print(f"EVIDENCE: {verdict.reason}")
        receipt_allow = Attestation.run(allow, ledger)
        print(f"POLICY: {receipt_allow['decision']} policy_version={receipt_allow['policy_version']}")
        print(f"RECEIPT: {receipt_allow['receipt_id']}")

        print("=== STEP 2: VERIFIED EVIDENCE POLICY DENY (expect PASS + DENY + receipt) ===")
        deny = DemoScenarios.deny_bundle()
        verdict_deny = EvidenceVerifier.verify(deny)
        print(f"EVIDENCE: {verdict_deny.reason}")
        receipt_deny = Attestation.run(deny, ledger)
        print(f"POLICY: {receipt_deny['decision']} policy_version={receipt_deny['policy_version']}")
        print(f"RECEIPT: {receipt_deny['receipt_id']}")

        Ledger.seal(ledger, receipt_count=2, tip_receipt_id=receipt_deny["receipt_id"])
        print(f"LEDGER_SEAL: receipt_count=2 tip={receipt_deny['receipt_id']}")

        print("=== STEP 3: FORGED EVIDENCE (expect REJECT exit=1, ledger unchanged) ===")
        before = Ledger.line_count(ledger)
        for label, bundle in DemoScenarios.forged_cases(allow):
            try:
                Attestation.run(bundle, ledger)
                print(f"FORGED [{label}]: UNEXPECTED PASS", file=sys.stderr)
                return 1
            except AttestationRejected as exc:
                after = Ledger.line_count(ledger)
                if after != before:
                    print(f"FORGED [{label}]: ledger mutated", file=sys.stderr)
                    return 1
                print(f"FORGED [{label}]: REJECT exit=1 reason={exc.reason}")
        print(f"LEDGER_LINES: {before} (receipts + seal, unchanged after forged attempts)")

        print("=== STEP 4: REPLAY (expect MATCH for each receipt) ===")
        code = Replay.run(ledger)
        if code != 0:
            return code

        print(
            "SUMMARY: authentic ALLOW + verified DENY receipted; "
            "forged rejected fail-closed; replay MATCH on ledger"
        )
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ProofOS Oct 29 evidence demo")
    parser.add_argument("--replay", metavar="LEDGER", help="Replay a JSONL ledger and exit")
    args = parser.parse_args()
    if args.replay:
        return Replay.run(Path(args.replay))
    return DemoScenarios.run_demo()


if __name__ == "__main__":
    sys.exit(main())
