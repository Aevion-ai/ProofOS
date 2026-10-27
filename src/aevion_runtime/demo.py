"""Oct 29 customer-gate demo — evidence, policy, receipts, replay."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from aevion_runtime.attestation import Attestation, AttestationRejected
from aevion_runtime.evidence import EvidenceVerifier
from aevion_runtime.ledger import Ledger
from aevion_runtime.model_access_envelope import ModelAccessEnvelope
from aevion_runtime.replay import Replay


def _artifact() -> bytes:
    return b"proofos-oct29-evidence-artifact-v1"


def _allow_bundle() -> dict:
    env = ModelAccessEnvelope.aevion_proof_os("demo-model").to_dict()
    return EvidenceVerifier.build_bundle(env, _artifact(), "BUSINESS", 10, 3)


def _deny_bundle() -> dict:
    env = ModelAccessEnvelope.mythos_5().to_dict()
    return EvidenceVerifier.build_bundle(env, _artifact(), "BUSINESS", 10, 3)


def _forged_cases(allow_bundle: dict) -> list[tuple[str, dict]]:
    cases: list[tuple[str, dict]] = []

    bad_byte = dict(allow_bundle)
    bad_byte["artifact_b64"] = bad_byte["artifact_b64"][:-1] + "A"
    cases.append(("artifact byte tampered", bad_byte))

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


def run_demo(ledger_path: Path | None = None) -> int:
    out_dir = tempfile.mkdtemp(prefix="proofos-demo-")
    ledger = ledger_path or Path(out_dir) / "ledger.jsonl"

    print("=== STEP 1: AUTHENTIC EVIDENCE (expect PASS + policy ALLOW + receipt) ===")
    allow = _allow_bundle()
    verdict = EvidenceVerifier.verify(allow)
    print(f"EVIDENCE: {verdict.reason}")
    receipt_allow = Attestation.run(allow, ledger)
    print(f"POLICY: {receipt_allow['decision']} policy_version={receipt_allow['policy_version']}")
    print(f"RECEIPT: {receipt_allow['receipt_id']}")

    print("=== STEP 2: VERIFIED EVIDENCE POLICY DENY (expect PASS + DENY + receipt) ===")
    deny = _deny_bundle()
    verdict_deny = EvidenceVerifier.verify(deny)
    print(f"EVIDENCE: {verdict_deny.reason}")
    receipt_deny = Attestation.run(deny, ledger)
    print(f"POLICY: {receipt_deny['decision']} policy_version={receipt_deny['policy_version']}")
    print(f"RECEIPT: {receipt_deny['receipt_id']}")

    Ledger.seal(ledger, receipt_count=2, tip_receipt_id=receipt_deny["receipt_id"])
    print(f"LEDGER_SEAL: receipt_count=2 tip={receipt_deny['receipt_id']}")

    print("=== STEP 3: FORGED EVIDENCE (expect REJECT exit=1, ledger unchanged) ===")
    before = Ledger.line_count(ledger)
    for label, bundle in _forged_cases(allow):
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
    return run_demo()


if __name__ == "__main__":
    sys.exit(main())
