# ProofOS Architecture Diagram

**Date:** 2026-06-09  
**Status:** Architecture reference aligned with the verified claim ceiling on `main` (see [README.md](README.md)).

**Shipped in this repository:** fail-closed evidence verification (forged or invalid input exits 1 with no ledger write); runtime policy gate decisions **ALLOW** or **DENY**, each with a SHA-256-chained receipt carrying the reason; replay against an anchored tip and receipt count.

**Specified, not deployed here:** Agent Counsel Colony ([quorum.md](quorum.md)); intercepting, holding, or pausing tool calls; hold/release; human approval or escalation (including rate targets such as 12%); **ESCALATE** as a runtime decision.

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
│  Hold, release, approval tokens, and escalation (e.g. design notes for     │
│  ~12% escalation in colony specs) are not wired into the public runtime  │
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
| Human gate (hold, release, approval, escalation) | **Planned** | Including ESCALATE and rate targets such as 12% in colony design docs |
| Lean 4 gate proofs | **In progress** | No published theorem-count or “fully proven” claims |
| Colony eval metrics (e.g. 88% auto-pass, 150-case harness) | **Not claimed** | No private harness or corpus in this mirror |

## Design context (not endorsements)

ProofOS receipt chaining is informed by published work on robust AI governance limits (see bibliography in [STANDARDS.md](STANDARDS.md)). That citation does not imply NIST, OpenSSF, or peer-review endorsement of ProofOS, and this repository does not ship certification or consortium-approval claims.
