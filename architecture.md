# ProofOS Architecture Diagram

**Date:** 2026-06-09  
**Status:** Architecture reference aligned with the verified claim ceiling on `main` (see [README.md](README.md)).

**Shipped in this repository:** fail-closed evidence verification (forged or invalid input exits 1 with no ledger write); runtime policy gate decisions **ALLOW** or **DENY**, each with a SHA-256-chained receipt carrying the reason; replay against an anchored tip and receipt count.

**Specified, not deployed here:** Agent Counsel Colony ([quorum.md](quorum.md)).

**Planned, not implemented:** intercepting, holding, or pausing tool calls; hold/release; human approval or escalation (including escalation-rate targets); **ESCALATE** as a runtime decision.

**In progress:** Lean 4 proofs for gate predicates (this mirror ships partial Lean sources only).

---

## Full Architecture

```
                         ┌──────────────────────────────────┐
                         │         ANY AI SYSTEM             │
                         │  (model, agent, workflow, swarm)  │
                         └──────────────┬───────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   RUNTIME CONSTITUTIONAL HALT GATE (SHIPPED)             │
│  Evidence envelope → ALLOW or DENY (fail-closed)                       │
│  Forged/invalid evidence: exit 1, no ledger write                        │
│  Lean 4 predicate proofs: in progress                                    │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        RECEIPT CHAIN (SHIPPED)                           │
│  SHA-256 canonical JSON | chained receipts with decision reason          │
│  Replay against tip receipt id + count anchored at run time              │
│  (does not detect a full rewrite of the ledger and seal)                 │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│           AGENT COUNSEL COLONY — SPECIFIED IN quorum.md (NOT DEPLOYED)   │
│                                                                          │
│  Seven roles (Deterministic, Stochastic, NonDeterministic, Byzantine,     │
│  DiF, SIFT, Arbiter) — voting rules, HOLD, and ESCALATE thresholds are    │
│  design targets for a future deployment, not runtime behavior in this repo │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              HUMAN GATE — PLANNED (NOT IMPLEMENTED IN THIS REPO)           │
│  Hold, release, approval tokens, and escalation-rate targets (planned) are │
│  not wired into the public runtime                                         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│ LEAN SOURCES    │   │  FUTURE: PHYSICAL   │   │  FUTURE: QUANTUM    │
│ (in progress)   │   │  WITNESS (planned)  │   │  WITNESS (planned)  │
│ partial modules │   │  not shipped here   │   │  not shipped here   │
│ in lean/        │   │                     │   │                     │
└─────────────────┘   └─────────────────────┘   └─────────────────────┘
```

## Layer summary

| Layer | Status in this repo | Notes |
|-------|---------------------|-------|
| Constitutional halt gate + receipt chain | **Shipped** | ALLOW/DENY only; SHA-256 receipts; replay vs anchored tip/count |
| Tool-call intercept / hold / pause | **Planned** | Not implemented |
| Agent Counsel Colony (Byzantine + SIFT roles) | **Specified** | [quorum.md](quorum.md); not deployed |
| Human gate (hold, release, approval, escalation) | **Planned** | Including ESCALATE and escalation-rate targets (planned) in colony design docs |
| Lean 4 gate proofs | **In progress** | No published theorem-count or “fully proven” claims |
| Colony evaluation metrics | **Planned** | No evaluation results are published from this repository |

## Design context (not endorsements)

Related reading is listed in the bibliography in [STANDARDS.md](STANDARDS.md). No endorsement, certification, or peer review of ProofOS by NIST, OpenSSF, or any other body is claimed.
