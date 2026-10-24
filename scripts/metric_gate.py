#!/usr/bin/env python3
"""
Structural metric-reconciliation gate for ProofOS public surfaces.

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

DENYLIST = [
    r"Wukong Bell", r"QGOV Predict",
    r"NIST published (?:the|a) proof",
    r"96\.02",
    r"lean%20build-EXIT%200",
    r"proof%20density-9",
    r"open%20obligations-(?:[1-9]\d\d|[3-9]\d)",
    r"paper-arXiv%20ready",
]


def classify_lean_file(path: str, default_roots: list[str]) -> str:
    """Separate research scaffolding from default-target and other Lean code."""
    path = pathlib.PurePosixPath(path).as_posix()
    if path == "Aevion/SBIR.lean" or path.startswith("Aevion/SBIR/"):
        return "research_scaffolding"
    if any(path == f"{root}.lean" or path.startswith(f"{root}/")
           for root in default_roots):
        return "default_target"
    return "non_default_source"


def lean_inventory(root: pathlib.Path | None = None) -> dict:
    """Recursively recompute theorem/sorry counts and classify every source."""
    repo_root = ROOT if root is None else root
    lean_dir = repo_root / "lean"
    lakefile = (repo_root / "lakefile.toml").read_text(encoding="utf-8")
    roots_match = re.search(r"(?m)^roots\s*=\s*\[([^]]*)\]", lakefile)
    default_roots = re.findall(r'"([^"]+)"', roots_match.group(1)) if roots_match else []
    files = sorted(lean_dir.rglob("*.lean"))
    theorems = sorries = 0
    entries = []
    for f in files:
        t = f.read_text(encoding="utf-8")
        t = re.sub(r"/-.*?-/", "", t, flags=re.S)
        t = re.sub(r"--.*", "", t)
        file_theorems = len(re.findall(r"^\s*theorem\s+\w+", t, flags=re.M))
        file_sorries = len(re.findall(r"\bsorry\b", t))
        theorems += file_theorems
        sorries += file_sorries
        rel = f.relative_to(lean_dir).as_posix()
        entries.append({
            "path": rel,
            "classification": classify_lean_file(rel, default_roots),
            "theorems": file_theorems,
            "sorries": file_sorries,
        })
    return {
        "files": len(files),
        "theorems": theorems,
        "sorries": sorries,
        "default_roots": default_roots,
        "entries": entries,
        "research_scaffolding_files": sum(
            e["classification"] == "research_scaffolding" for e in entries
        ),
    }


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
          f"{inv['theorems']} theorem decls, {inv['sorries']} sorry; "
          f"research scaffolding: {inv['research_scaffolding_files']} files")
    deny = re.compile("|".join(DENYLIST))
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
