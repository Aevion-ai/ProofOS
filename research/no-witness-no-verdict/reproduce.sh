#!/usr/bin/env bash
# No Witness, No Verdict — reproduction script.
# Proves the artifact reproduces from source in a clean environment.
#
# Usage: bash reproduce.sh
# Requires: python3 >= 3.10, pytest, and (for Lean) lake/elan.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "== No Witness, No Verdict — reproduction =="
echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "python: $(python3 --version 2>&1 || py -3 --version 2>&1)"

# 1. Python evaluation battery
echo ""
echo "== 1. Python evaluation battery =="
python3 -m pytest tests/ -q 2>&1 || py -3 -B -m pytest tests/ -q

# 2. Lean formal statements (dependency-free: no Mathlib import)
echo ""
echo "== 2. Lean formal statements =="
if command -v lean >/dev/null 2>&1 || [ -x "$HOME/.elan/bin/lean" ]; then
  LEAN_BIN="$(command -v lean || echo "$HOME/.elan/bin/lean")"
  echo "lean found: $($LEAN_BIN --version 2>&1 | head -1)"
  for f in lean/NoWitnessNoVerdict/RejectAbsorption.lean \
           lean/NoWitnessNoVerdict/CandidateOnly.lean \
           lean/NoWitnessNoVerdict/ReceiptBoundReplay.lean; do
    out="$("$LEAN_BIN" "$f" 2>&1)"
    if [ -z "$out" ]; then
      echo "  $f: CLEAN"
    else
      echo "  $f: $out" | head -2
      exit 1
    fi
  done
else
  echo "lean not found — Lean verification skipped (see README for elan install)"
fi

# 3. Artifact digest
echo ""
echo "== 3. Artifact digest =="
find . -type f \( -name "*.py" -o -name "*.lean" -o -name "*.toml" -o -name "*.tex" -o -name "*.bib" \) \
  -not -path "./.pytest_cache/*" -not -path "*/__pycache__/*" | sort | while read -r f; do
  sha256sum "$f" | awk -v f="$f" '{print $1 "  " f}'
done

echo ""
echo "== Reproduction complete =="
