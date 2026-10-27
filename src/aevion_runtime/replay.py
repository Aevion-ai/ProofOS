"""Replay ledger — re-verify chain and re-derive decisions."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aevion_runtime.evidence import EvidenceVerifier
from aevion_runtime.ledger import Ledger
from aevion_runtime.policy import PolicyGate
from aevion_runtime.receipt import Receipt


@dataclass(frozen=True)
class ReplayFailure:
    """First replay failure on a ledger line."""

    ledger_index: int
    reason: str

    def format_line(self) -> str:
        return f"REPLAY FAIL at ledger index {self.ledger_index}: {self.reason}"


class Replay:
    """Re-verify receipts from a JSONL ledger file alone."""

    @staticmethod
    def _parse_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], ReplayFailure | None]:
        if not rows:
            return [], ReplayFailure(0, "empty ledger")

        if rows[-1].get("record_type") == "SEAL":
            seal = rows[-1]
            receipts = rows[:-1]
            seal_index = len(rows) - 1
            expected = seal.get("receipt_count")
            if not isinstance(expected, int):
                return [], ReplayFailure(seal_index, "invalid seal")
            if len(receipts) != expected:
                return [], ReplayFailure(
                    seal_index,
                    f"seal receipt_count {expected} != {len(receipts)} receipt lines",
                )
            tip = seal.get("tip_receipt_id")
            if not isinstance(tip, str) or not receipts or receipts[-1].get("receipt_id") != tip:
                return [], ReplayFailure(seal_index, "tip_receipt_id mismatch")
            return receipts, None

        return rows, None

    @staticmethod
    def _check_receipt(
        receipt: Any, index: int, prev_id: str
    ) -> ReplayFailure | None:
        if not isinstance(receipt, dict):
            return ReplayFailure(index, "receipt must be a mapping")

        if not Receipt.verify_id(receipt):
            return ReplayFailure(index, "receipt_id SHA-256 mismatch")

        if receipt.get("prev_receipt_id", "") != prev_id:
            return ReplayFailure(index, "prev_receipt_id chain broken")

        bundle = receipt.get("evidence_bundle")
        if not isinstance(bundle, dict):
            return ReplayFailure(index, "missing evidence_bundle")

        verdict = EvidenceVerifier.verify(bundle)
        if not verdict.passed:
            return ReplayFailure(
                index, f"evidence re-verify failed: {verdict.reason}"
            )

        if verdict.bundle_digest != receipt.get("bundle_digest"):
            return ReplayFailure(index, "bundle_digest mismatch")

        policy = PolicyGate.evaluate(verdict)
        if policy.decision != receipt.get("decision"):
            return ReplayFailure(index, "decision mismatch")
        if policy.policy_version != receipt.get("policy_version"):
            return ReplayFailure(index, "policy_version mismatch")

        return None

    @staticmethod
    def check(ledger_path: Path) -> ReplayFailure | None:
        """Return the first failure, or None when the ledger replays cleanly."""
        try:
            rows = Ledger.read_all(ledger_path)
        except ValueError as exc:
            return ReplayFailure(0, str(exc))

        receipts, parse_failure = Replay._parse_rows(rows)
        if parse_failure is not None:
            return parse_failure

        prev_id = ""
        for index, receipt in enumerate(receipts):
            failure = Replay._check_receipt(receipt, index, prev_id)
            if failure is not None:
                return failure
            prev_id = receipt["receipt_id"]

        return None

    @staticmethod
    def run(ledger_path: Path) -> int:
        """Print MATCH per receipt; exit 1 on first failure with ledger index."""
        try:
            rows = Ledger.read_all(ledger_path)
        except ValueError as exc:
            print(f"REPLAY FAIL at ledger index 0: {exc}")
            return 1

        receipts, parse_failure = Replay._parse_rows(rows)
        if parse_failure is not None:
            print(parse_failure.format_line())
            return 1

        prev_id = ""
        for index, receipt in enumerate(receipts):
            failure = Replay._check_receipt(receipt, index, prev_id)
            if failure is not None:
                print(failure.format_line())
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
