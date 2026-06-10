# ProofOS

[![Lean 4](https://img.shields.io/badge/Lean-4.16.0-7B2D8B)](lean/)
[![Tests](https://img.shields.io/badge/tests-20%2F20%20PASS-brightgreen)](tests/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![NIST Consortium](https://img.shields.io/badge/NIST%20AI%20Consortium-applicant-blue)](https://www.nist.gov/aisi)

**Receipt chain for Lean 4 proof obligations.** Every agent decision generates a cryptographically chained, machine-checkable artifact. This public repository ships 2 Lean 4 modules — 4 proved theorems (0 `sorry`) and 2 open obligations — published as a machine-readable gap list. The methodology, not a headline number, is the deliverable. The broader Aevion formal corpus is maintained privately.

---

## What it does

ProofOS wraps AI agent decisions in a constitutional halt gate backed by Lean 4 proofs. When an agent proposes an action, the system checks it against declared safety predicates. If the check passes, a SHA-256 receipt is emitted. If it fails, the action is blocked. Every receipt is content-addressed, append-only, and independently verifiable.

The unprovable remainder — in this repository, 2 open obligations in `lean/CapabilityAccessSeparation.lean` — is published as a gap list rather than hidden behind a confidence percentage. No hidden failure surfaces. An auditor reads the gap list.

```
Agent Action → Halt Gate (Lean 4 predicate) → Colony Review (7 agents) → Receipt (SHA-256) → Ledger
```

---

## What's inside

| Component | Description | Link |
|-----------|-------------|------|
| Constitutional Halt Gate | Lean 4 predicates block unsafe state transitions | [LeishmanBerger.lean](lean/LeishmanBerger.lean) |
| Capability Access Separation | Access-tier ordering, Lean-proved (3 theorems, 0 sorry) | [CapabilityAccessSeparation.lean](lean/CapabilityAccessSeparation.lean) |
| ModelAccessEnvelope | Runtime access control for frontier models (20/20 tests) | [model_access_envelope.py](src/aevion_runtime/model_access_envelope.py) |
| Open-Obligation Surface | Named, receipt-stamped obligations (2 open in this repo) | [lean/](lean/) |

The receipt-chain implementation, ProofDB store, and the Agent Counsel Colony (`colony.py`) live in the private Aevion stack and are not vendored here; this repository is a public slice.

## Proven theorems (in this repo)

| Theorem | Module | Status |
|---------|--------|--------|
| `haltSoundness` | `lean/LeishmanBerger.lean` | Proved (0 sorry) |
| `accessTier_le_trans` | `lean/CapabilityAccessSeparation.lean` | Proved (0 sorry) |
| `humanOnly_is_top` | `lean/CapabilityAccessSeparation.lean` | Proved (0 sorry) |
| `public_is_bottom` | `lean/CapabilityAccessSeparation.lean` | Proved (0 sorry) |
| `envelope_composition_monotonic` | `lean/CapabilityAccessSeparation.lean` | Open (`True` placeholder) |
| `fallback_preserves_safety` | `lean/CapabilityAccessSeparation.lean` | Open (`sorry`) |

## Design lineage (by analogy)

ProofOS applies a well-established pattern — **verify the boundary, not the untrusted component** — to AI agent actions. The analogy to verified-systems milestones is inspirational, not a claim of equivalent verification scope:

| System | What it verified | The analogy in ProofOS |
|--------|------------------|------------------------|
| seL4 | Microkernel implementation correctness | Halt gate verifies the agent-action interface |
| HACMS | Code-injection-resistant flight software | Byzantine/SIFT agents as standing red-team |
| CertiKOS | Layered OS abstraction proofs | Layered enforcement → human-gate escalation |
| CompCert | Verified compiler determinism | Deterministic, re-derivable receipt chain |

ProofOS does **not** claim seL4/HACMS/CertiKOS/CompCert-scale verification; those systems carry full machine-checked implementation proofs. ProofOS verifies declared safety predicates and publishes its open obligations.

## Paper

A technical paper (*Proof-Native Constitutional Harnesses*) is **in preparation** and not yet submitted. A working draft PDF is under `docs/papers/`.

---

[Aevion LLC](https://aevion.ai) — SDVOSB — NIST AI Safety Institute Consortium applicant
