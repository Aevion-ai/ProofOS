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

MISSING_ANCHORS_REASON = (
    "replay requires --expect-tip and --expect-count; tail truncation cannot be "
    "checked without anchors recorded at attest time"
)


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
    def _parse_rows(
        rows: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], int, ReplayFailure | None]:
        """Return (receipt rows, seal line index, parse failure)."""
        if not rows:
            return [], 0, ReplayFailure(0, "empty ledger")

        if rows[-1].get("record_type") != "SEAL":
            return [], len(rows) - 1, ReplayFailure(
                len(rows) - 1, "missing SEAL terminal record"
            )

        seal = rows[-1]
        receipts = rows[:-1]
        seal_index = len(rows) - 1
        expected = seal.get("receipt_count")
        if not isinstance(expected, int):
            return [], seal_index, ReplayFailure(seal_index, "invalid seal")
        if len(receipts) != expected:
            return [], seal_index, ReplayFailure(
                seal_index,
                f"seal receipt_count {expected} != {len(receipts)} receipt lines",
            )
        tip = seal.get("tip_receipt_id")
        if not isinstance(tip, str) or not receipts or receipts[-1].get("receipt_id") != tip:
            return [], seal_index, ReplayFailure(seal_index, "tip_receipt_id mismatch")
        return receipts, seal_index, None

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
        if policy.reason != receipt.get("policy_reason"):
            return ReplayFailure(index, "policy_reason mismatch")

        return None

    @staticmethod
    def _evaluate(
        ledger_path: Path,
        expect_tip: str | None = None,
        expect_count: int | None = None,
    ) -> ReplayFailure | None:
        if expect_tip is None or expect_count is None:
            return ReplayFailure(0, MISSING_ANCHORS_REASON)

        try:
            rows = Ledger.read_all(ledger_path)
        except ValueError as exc:
            return ReplayFailure(0, str(exc))

        receipts, seal_index, parse_failure = Replay._parse_rows(rows)
        if parse_failure is not None:
            return parse_failure

        prev_id = ""
        for index, receipt in enumerate(receipts):
            failure = Replay._check_receipt(receipt, index, prev_id)
            if failure is not None:
                return failure
            prev_id = receipt["receipt_id"]

        actual_count = len(receipts)
        if actual_count != expect_count:
            return ReplayFailure(
                seal_index,
                f"expect-count mismatch: expected {expect_count} got {actual_count}",
            )

        actual_tip = receipts[-1]["receipt_id"] if receipts else ""
        if actual_tip != expect_tip:
            return ReplayFailure(
                seal_index,
                f"expect-tip mismatch: expected {expect_tip} got {actual_tip}",
            )

        return None

    @staticmethod
    def check(
        ledger_path: Path,
        expect_tip: str | None = None,
        expect_count: int | None = None,
    ) -> ReplayFailure | None:
        """Return the first failure, or None when the ledger replays cleanly."""
        return Replay._evaluate(ledger_path, expect_tip, expect_count)

    @staticmethod
    def run(
        ledger_path: Path,
        expect_tip: str | None = None,
        expect_count: int | None = None,
    ) -> int:
        """Print MATCH per receipt; exit 1 on first failure with ledger index."""
        failure = Replay._evaluate(ledger_path, expect_tip, expect_count)
        if failure is not None:
            print(failure.format_line())
            return 1

        rows = Ledger.read_all(ledger_path)
        receipts, _, _ = Replay._parse_rows(rows)
        for receipt in receipts:
            print(f"MATCH receipt_id={receipt['receipt_id']}")
        return 0

    @staticmethod
    def main(argv: list[str] | None = None) -> int:
        args = argv if argv is not None else sys.argv[1:]
        if not args or args[0] in ("-h", "--help"):
            print(
                "usage: replay <ledger.jsonl> --expect-tip <id> --expect-count <n>",
                file=sys.stderr,
            )
            return 2
        ledger_arg = args[0]
        expect_tip: str | None = None
        expect_count: int | None = None
        rest = args[1:]
        index = 0
        while index < len(rest):
            if rest[index] == "--expect-tip":
                if index + 1 >= len(rest):
                    print("--expect-tip requires a receipt_id", file=sys.stderr)
                    return 2
                expect_tip = rest[index + 1]
                index += 2
                continue
            if rest[index] == "--expect-count":
                if index + 1 >= len(rest):
                    print("--expect-count requires an integer", file=sys.stderr)
                    return 2
                expect_count = int(rest[index + 1])
                index += 2
                continue
            print(f"unknown argument: {rest[index]}", file=sys.stderr)
            return 2
        return Replay.run(Path(ledger_arg), expect_tip, expect_count)
