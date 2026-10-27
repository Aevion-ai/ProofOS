"""Replay ledger — re-verify chain and re-derive decisions."""

from __future__ import annotations

import sys
from pathlib import Path

from aevion_runtime.evidence import EvidenceVerifier
from aevion_runtime.ledger import Ledger
from aevion_runtime.policy import PolicyGate
from aevion_runtime.receipt import Receipt


class Replay:
    """Re-verify receipts from a JSONL ledger file alone."""

    @staticmethod
    def run(ledger_path: Path) -> int:
        """Print MATCH per receipt; exit 1 on first failure with ledger index."""
        try:
            rows = Ledger.read_all(ledger_path)
        except ValueError as exc:
            print(f"REPLAY FAIL at ledger index 0: {exc}")
            return 1

        if not rows:
            print("REPLAY FAIL at ledger index 0: empty ledger")
            return 1

        if rows[-1].get("record_type") == "SEAL":
            seal = rows[-1]
            receipts = rows[:-1]
            seal_index = len(rows) - 1
            expected = seal.get("receipt_count")
            if not isinstance(expected, int):
                print(f"REPLAY FAIL at ledger index {seal_index}: invalid seal")
                return 1
            if len(receipts) != expected:
                print(
                    f"REPLAY FAIL at ledger index {seal_index}: "
                    f"seal receipt_count {expected} != {len(receipts)} receipt lines"
                )
                return 1
            tip = seal.get("tip_receipt_id")
            if not isinstance(tip, str) or not receipts or receipts[-1].get("receipt_id") != tip:
                print(f"REPLAY FAIL at ledger index {seal_index}: tip_receipt_id mismatch")
                return 1
        else:
            receipts = rows

        prev_id = ""
        for index, receipt in enumerate(receipts):
            if not isinstance(receipt, dict):
                print(f"REPLAY FAIL at ledger index {index}: receipt must be a mapping")
                return 1

            if not Receipt.verify_id(receipt):
                print(f"REPLAY FAIL at ledger index {index}: receipt_id mismatch")
                return 1

            if receipt.get("prev_receipt_id", "") != prev_id:
                print(
                    f"REPLAY FAIL at ledger index {index}: "
                    f"prev_receipt_id chain broken"
                )
                return 1

            bundle = receipt.get("evidence_bundle")
            if not isinstance(bundle, dict):
                print(f"REPLAY FAIL at ledger index {index}: missing evidence_bundle")
                return 1

            verdict = EvidenceVerifier.verify(bundle)
            if not verdict.passed:
                print(
                    f"REPLAY FAIL at ledger index {index}: "
                    f"evidence re-verify failed: {verdict.reason}"
                )
                return 1

            if verdict.bundle_digest != receipt.get("bundle_digest"):
                print(f"REPLAY FAIL at ledger index {index}: bundle_digest mismatch")
                return 1

            policy = PolicyGate.evaluate(verdict)
            if policy.decision != receipt.get("decision"):
                print(f"REPLAY FAIL at ledger index {index}: decision mismatch")
                return 1
            if policy.policy_version != receipt.get("policy_version"):
                print(f"REPLAY FAIL at ledger index {index}: policy_version mismatch")
                return 1

            print(f"MATCH receipt_id={receipt['receipt_id']}")
            prev_id = receipt["receipt_id"]

        return 0

    @staticmethod
    def main(argv: list[str] | None = None) -> int:
        args = argv if argv is not None else sys.argv[1:]
        if len(args) != 1:
            print("usage: replay <ledger.jsonl>", file=sys.stderr)
            return 2
        return Replay.run(Path(args[0]))
