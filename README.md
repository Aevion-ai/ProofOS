# ProofOS

[![Version](https://img.shields.io/badge/version-v1.0.0-teal)](https://github.com/Aevion-ai/ProofOS/releases/tag/v1.0.0)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Lean 4](https://img.shields.io/badge/Lean-4.16.0-7B2D8B)](lean/)
[![CI](https://github.com/Aevion-ai/ProofOS/actions/workflows/ci.yml/badge.svg)](https://github.com/Aevion-ai/ProofOS/actions)

**Receipt chain for Lean 4 proof obligations.** Every agent decision generates a cryptographically chained, machine-checkable artifact. 1,252 theorems at 96% density across 343 files.

---

## What it does

ProofOS wraps AI agent decisions in a constitutional halt gate backed by Lean 4 proofs. When an agent proposes an action, the system checks it against declared safety predicates. If the check passes, a SHA-256 receipt is emitted. If it fails, the action is blocked. Every receipt is content-addressed, append-only, and independently verifiable.

The unprovable remainder — 104 open obligations across 32 files — is published as a machine-readable gap list. No confidence percentages. No hidden failure surfaces. An auditor reads the gap list.

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

## What's inside

| Component | Description | Link |
|-----------|-------------|------|
| Constitutional Halt Gate | Lean 4 predicates block unsafe state transitions | [LeishmanBerger.lean](lean/LeishmanBerger.lean) |
| Receipt Chain | SHA-256 content-addressed, canonical JSON, append-only | [architecture.md](architecture.md) |
| Agent Counsel Colony | N-agent review council with Byzantine fault detection and SIFT filtering | [quorum.md](quorum.md) |
| Capability Access Separation | Access envelopes PUBLIC → HUMAN\_ONLY, Lean-proven (3 theorems) | [CapabilityAccessSeparation.lean](lean/CapabilityAccessSeparation.lean) |
| ModelAccessEnvelope | Runtime access control for frontier models | [model_access_envelope.py](src/aevion_runtime/model_access_envelope.py) |
| Open-Obligation Surface | 104 named, categorized, receipt-stamped obligations | [lean/](lean/) |

## Architecture

The architecture instantiates three prescriptions from a 2026 NIST proof (Vassilev, IEEE S&P, DOI: `10.1109/MSEC.2026.3678214`) that established no finite guardrail set is universally robust:

| Principle | Implementation |
|-----------|---------------|
| Continuous monitoring | Receipt chain — every decision emits an auditable record |
| Proactive red-teaming | Agent Counsel Colony — Byzantine + SIFT agents as standing capability |
| Operational resilience | Constitutional halt gate + Human Gate escalation |

The full architecture diagram and walkthrough are in [architecture.md](architecture.md).

## Agent Counsel Colony

Seven agents review every change before it's committed. A Quorum Constitution ([quorum.md](quorum.md)) defines how their votes aggregate.

| Agent | Role | Status |
|-------|------|--------|
| DeterministicCounsel | Rule-based safety floor (TTS 0.850) | Healthy |
| ByzantineCounsel | Adversarial red-team with SIFT pre-filter (TTS 0.429) | Healthy |
| DiFCounsel | Pure deterministic function — cannot hallucinate (TTS 0.950) | Healthy |
| SIFTCounsel | Strips decorative reasoning from other agents (TTS 0.880) | Healthy |
| StochasticCounsel | Probability distribution estimator (TTS 0.120) | Pre-training |
| NonDeterministicCounsel | Edge case explorer (TTS 0.120) | Pre-training |
| CounselArbiter | Synthesizes verdicts, applies Quorum Constitution | — |

Evaluated on 150 stratified cases: 88% auto-pass, 4.0% Byzantine veto, 82% DiF agreement.

## Proven theorems

| Theorem | Status |
|---------|--------|
| `haltSoundness` | Proved (0 sorry) |
| `barrierInvariance` | Proved (0 sorry) |
| `byzantineGovernance` | Proved (7 theorems, 0 sorry) |
| `barabanov_norm_implies_GAS` | Proved (0 sorry) |
| `interaction_bounded` | Proved |
| `etaRecurrenceFinite` | Proved (4 sorries closed) |
| `accessTier_le_trans` | Proved (0 sorry) |

## Paper

[Proof-Native Constitutional Harnesses: An Architecture with a Published Open-Obligation Surface](paper.md)

## License

Apache 2.0

---

[Aevion LLC](https://aevion.ai) — SDVOSB — NIST AI Consortium applicant
