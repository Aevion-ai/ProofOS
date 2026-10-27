# ProofOS

[![Lean 4](https://img.shields.io/badge/Lean-4.16.0-7B2D8B)](lean/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)

**Receipt chain for AI agent decisions.** Fail-closed ALLOW/DENY gating with SHA-256-chained receipts; Lean 4 proofs are in progress.

Canonical public documentation: [README.md](README.md).

---

## What it does

ProofOS scores a submitted evidence envelope in a runtime constitutional halt gate and returns **ALLOW** or **DENY** with a SHA-256 receipt that carries the reason. Forged or invalid evidence is rejected with exit code 1 and nothing is written to the ledger. The runtime does not intercept, hold, or pause tool calls (planned). Receipts can be checked by replaying the chain against the tip and count anchored at run time.

The Agent Counsel Colony is **specified** in [quorum.md](quorum.md), **not deployed** in this repository. Human hold, release, approval, and escalation—including design targets such as 12% escalation in architecture notes—are **planned**, not implemented.

```
Agent Action → Fail-closed Halt Gate (ALLOW/DENY) → Receipt (SHA-256) → Ledger
```

---

## What's inside

| Component | Description | Link |
|-----------|-------------|------|
| Constitutional Halt Gate | Runtime ALLOW/DENY on evidence (Lean proofs in progress) | [demo](src/aevion_runtime/demo.py) |
| Receipt Chain | SHA-256 chained receipts; replay vs anchored tip/count | [architecture.md](architecture.md) |
| Capability Access Separation | Access-tier ordering in Lean sources (proofs in progress) | [CapabilityAccessSeparation.lean](lean/CapabilityAccessSeparation.lean) |
| ModelAccessEnvelope | Runtime access control for frontier models | [model_access_envelope.py](src/aevion_runtime/model_access_envelope.py) |
| Agent Counsel Colony | Seven-role process specified in quorum.md; not deployed here | [quorum.md](quorum.md) |

## Lean proofs (in progress)

Lean 4 modules in [lean/](lean/) are under active development. This document does not publish theorem counts or a “fully proven” status for the gate.

## Design lineage (by analogy)

ProofOS applies a well-established pattern — **verify the boundary, not the untrusted component** — to AI agent actions. The analogy to verified-systems milestones is inspirational, not a claim of equivalent verification scope:

| System | What it verified | The analogy in ProofOS |
|--------|------------------|------------------------|
| seL4 | Microkernel implementation correctness | Halt gate verifies the agent-action interface |
| HACMS | Code-injection-resistant flight software | Byzantine/SIFT roles in the **specified** colony |
| CertiKOS | Layered OS abstraction proofs | Layered enforcement → **planned** human-gate escalation |
| CompCert | Verified compiler determinism | Deterministic, re-derivable receipt chain (**shipped**) |

ProofOS does **not** claim seL4/HACMS/CertiKOS/CompCert-scale verification.

## Paper

Architecture paper: in preparation; not yet submitted.

---

[Aevion LLC](https://aevion.ai) — SDVOSB
