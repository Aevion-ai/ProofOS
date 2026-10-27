# ProofOS

[![Version](https://img.shields.io/badge/version-v1.0.0-teal)](https://github.com/Aevion-ai/ProofOS/releases/tag/v1.0.0)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Lean 4](https://img.shields.io/badge/Lean-4.16.0-7B2D8B)](lean/)
[![CI](https://github.com/Aevion-ai/ProofOS/actions/workflows/ci.yml/badge.svg)](https://github.com/Aevion-ai/ProofOS/actions)

**Receipt chain for AI agent decisions.** Each decision submitted to the gate generates a SHA-256-chained, machine-checkable receipt; Lean 4 proofs are in progress.

---

## Public mirror

ProofOS is a **governed public repository**. Only the allow-listed paths in [MIRROR_MANIFEST.md](MIRROR_MANIFEST.md) are published here; secrets, credentials, and internal-only evidence are never included. See the manifest for the current sync status and path map.

## What it does

ProofOS scores a submitted evidence envelope in a constitutional halt gate (runtime policy gate) and returns ALLOW or DENY with a SHA-256 receipt that carries the reason. Forged or invalid evidence is rejected with exit code 1 and nothing is written to the ledger. The runtime does not intercept, hold, or pause tool calls; intercepting or holding tool calls is planned. Every receipt is SHA-256 content-addressed and can be checked by replaying the chain against the tip and count anchored at run time; this does not detect a full rewrite of the ledger and seal. Lean 4 proofs for the gate predicates are in progress.

This repository implements fail-closed ALLOW/DENY gating and SHA-256 receipt chains in the runtime policy gate. The Agent Counsel Colony is specified in [quorum.md](quorum.md), not deployed here. Human hold, release, approval, and escalation—including escalation-rate targets (planned) described in [architecture.md](architecture.md)—are planned and not implemented in this repository.

```
Agent Action → Fail-closed Halt Gate (ALLOW/DENY) → Receipt (SHA-256) → Ledger
```

Counsel Colony (7 roles, [quorum.md](quorum.md)) is specified, not deployed.

---

## Quick start

```bash
git clone https://github.com/Aevion-ai/ProofOS
cd ProofOS
pip install -r requirements.txt
pytest tests/ -q
```

Expected output:
```
96 passed in ~0.5s
```

Oct 29 evidence demo (authentic → forged → replay):

```bash
pip install -r requirements.txt && PYTHONPATH=src python3 -m aevion_runtime.demo
```

Replay checks the ledger against the tip receipt id and receipt count recorded at run time, so it detects edits, deletions, reordering, and truncation in the anchored tail. It does not detect someone who rewrites the whole ledger and seal unless the tip is anchored externally.

---

## Repo structure

```
ProofOS/
├── lean/                     # Lean 4 sources (proofs in progress)
├── src/aevion_runtime/       # ModelAccessEnvelope runtime
├── schemas/                  # JSON Schema specifications
├── tests/                    # Python test suite (96 tests; see Quick start)
├── e2e/                      # Playwright end-to-end tests
├── docs/                     # Landing page (aevion.ai)
├── architecture.md           # System diagram
├── quorum.md                 # Agent Counsel Colony constitution
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Python project config
├── package.json              # Node/Playwright dependencies
└── CONTRIBUTING.md           # Contribution guide
```

---

## What's inside

| Component | Description | Link |
|-----------|-------------|------|
| Constitutional Halt Gate | Fail-closed gate on declared predicates (Lean proofs in progress) | [LeishmanBerger.lean](lean/LeishmanBerger.lean) |
| Receipt Chain | SHA-256 content-addressed, canonical JSON; replay against tip and count anchored at run time (does not detect a full rewrite of the ledger and seal) | [architecture.md](architecture.md) |
| Agent Counsel Colony | Seven-role counsel process specified in quorum.md (Byzantine and SIFT roles); not deployed in this repo | [quorum.md](quorum.md) |
| Capability Access Separation | Access envelopes PUBLIC → HUMAN\_ONLY; Lean proofs in progress | [CapabilityAccessSeparation.lean](lean/CapabilityAccessSeparation.lean) |
| ModelAccessEnvelope | Runtime access control for frontier models | [model_access_envelope.py](src/aevion_runtime/model_access_envelope.py) |
| Playwright E2E | Browser smoke tests for the aevion.ai dashboard | [smoke.spec.ts](e2e/smoke.spec.ts) |
| JSON Schemas | Schema specifications for all interface contracts | [schemas/](schemas/) |

## Architecture

This table maps design themes to what ships in this repository:

| Principle | Implementation |
|-----------|---------------|
| Continuous monitoring | Receipt chain — every decision emits an auditable record |
| Proactive red-teaming | Agent Counsel Colony — Byzantine and SIFT roles as specified in quorum.md |
| Operational resilience | Halt gate (ALLOW/DENY only in runtime). Human Gate hold, release, approval, and escalation (escalation-rate targets (planned) in architecture.md) planned, not implemented |

The full architecture diagram and walkthrough are in [architecture.md](architecture.md).

## Agent Counsel Colony

[quorum.md](quorum.md) specifies a designed Agent Counsel Colony review process (seven roles) and how votes aggregate; it does not run automatically on every commit in this repository. Each role is distinct — from deterministic rule-checking to Byzantine adversarial probing to pure-function intent folding. The DiF agent is a deterministic function. The SIFT agent strips decorative reasoning from other agents' outputs before the Arbiter synthesizes a final verdict in that specified process.

The colony is specified in the Quorum Constitution, not deployed as production automation in this public mirror.

## Lean proofs (in progress)

Lean 4 modules in [lean/](lean/) (e.g. [CapabilityAccessSeparation.lean](lean/CapabilityAccessSeparation.lean), [LeishmanBerger.lean](lean/LeishmanBerger.lean)) are under active development. This README does not publish theorem counts or proof completion status.

Contact <scott@aevion.ai> for questions about Lean modules in this repository.

## Paper

Architecture paper: in preparation; not yet submitted.

## License

MIT

---

© 2026 Aevion LLC · Sartell, Minnesota · [scott@aevion.ai](mailto:scott@aevion.ai)
