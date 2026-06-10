# ProofOS Architecture Diagram

**Date:** 2026-06-09
**Status:** Architecture reference. External-facing use still passes claim review; numbers describe **this public repository**, not the private corpus.

---

## Full Architecture

```
                         ┌──────────────────────────────────┐
                         │         ANY AI SYSTEM             │
                         │  (model, agent, workflow, swarm)  │
                         │  K2.6 (1K agents) | GPT-5.4 | ... │
                         └──────────────┬───────────────────┘
                                        │
          ┌─────────────────────────────┼─────────────────────────────┐
          │                             │                             │
          │   Vassilev Prescription 1:  │   Continuous Monitoring     │
          │                             │                             │
          ▼                             ▼                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        CONSTITUTIONAL HALT GATE                          │
│  Lean 4 predicates — blocks transition if guard fails                    │
│  haltSoundness (proved, 0 sorry) | accessTier ordering (proved, 0 sorry)  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           RECEIPT CHAIN                                  │
│  SHA-256 canonical JSON | ProofDB content-addressed store                │
│  canonical_sha256() — single source of truth                             │
│  Every gating decision emits an immutable, independently re-derivable    │
│  record                                                                    │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          │   Vassilev Prescription 2: Proactive Red-Teaming    │
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      AGENT COUNSEL COLONY (N agents)                     │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │Deterministic │  │  Stochastic  │  │  Byzantine   │                   │
│  │  Counsel     │  │   Counsel    │  │   Counsel    │                   │
│  │  TTS: 0.850  │  │  TTS: 0.120  │  │  TTS: 0.429  │                   │
│  │  HEALTHY     │  │  DRIFTING    │  │  HEALTHY     │                   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                   │
│         │                 │                 │                            │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐                   │
│  │     DiF      │  │    SIFT      │  │   Arbiter    │                   │
│  │   Counsel    │  │   Counsel    │  │              │                   │
│  │  TTS: 0.950  │  │  TTS: 0.880  │  │  88% auto    │                   │
│  │  HEALTHY     │  │  HEALTHY     │  │  12% escalate│                   │
│  │  PURE FUNC   │  │  FILTER      │  │  4% veto     │                   │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
│                                                                          │
│  Infrastructure: CircuitBreaker | AgentSandbox | DeterministicReplay     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          │   Vassilev Prescription 3: Resilience Mechanisms    │
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            HUMAN GATE                                    │
│  Escalation when guardrails disagree (as Theorem II.1 proves they must)  │
│  12% escalation rate | Approval token required for live operations       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│ OPEN-OBLIGATION │   │  PHYSICAL ROOT      │   │  QUANTUM WITNESS    │
│ SURFACE         │   │  OF TRUST           │   │  TILES              │
│                 │   │                     │   │                     │
│ 4 proved (0 srry)│   │  Pi Sheriff Node    │   │  Hardware witness   │
│ 2 open oblig.   │   │  Pi 5 (ARM64)       │   │  Simulator control  │
│ 2 modules       │   │  LCD + Camera       │   │  TVD delta check    │
│ public repo     │   │  DHT11 Sensor       │   │  NISQ noise detect  │
│ Gödel register  │   │  Ollama inference   │   │  INTERNAL_ONLY      │
└─────────────────┘   └─────────────────────┘   └─────────────────────┘
```

## Layer-to-Vassilev Mapping

| Layer | Vassilev Prescription | Proof |
|-------|----------------------|-------|
| Constitutional Halt Gate + Receipt Chain | Continuous monitoring + update cycle | receipt chain SHA-256, canonical serialization |
| Agent Counsel Colony (Byzantine + SIFT) | Proactive red-teaming | internal 150-case eval (harness not vendored here): 88% auto-pass, 4% veto |
| Human Gate + Open-Obligation Surface | Resilience mechanisms | 2 named obligations (this repo), 12% escalation rate |

## Why Three Roots of Trust

The architecture terminates in three roots of trust because no single root is sufficient:

1. **Open-Obligation Surface** — the formal root. What the Lean kernel can and cannot prove.
2. **Physical Root of Trust** — the hardware root. Pi witness receipts prove the system ran on real hardware at a specific time.
3. **Quantum Witness Tiles** — the physics root. Hardware-vs-simulator TVD proves the system can detect when the physical substrate disagrees with the ideal model.

Theorem II.1 applies to all three layers. The receipt chain is the only thing that spans them.
