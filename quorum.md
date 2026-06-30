# Agent Counsel Colony — Quorum Constitution v1.0

**Date:** 2026-06-09
**Status:** Active — governs all counsel colony decisions
**Binding on:** All 7 agents + Piper Sheriff

---

## 1. Purpose

The Quorum Constitution defines how individual agent verdicts aggregate into a council decision. Without an explicit constitution, the aggregation rules are implicit, untestable, and vulnerable to Byzantine override of legitimate dissent.

This document is the single source of truth. The `CounselArbiterEnv` implementation in `colony.py` MUST implement these rules exactly. Any deviation is a bug.

---

## 2. Agent Roles and Vote Weights

| Agent | Role | Vote Weight | Must Produce | Vote Semantics |
|-------|------|------------|--------------|----------------|
| **DeterministicCounsel** | Rule-based safety floor | 1 | Named rule on EVERY verdict (pass or fail) | DISSENT = hard rule violation. Can block alone if proof_density < 0.90 AND sorry_delta > 0 |
| **StochasticCounsel** | Probability distribution estimator | 1 | Confidence interval width | DISSENT = P(harm) > 0.15 OR confidence interval width > 0.40. Cannot block alone — requires 1+ other non-DiF agent |
| **NonDeterministicCounsel** | Edge case explorer | 1 | ≥1 edge case candidate per cycle OR ABSTAIN | DISSENT = edge case found that no other agent caught. Cannot block alone — requires 2+ other agents |
| **ByzantineCounsel** | Adversarial red-team | 1 (veto weight: 2) | Named failure mode classification (deep vs. surface) | VETO requires: (a) ≥1 deep failure mode, AND (b) ≥1 other non-Byzantine agent also rejects. Veto weight 2 means Byzantine DISSENT counts as 2 dissenting votes for threshold purposes |
| **DiFCounsel** | Pure function intent folder | 1 (non-overridable) | Intent label + action mapping | DISSENT = halt or drift intent. Non-overridable by Byzantine alone — requires 3+ agents to override DiF DISSENT |
| **SIFTCounsel** | Pre-aggregation noise filter | 0 (gate, not vote) | Decorative ratio + filter decision | POSITION: runs BEFORE vote aggregation. GATE: SIFT BLOCK = council never sees input. SIFT PASS = input passes to council. SIFT ABSTAIN = input passes with warning |
| **CounselArbiter** | Synthesizer | N/A (decides, doesn't vote) | Final verdict + quorum analysis | Synthesizes weighted votes per Constitution §4 |
| **SheriffAgent** | Cross-architecture witness | 0 (countersigns, doesn't vote) | CONFIRM/FLAG/ABSTAIN attestation | Runs on Pi 5 (ARM64, independent). FLAG = DISPUTED provenance, not a vote override |

---

## 3. Pre-Aggregation Pipeline (Order is Load-Bearing)

```
INPUT (PR item)
    │
    ▼
┌──────────────────────┐
│  SIFT PRE-FILTER     │  ← GATE position (not voter)
│  Decorative ratio <  │     BLOCK: input rejected before council sees it
│  0.30 → PASS         │     PASS: input proceeds to council
│  ≥ 0.30 → ABSTAIN    │     ABSTAIN: input proceeds with warning flag
│  ≥ 0.50 → BLOCK      │
└──────┬───────────────┘
       │ (if PASS or ABSTAIN)
       ▼
┌──────────────────────┐
│  DETERMINISTIC        │  ← First voter (safety floor)
│  Must emit named rule │     APPROVE: deterministic_pass
│  on EVERY verdict     │     DISSENT: deterministic_block(<reason>)
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  STOCHASTIC           │  ← Second voter (distribution check)
│  Must report CI width │     APPROVE: stochastic_pass
│  DISSENT semantics:   │     DISSENT: stochastic_dissent(P_harm=X, CI_width=Y)
│  uncertainty too high │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  NON-DETERMINISTIC    │  ← Third voter (edge case exploration)
│  Must produce ≥1 edge │     APPROVE: nondeterministic_pass
│  case OR ABSTAIN      │     DISSENT: nondeterministic_edge_case(<description>)
│  DISSENT semantics:   │     ABSTAIN: nondeterministic_abstain
│  found unexamined path│
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  BYZANTINE (pre-      │  ← Fourth voter (adversarial scan)
│  filtered by SIFT)    │     APPROVE: byzantine_pass
│  Must classify: deep  │     DISSENT: byzantine_veto(<deep_failure_modes>)
│  vs. surface modes    │     HOLD: byzantine_concern(<surface_modes>)
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  DiF (intent folder)  │  ← Fifth voter (pure function)
│  Non-overridable by   │     APPROVE: dif_intent_binding(exploit)
│  Byzantine alone      │     DISSENT: dif_drift_binding(halt|drift)
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  ARBITER              │  ← Synthesizer
│  Applies Constitution │
│  §4 quorum rules      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  SHERIFF (Pi 5)       │  ← Independent attestation
│  Cross-architecture   │     CONFIRM/FLAG/ABSTAIN
│  countersigns receipt │
└──────────────────────┘
```

---

## 4. Quorum Aggregation Rules

### 4.1 Voting Population

- Total voting agents: 5 (Deterministic, Stochastic, NonDeterministic, Byzantine, DiF)
- SIFT is a gate, not a voter
- Arbiter synthesizes, doesn't vote
- Sheriff attests, doesn't vote

### 4.2 Concurrence Thresholds

| Verdict | Requirement |
|---------|------------|
| **APPROVE** | ≥4 of 5 voting agents APPROVE, AND 0 agents DISSENT, AND no SIFT BLOCK |
| **DISSENT** | ≥2 of 5 agents DISSENT, AND no Byzantine VETO fires |
| **CONFLICTED** | Byzantine VETO fires (≥1 deep mode + ≥1 other reject), OR DiF DISSENT + ≥2 other agents DISSENT |
| **REQUEST_CHANGES** | 1 agent DISSENT (insufficient for full DISSENT) OR SIFT ABSTAIN with ≥0.30 decorative ratio |
| **HOLD** | Council cannot reach concurrence (tie, uncertainty, agents abstaining), OR ≥3 agents ABSTAIN |
| **ESCALATE** | Human gate: CONFLICTED verdict, OR ≥1 agent DISSENT + council agreement < 0.50 |

### 4.3 Weight and Override Rules

1. **Byzantine weight multiplier:** Byzantine DISSENT counts as 2 dissenting votes for threshold calculations. This reflects the adversarial agent's specialized role.

2. **DiF non-overridability:** DiF DISSENT cannot be overridden by Byzantine alone. Overriding DiF DISSENT requires ≥3 other agents to APPROVE (qualified supermajority).

3. **Deterministic block authority:** Deterministic DISSENT with `proof_density < 0.90 AND sorry_delta > 0` is a constitutional halt — council cannot APPROVE regardless of other votes. The item must be REQUEST_CHANGES or DISSENT.

4. **SIFT gate authority:** SIFT BLOCK (decorative ratio ≥ 0.50) prevents the input from reaching the council. The item is returned as REQUEST_CHANGES with reason "sift_block_excessive_decorative."

### 4.4 Agent-Specific DISSENT Semantics

| Agent DISSENT | Means | Minimum Other Support Needed |
|--------------|-------|------------------------------|
| Deterministic DISSENT | Hard rule violation | 0 (can block alone if constitutional halt) |
| Stochastic DISSENT | Distribution too wide to act | 1 other non-DiF agent |
| NonDeterministic DISSENT | Unexamined edge case found | 2 other agents |
| Byzantine VETO | Deep adversarial pattern | 1 other non-Byzantine reject |
| DiF DISSENT | Halt or drift intent | 3 to override (qualified supermajority) |

---

## 5. Named Rule Instrumentation

Every agent MUST emit a named rule on every verdict. Silent votes are forbidden.

| Agent | Pass Rule | Dissent Rule |
|-------|----------|--------------|
| Deterministic | `deterministic_pass` | `deterministic_block(<reason>)` |
| Stochastic | `stochastic_pass(P_harm=X, CI_width=Y)` | `stochastic_dissent(P_harm=X, CI_width=Y)` |
| NonDeterministic | `nondeterministic_pass` | `nondeterministic_edge_case(<desc>)` |
| Byzantine | `byzantine_pass` | `byzantine_veto(<deep_modes>)` or `byzantine_concern(<surface_modes>)` |
| DiF | `dif_intent_binding(<intent>)` | `dif_drift_binding(<intent>)` |
| SIFT | `sift_pass(ratio=X)` | `sift_block(ratio=X)` or `sift_abstain(ratio=X)` |
| Sheriff | `sheriff_confirm` | `sheriff_flag(<signature>)` |

---

## 6. Eval Instrumentation Requirements

Every council decision receipt MUST include:

- `arbiter_rules`: list of ALL named rules fired (pass and dissent)
- `vote_counts`: per-action counts with agent names
- `quorum_analysis`: which §4 rule was applied
- `constitution_version`: "1.0"

---

## 7. Relationship to Vassilev Theorem II.1

The constitution is the formal acknowledgment that Vassilev's theorem applies: no finite rule set is universally robust. The constitution is therefore **versioned and receipted** — it can be amended by a new council decision that passes a constitutional halt gate check on the amendment itself. The constitution governs its own amendment.

---

## 8. Implementation

- **Specification:** This document (`quorum.md`)
- **Implementation:** `CounselArbiterEnv` in the private Aevion stack (`colony.py`) — not vendored in this public repository
- **Verification:** internal eval harness (150-problem corpus); results reported as internal, not reproducible from this repo
- **Version:** 1.0
- **Receipt:** Every eval run emits a receipt citing this constitution version
