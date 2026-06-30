# ProofOS

[![Version](https://img.shields.io/badge/version-v1.0.0-teal)](https://github.com/Aevion-ai/ProofOS/releases/tag/v1.0.0)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Lean 4](https://img.shields.io/badge/Lean-4.16.0-7B2D8B)](lean/)
[![CI](https://github.com/Aevion-ai/ProofOS/actions/workflows/ci.yml/badge.svg)](https://github.com/Aevion-ai/ProofOS/actions)

**Receipt chain for Lean 4 proof obligations.** Every agent decision generates a cryptographically chained, machine-checkable artifact.

---

## Public mirror

ProofOS is the **governed public mirror** of the canonical Aevion monorepo,
[Aevion-ai/Aevion-Verifiable-AI](https://github.com/Aevion-ai/Aevion-Verifiable-AI).
Only the allow-listed paths in [MIRROR_MANIFEST.md](MIRROR_MANIFEST.md) are copied
from the monorepo; secrets, credentials, and internal-only evidence are never
mirrored. See the manifest for the current sync status and path map.

## What it does

ProofOS wraps AI agent decisions in a constitutional halt gate backed by Lean 4 proofs. When an agent proposes an action, the system checks it against declared safety predicates. If the check passes, a SHA-256 receipt is emitted. If it fails, the action is blocked. Every receipt is content-addressed, append-only, and independently verifiable.

The design follows a published impossibility result (Vassilev, *IEEE S&P*, 2026) that no finite guardrail set is universally robust, and implements the three architectural responses it motivates: continuous monitoring via receipt chains, proactive red-teaming via a multi-agent counsel colony, and operational resilience via constitutional halt gates and human-in-the-loop escalation. (This is convergence on a shared prescription, not an endorsement of ProofOS by NIST.)

```
Agent Action → Halt Gate (Lean 4 predicate) → Colony Review (7 agents) → Receipt (SHA-256) → Ledger
```

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
tests/test_model_access_envelope.py .................... [100%]
20 passed in 0.71s
```

---

## Repo structure

```
ProofOS/
├── lean/                     # Example Lean 4 proofs (full corpus: contact for access)
├── src/aevion_runtime/       # ModelAccessEnvelope runtime
├── schemas/                  # JSON Schema specifications
├── tests/                    # Python test suite (20/20)
├── e2e/                      # Playwright end-to-end tests
├── docs/                     # Landing page (aevion.ai) + draft paper PDF
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
| Constitutional Halt Gate | Lean 4 predicates block unsafe state transitions | [LeishmanBerger.lean](lean/LeishmanBerger.lean) |
| Receipt Chain | SHA-256 content-addressed, canonical JSON, append-only | [architecture.md](architecture.md) |
| Agent Counsel Colony | N-agent review council with Byzantine fault detection and SIFT filtering | [quorum.md](quorum.md) |
| Capability Access Separation | Access envelopes PUBLIC → HUMAN\_ONLY, Lean-proven (3 theorems) | [CapabilityAccessSeparation.lean](lean/CapabilityAccessSeparation.lean) |
| ModelAccessEnvelope | Runtime access control for frontier models (20/20 tests) | [model_access_envelope.py](src/aevion_runtime/model_access_envelope.py) |
| Playwright E2E | Browser smoke tests for the aevion.ai dashboard | [smoke.spec.ts](e2e/smoke.spec.ts) |
| JSON Schemas | Schema specifications for all interface contracts | [schemas/](schemas/) |

## Architecture

The architecture instantiates three prescriptions from a 2026 NIST proof (Vassilev, IEEE S&P, DOI: `10.1109/MSEC.2026.3678214`) that established no finite guardrail set is universally robust:

| Principle | Implementation |
|-----------|---------------|
| Continuous monitoring | Receipt chain — every decision emits an auditable record |
| Proactive red-teaming | Agent Counsel Colony — Byzantine + SIFT agents as standing capability |
| Operational resilience | Constitutional halt gate + Human Gate escalation |

The full architecture diagram and walkthrough are in [architecture.md](architecture.md).

## Agent Counsel Colony

Seven agents review every change before it's committed. A Quorum Constitution ([quorum.md](quorum.md)) defines how their votes aggregate. Each agent has a distinct role — from deterministic rule-checking to Byzantine adversarial probing to pure-function intent folding. The DiF agent is a deterministic function that cannot hallucinate. The SIFT agent strips decorative reasoning from other agents' outputs before the Arbiter synthesizes a final verdict.

The architecture is specified in the Quorum Constitution. Implementation and evaluation harnesses are available in the private repository.

## Proven theorems (in this repo)

| Theorem | File | Status |
|---------|------|--------|
| `accessTier_le_trans` | [CapabilityAccessSeparation.lean](lean/CapabilityAccessSeparation.lean) | Proved (0 sorry) |
| `humanOnly_is_top` | [CapabilityAccessSeparation.lean](lean/CapabilityAccessSeparation.lean) | Proved (0 sorry) |
| `public_is_bottom` | [CapabilityAccessSeparation.lean](lean/CapabilityAccessSeparation.lean) | Proved (0 sorry) |
| `envelope_composition_monotonic` | [CapabilityAccessSeparation.lean](lean/CapabilityAccessSeparation.lean) | Reducible sorry |
| `fallback_preserves_safety` | [CapabilityAccessSeparation.lean](lean/CapabilityAccessSeparation.lean) | Reducible sorry |
| `haltSoundness` | [LeishmanBerger.lean](lean/LeishmanBerger.lean) | Proved |

Note: the broader Lean 4 corpus is maintained privately in the Aevion-Verifiable-AI repository; its counts are not reproduced here to avoid publishing figures that cannot be checked from this repo. Contact <scott@aevion.ai> for access.

## Paper

*Proof-Native Constitutional Harnesses: An Architecture with a Published Open-Obligation Surface* — in preparation; not yet submitted. Working [draft PDF](docs/papers/proofos_architecture_arxiv_v1.pdf).

## License

Apache 2.0

---

[Aevion LLC](https://aevion.ai) — SDVOSB — NIST AI Consortium applicant
