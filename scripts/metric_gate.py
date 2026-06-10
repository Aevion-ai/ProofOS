#!/usr/bin/env python3
"""Structural metric-reconciliation gate for ProofOS public surfaces.

Why structural: a denylist of specific fossil numbers is too weak — the count
has already mutated (1,252 -> 1,283; 343 -> 350 files) across sessions. This
gate recomputes the REAL Lean inventory from `lean/` and fails (exit 1) on any
public claim that exceeds it, plus a denylist for RED-gated framing and
INTERNAL_ONLY codenames. Future mutations of the number are caught regardless
of the specific value.

Run:  python scripts/metric_gate.py
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

PUBLIC_SURFACES = [
    "README.md", "PROOFOS.md", "architecture.md", "quorum.md",
    "docs/index.html", "docs/assets",
]

# RED-gated framing / INTERNAL_ONLY codenames / unverified-badge tokens.
DENYLIST = [
    r"Wukong Bell", r"QGOV Predict",
    r"NIST published (?:the|a) proof",
    r"96\.02",                       # specific density figure, unsourced
    r"lean%20build-EXIT%200",        # badge: unverified "lean build EXIT 0"
    r"proof%20density-9",            # badge: density % (we publish none)
    r"open%20obligations-(?:[1-9]\d\d|[3-9]\d)",  # badge: >=30 open obligations
    r"paper-arXiv%20ready",          # badge: paper is not arXiv-submitted
]


def lean_inventory() -> dict:
    """Recompute theorem/sorry counts from the Lean sources in lean/."""
    lean_dir = ROOT / "lean"
    files = sorted(lean_dir.glob("*.lean"))
    theorems = sorries = 0
    for f in files:
        t = f.read_text(encoding="utf-8")
        t = re.sub(r"/-.*?-/", "", t, flags=re.S)
        t = re.sub(r"--.*", "", t)
        theorems += len(re.findall(r"^\s*theorem\s+\w+", t, flags=re.M))
        sorries += len(re.findall(r"\bsorry\b", t))
    return {"files": len(files), "theorems": theorems, "sorries": sorries}


def num(s: str) -> int:
    """Parse a claim number that may carry thousands separators."""
    return int(s.replace(",", "").replace("%20", "").strip())


def iter_surface_files():
    """Yield every file under the configured public surfaces."""
    for entry in PUBLIC_SURFACES:
        p = ROOT / entry
        candidates = p.rglob("*") if p.is_dir() else [p]
        for f in candidates:
            if f.is_file():
                yield f


def scan_text(rel, text, claims, deny, density):
    """Return violations found in one file's text."""
    found = []
    for m in deny.finditer(text):
        found.append(f"{rel}: forbidden token '{m.group(0)[:40]}'")
    for rx, kind, ceiling in claims:
        for m in rx.finditer(text):
            try:
                claimed = num(m.group(1))
            except ValueError:
                continue
            if claimed > ceiling:
                found.append(
                    f"{rel}: claims {claimed} {kind} > actual {ceiling} "
                    f"('{m.group(0)[:40]}')")
    if density.search(text):
        found.append(f"{rel}: publishes a proof-density % (this repo publishes none)")
    return found


def main() -> int:
    """Scan public surfaces; exit 1 on any claim exceeding the inventory."""
    inv = lean_inventory()
    print(f"[metric_gate] lean inventory: {inv['files']} files, "
          f"{inv['theorems']} theorem decls, {inv['sorries']} sorry")
    deny = re.compile("|".join(DENYLIST))
    # structural claim patterns: (regex, kind, ceiling)
    claims = [
        (re.compile(r"([\d,]+)\s*(?:Lean\s*4?\s*)?theorems?", re.I), "theorems", inv["theorems"]),
        (re.compile(r"(?:across|in)\s*([\d,]+)\s*(?:Lean\s*)?files", re.I), "files", inv["files"]),
        (re.compile(r"([\d,]+)\s*open obligations", re.I), "open obligations", inv["sorries"] + 1),
    ]
    density = re.compile(r"\d+(?:\.\d+)?%\s*(?:proof\s*)?density", re.I)

    v: list[str] = []
    for f in iter_surface_files():
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        v.extend(scan_text(f.relative_to(ROOT), text, claims, deny, density))

    if inv["files"] == 0:
        v.append("lean/: no .lean files (inventory sanity floor)")

    if v:
        print("[metric_gate] FAIL — public surfaces disagree with the repo:")
        for x in v:
            print(f"  - {x}")
        return 1
    print("[metric_gate] PASS — public claims are within the in-repo inventory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
