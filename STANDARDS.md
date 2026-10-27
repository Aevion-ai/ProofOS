# Standards Alignment

This document describes **design alignment** with public frameworks. It is not a claim of NIST or OpenSSF endorsement, certification, or peer review of ProofOS.

## NIST AI Risk Management Framework (design alignment)

ProofOS design themes are informed by NIST AI RMF 1.0 (AI 100-1) and the Secure Software Development Practices for Generative AI and Dual-Use Foundation Models community profile (SP 800-218A). Alignment is aspirational until independently assessed.

### Govern

- Constitutional halt gate enforces declared safety predicates before action execution (**ALLOW/DENY shipped** in this repo)
- Human gate escalation when automated guardrails disagree (**planned**; hold, release, and approval not implemented here)
- Open-obligation surface: Lean modules in progress; obligations are tracked in source rather than hidden behind confidence scores

### Map

- Receipt chain provides content-addressed audit trail for each **ALLOW/DENY** decision shipped in the runtime
- SHA-256 canonical serialization enables independent verification of receipts in the anchored tail
- Agent Counsel Colony multi-agent review is **specified** in [quorum.md](quorum.md), **not deployed** in this repository

### Measure

- Receipt chain validation and replay against anchored tip/count (**shipped**)
- Agent TTS (True-Thinking Score) and colony eval metrics (e.g. auto-pass rates) are **design targets** for a future deployment, not reported results from this mirror

### Manage

- Quorum Constitution defines aggregation rules for the **specified** counsel colony process
- Capability Access Separation enforces tiered deployment (PUBLIC → BUSINESS → TRUSTED_ACCESS → HUMAN_ONLY) in Lean sources (**proofs in progress**)
- Policy-versioned execution with content-addressed receipts (**shipped** for runtime gate decisions)

## NIST SP 800-218A (mapping table — implementation status)

| Practice | ProofOS status in this repo |
|----------|----------------------------|
| AM-1: Model Version Control and Provenance | Receipts content-addressed with canonical SHA-256 (**shipped** for gate decisions) |
| AM-2: Training Data Documentation | AI-BOM generator not vendored in this public mirror |
| AM-6: Vulnerability Management | Byzantine/SIFT roles specified in quorum.md; colony **not deployed** here |
| SC-3: Continuous Monitoring | Receipt chain for each ALLOW/DENY decision (**shipped**) |

## AI-BOM

AI Bill of Materials generation aligned with SP 800-218A is not shipped in this public mirror. Contact <scott@aevion.ai> for questions about separate tooling.

## Bibliography (citation only)

Vassilev, A. "Robust AI Security and Alignment: A Sisyphean Endeavor?" *IEEE Security & Privacy*, May 2026. DOI: `10.1109/MSEC.2026.3678214`.

Citation does not constitute endorsement of ProofOS by the author, IEEE, or NIST.
