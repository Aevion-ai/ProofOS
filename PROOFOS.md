# ProofOS

[![Lean Build](https://img.shields.io/badge/lean%20build-EXIT%200-brightgreen)](lean-proofs/)
[![Proof Density](https://img.shields.io/badge/proof%20density-96.02%25-brightgreen)](lean-proofs/Aevion/)
[![Open Obligations](https://img.shields.io/badge/open%20obligations-104-orange)](lean-proofs/Aevion/)
[![Tests](https://img.shields.io/badge/tests-82%2F82%20PASS-brightgreen)](tests/)
[![Paper](https://img.shields.io/badge/paper-arXiv%20ready-blue)](docs/papers/proofos_architecture_arxiv_v1.pdf)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![NIST Consortium](https://img.shields.io/badge/NIST%20AI%20Consortium-applicant-blue)](docs/federal/)

**Receipt chain for Lean 4 proof obligations.** Every agent decision generates a cryptographically chained, machine-checkable artifact. 1,283 theorems at 96% density across 350 files. Backed by decades of verified high-assurance systems lineage (seL4, HACMS, CertiKOS, CompCert).

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
| Constitutional Halt Gate | Lean 4 predicates block unsafe state transitions | [LeishmanBerger.lean](lean-proofs/Aevion/Consensus/LeishmanBerger.lean) |
| Receipt Chain | SHA-256 content-addressed, canonical JSON, append-only | [canonical.py](core/python/proofdb/canonical.py) |
| Agent Counsel Colony | N-agent review council with Byzantine fault detection and SIFT filtering | [colony.py](integrations/tinker_cookbook/counsel/colony.py) |
| Capability Access Separation | Access envelopes PUBLIC → HUMAN\_ONLY, Lean-proven tier ordering | [CapabilityAccessSeparation.lean](lean-proofs/Aevion/Runtime/CapabilityAccessSeparation.lean) |
| ModelAccessEnvelope | Runtime access control for frontier models | [model_access_envelope.py](src/aevion_runtime/model_access_envelope.py) |
| Open-Obligation Surface | Named, categorized, receipt-stamped obligations (machine-readable Gödel register) | [lean-proofs/Aevion/](lean-proofs/Aevion/) |

## Architecture

The architecture instantiates three prescriptions from a 2026 NIST proof (Vassilev, IEEE S&P, DOI: `10.1109/MSEC.2026.3678214`) that established no finite guardrail set is universally robust:

| Principle | Implementation |
|-----------|---------------|
| Continuous monitoring | Receipt chain — every decision emits an auditable record |
| Proactive red-teaming | Agent Counsel Colony — Byzantine + SIFT agents as standing capability |
| Operational resilience | Constitutional halt gate + Human Gate escalation |

The full architecture diagram and walkthrough are in [docs/architecture/proofos_architecture_diagram.md](docs/architecture/proofos_architecture_diagram.md).

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

## Verified Systems Lineage

ProofOS extends a three-decade pattern of formally verified boundaries from operating systems to AI governance:

| System | What Was Proved | ProofOS Equivalent |
|--------|----------------|-------------------|
| **seL4** (NICTA/Data61) | Microkernel implementation correctness — all syscalls gated by proved capability checks | Constitutional Halt Gate — all agent state transitions gated by proved Lean predicates |
| **HACMS** (DARPA) | Attack helicopter software immune to code injection — red teams could not compromise | Byzantine + SIFT agents as standing red-team capability — adversarial review before every merge |
| **CertiKOS** (Yale/Columbia) | Layered OS abstraction proofs — each layer proved against the layer below | DiF → Fable → Human Gate layered enforcement chain — failures escalate upward |
| **CompCert** (INRIA) | Verified C compiler — compiler never introduces bugs absent in source | Receipt chain — `canonical_dumps()` → `canonical_sha256()` → ProofDB is deterministic and independently checkable |

The architectural principle is identical across all five systems: **verify the boundary, not the untrusted component.** seL4 verifies the kernel interface; ProofOS verifies the agent action interface.

## Paper

[Proof-Native Constitutional Harnesses: An Architecture with a Published Open-Obligation Surface](docs/papers/proofos_architecture_arxiv_v1.pdf) — 11 pages, arXiv-ready, clean compile (0 warnings).

See also: [arXiv submission checklist](docs/launch/arxiv_submission_checklist.md)

## License

Apache 2.0

---

[Aevion LLC](https://aevion.ai) — SDVOSB — NIST AI Consortium applicant
