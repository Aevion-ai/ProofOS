# Contributing to ProofOS

## Proof standards

- **No `sorry` in active safety corpus.** New theorems must be kernel-clean. Stubs belong in `research_scaffold/` with explicit documentation.
- **Mathlib-first.** Prefer Mathlib imports over custom definitions. Pin versions in `lean-toolchain`.
- **Canonical serialization.** All receipts use `canonical_sha256` from `core/python/proofdb/canonical.py`. No local reimplementations.

## Issue workflow

| Label | Meaning | Response |
|-------|---------|----------|
| `proof-debt:P0:critical` | Safety/governance invariant with no formal proof | Requires linked PR within 7 days |
| `colony:eval` | Agent Counsel Colony evaluation or calibration | Standard triage |
| `documentation` | Docs, README, architecture, paper | Standard triage |
| `good-first-issue` | Scoped, self-contained, no deep domain knowledge needed | Encouraged for new contributors |

## PR checklist

- [ ] `lake build` passes locally
- [ ] `pytest tests/ -q` passes locally
- [ ] Receipts emitted for substantive changes
- [ ] No new `sorry`/`admit`/`axiom` in active safety corpus without explicit `STATEMENT_CHANGED` review
- [ ] Architectural changes update `architecture.md` and Quorum Constitution if applicable

## Architecture

Before contributing, read:
- [architecture.md](architecture.md) — system diagram and layer mapping
- [quorum.md](quorum.md) — Agent Counsel Colony aggregation rules
- [paper.md](paper.md) — full technical paper

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
