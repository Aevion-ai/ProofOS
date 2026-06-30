# Contributing to Aevion-Verifiable-AI

Thank you for your interest in contributing.

## Getting Started

1. Fork the repository and create a feature branch from `main`.
2. Install dependencies:
   - **Python 3.11+** with `pytest` (`pip install pytest`)
   - **Lean 4** via [elan](https://github.com/leanprover/elan) (version pinned in `lean-proofs/lean-toolchain`)
   - **ripgrep** (`rg`) for proof hygiene scans
3. Make your changes.
4. Run tests before submitting:
   ```bash
   python3 -B -m pytest integrations/ tests/ -v
   cd lean-proofs && lake build
   ```
5. Open a pull request against `main`.

## Code Standards

- **Lean proofs:** No `sorry`, `admit`, or new project-defined `axiom` declarations. Prove only narrow decidable gates.
- **Python:** Follow existing code style. All new modules should have corresponding tests.
- **Claim hygiene:** Do not claim certification, guaranteed safety, or regulatory approval. Use maturity labels: `LOCAL_PROTOTYPE`, `CI_READY`, `ENTERPRISE_PILOT_READY`, `PRODUCTION_REQUIRES_REVIEW`.

## Review Process

All pull requests require review before merging. The CI pipeline runs:
- Python tests (pytest)
- Lean proof builds (lake)
- Security guard scan
- Schema validation

## Reporting Issues

Use GitHub Issues for bug reports and feature requests. For security issues, see [SECURITY.md](SECURITY.md).
