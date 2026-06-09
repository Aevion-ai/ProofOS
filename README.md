# Aevion ProofOS

## One Sentence

> **NIST published the proof. Anthropic launched the product architecture. Aevion built the proof-native control plane. All on June 9, 2026.**

---

## The Problem

On June 9, 2026, Apostol Vassilev (NIST) published Theorem II.1 in *IEEE Security & Privacy*: **no finite set of guardrails is universally robust against adversarial prompts.** This is a Gödel-Chaitin reduction applied to AI safety. It proves that any static checker \( C_\Pi \) will always miss some adversarial truth \( T_\Pi \).

Every AI safety system that reports a confidence percentage ("99.7% safe") has an invisible 0.3% failure surface. You don't know what you don't know. And Theorem II.1 proves you never will — not with a static guardrail.

## The Architecture

ProofOS is not a stronger static checker. It is a **receipted update protocol** — a dynamic system whose correctness is continuously re-established rather than statically claimed.

```
                    ┌──────────────────────────────────┐
                    │     ANY AI SYSTEM                 │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │   CONSTITUTIONAL HALT GATE        │
                    │   Lean 4 predicates               │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │   RECEIPT CHAIN                   │
                    │   SHA-256, content-addressed      │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │   AGENT COUNSEL COLONY (N agents) │
                    │   Red-team + filter + arbitrate   │
                    │   88% auto-pass | 4% veto | 82%   │
                    │   DiF agreement                   │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │   HUMAN GATE + GAP LIST           │
                    │   Machine-readable Gödel register │
                    └──────────────────────────────────┘
```

**Vassilev's three prescriptions → ProofOS instantiations:**

| Vassilev Says You Need | ProofOS Provides |
|------------------------|------------------|
| Continuous monitoring + update cycle | Receipt chain + PR-gated counsel review |
| Proactive red-teaming | Byzantine + SIFT agents as standing capability |
| Resilience mechanisms | Constitutional halt + Human Gate + gap list |

## The Open-Obligation Surface

Most AI safety vendors report a confidence percentage. **We publish the gap list.**

| Metric | Value |
|--------|-------|
| Active theorems | 1,252 (Lean 4.16.0, Mathlib pinned) |
| Proof density | 96.02% |
| Open obligations | 104 across 32 files |
| Discharged | ~91% |
| Corpus files | 343 |

The 9% that remains unproven is not a weakness. It is a **machine-readable Gödel register** — the exact set of propositions the formal system cannot currently discharge. Every gap is named, categorized, receipt-stamped, and auditable. An auditor reads the gap list, not a confidence number.

## What's Proved

| Theorem | File | Status |
|---------|------|--------|
| `haltSoundness` | `Aevion/Consensus/LeishmanBerger.lean` | PROVED (0 sorry) |
| `barabanov_norm_implies_GAS` | `Aevion/Dynamics/BarabanovStability.lean` | PROVED (0 sorry) |
| `byzantine_safe` | `Aevion/AuthorityCalculus/ByzantineGovernance.lean` | PROVED (0 sorry, 7 theorems) |
| `interaction_bounded` | `Aevion/Compliance/DrugInteraction.lean` | PROVED |
| `barrierInvariance` | `Aevion/BarrierInvariance.lean` | PROVED (0 sorry) |
| `etaRecurrenceFinite` | `Aevion/NumberTheory/RHAudit/EtaRecurrence.lean` | PROVED (4 sorries closed) |

## Agent Counsel Colony (live eval, June 9 2026)

150-case stratified evaluation across 5 categories:

| Agent | TTS | Status | Role |
|-------|-----|--------|------|
| DeterministicCounsel | 0.850 | HEALTHY | Rule-based safety floor |
| ByzantineCounsel | 0.429 | HEALTHY | Adversarial red-team (SIFT pre-filtered) |
| DiFCounsel | 0.950 | HEALTHY | Pure function, cannot hallucinate |
| SIFTCounsel | 0.880 | HEALTHY | Decorative reasoning filter |
| StochasticCounsel | 0.120 | DRIFTING | Exploration (pre-training) |
| NonDeterministicCounsel | 0.120 | DRIFTING | Unknown-unknown discovery |

**Council metrics:** 88% auto-pass | 12% gate escalation | 4.0% Byzantine veto | 82% DiF agreement

## Enterprise Use Cases

- **Agent Governance:** Any enterprise deploying agent swarms needs a governance layer. ProofOS is that layer.
- **Supply Chain Verification:** AI-BOM (NIST SP 800-218A aligned) generated from ProofDB.
- **Regulated Industry:** Proof-native audit trails for financial services, healthcare, defense.

## Competitive Positioning

| Competitor | What They Do | What They Don't Do |
|-----------|-------------|-------------------|
| **Anthropic** | Sells tokens | Doesn't prove what tokens did |
| **K2.6 (Moonshot)** | 1,000-agent swarms | Zero formal verification, principles-only governance |
| **Microsoft** | Agent governance toolkit (YAML/OPA) | No formal verification, no crypto receipts |

**Aevion's position:** The trust layer BENEATH all of them. Not competing on features. Competing on provability.

## What We Do NOT Claim

- NOT "fully verified" / "0 sorries." 104 obligations are open.
- NOT any regulatory certification (FAA/NIST/FIPS/CMVP/FedRAMP).
- NOT that the architecture defeats Vassilev's Theorem II.1. It accepts it as ground truth.
- NOT a behavioral-safety guarantee for arbitrary model outputs.
- NOT that the sorry corpus will ever reach zero — a Godelian system cannot close all its own obligations.

## How to Verify

Every claim in this document traces to a public artifact:

```bash
# Theorem/sorry counts
lake build Aevion && tools/lean_stats.py

# Colony eval
pytest tests/ -q

# Model access envelope
pytest tests/test_model_access_envelope.py -v
```

## Paper

[Proof-Native Constitutional Harnesses v1.0](papers/proof_native_constitutional_harness_v1.0.md)

Primary citation: Vassilev, A. "Robust AI Security and Alignment: A Sisyphean Endeavor?" *IEEE Security & Privacy*, May 2026. DOI: `10.1109/MSEC.2026.3678214`.

---

**Aevion LLC** — [aevion.ai](https://aevion.ai)
