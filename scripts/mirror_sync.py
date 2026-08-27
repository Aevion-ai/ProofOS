#!/usr/bin/env python3
"""
Sync allow-listed paths from the monorepo checkout into ProofOS.

Uses mirror_admission for fail-closed path evaluation and receipt emission
before any copy. Invoked by .github/workflows/mirror-from-monorepo.yml.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from src.aevion_runtime.mirror_admission import evaluate_mapping, parse_path_map_lines


def _update_manifest_metadata(
    manifest: Path,
    source_sha: str,
    last_sync: str,
) -> None:
    text = manifest.read_text(encoding="utf-8")
    text = re.sub(
        r"^(\| `source_commit` \| `)[^`]*(` \|)$",
        rf"\g<1>{source_sha}\g<2>",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^(\| `last_sync` \| `)[^`]*(` \|)$",
        rf"\g<1>{last_sync}\g<2>",
        text,
        flags=re.MULTILINE,
    )
    manifest.write_text(text, encoding="utf-8")


def main() -> int:
    repo_root = Path.cwd()
    monorepo_base = repo_root / ".monorepo"
    manifest = repo_root / "MIRROR_MANIFEST.md"

    if not monorepo_base.is_dir():
        print("DENY: monorepo checkout missing at .monorepo")
        return 1

    source_sha = subprocess.check_output(
        ["git", "-C", str(monorepo_base), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    last_sync = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"source_sha={source_sha}\n")
            handle.write(f"last_sync={last_sync}\n")

    text = manifest.read_text(encoding="utf-8")
    mappings = parse_path_map_lines(text)
    if not mappings:
        print("DENY: no path mappings found in MIRROR_MANIFEST.md")
        return 1

    for src, dst in mappings:
        decision = evaluate_mapping(src, dst, monorepo_base, repo_root)
        print(
            f"RECEIPT {decision.receipt_hash}: "
            f"{decision.decision} {src} -> {dst} ({decision.reason})"
        )
        if not decision.admitted:
            print(f"DENY: {decision.reason} for {src} -> {dst}")
            return 1

        src_path = Path(decision.resolved_src)
        if not src_path.exists():
            print(f"SKIP: source not found: {src}")
            continue

        dst_path = Path(decision.resolved_dst)
        print(f"COPY: {src} -> {dst}")
        if dst_path.exists():
            if dst_path.is_dir():
                shutil.rmtree(dst_path)
            else:
                dst_path.unlink()
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        if src_path.is_dir():
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)

    _update_manifest_metadata(manifest, source_sha, last_sync)
    return 0


if __name__ == "__main__":
    sys.exit(main())
