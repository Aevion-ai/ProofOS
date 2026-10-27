"""Append-only JSONL decision ledger."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aevion_runtime.canonical import CanonicalJson


class Ledger:
    """JSONL ledger; each line is one canonical receipt object."""

    @staticmethod
    def seal(path: Path, receipt_count: int, tip_receipt_id: str) -> None:
        """Terminal seal — replay fails if receipt lines were deleted after sealing."""
        Ledger.append(
            path,
            {
                "record_type": "SEAL",
                "receipt_count": receipt_count,
                "tip_receipt_id": tip_receipt_id,
            },
        )

    @staticmethod
    def append(path: Path, receipt: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(CanonicalJson.dumps(receipt) + "\n")

    @staticmethod
    def line_count(path: Path) -> int:
        if not path.is_file():
            return 0
        return sum(1 for _ in path.open(encoding="utf-8"))

    @staticmethod
    def read_all(path: Path) -> list[dict[str, Any]]:
        if not path.is_file():
            return []
        rows: list[dict[str, Any]] = []
        with path.open(encoding="utf-8") as handle:
            for index, line in enumerate(handle):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    rows.append(json.loads(stripped))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"ledger line {index} is not valid JSON: {exc}") from exc
        return rows
