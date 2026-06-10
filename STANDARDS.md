# Standards Alignment

## NIST AI Risk Management Framework

ProofOS aligns with NIST AI RMF 1.0 (AI 100-1) and the Secure Software Development Practices for Generative AI and Dual-Use Foundation Models community profile (SP 800-218A).

### Govern

- Constitutional halt gate enforces declared safety predicates before action execution
- Human gate escalation when automated guardrails disagree
- Open-obligation surface publishes every unproven proposition as a machine-readable gap list

### Map

- Receipt chain provides content-addressed audit trail for every system decision
- SHA-256 canonical serialization enables independent verification of any artifact
- Agent Counsel Colony performs continuous multi-agent review with Byzantine fault detection

### Measure

- ProofDB metrics: theorem count, proof density, sorry tracking, receipt chain validation
- Agent TTS (True-Thinking Score) monitoring across all 7 counsel agents
- Cross-architecture independent attestation via Pi 5 Sheriff (ARM64, different silicon)

### Manage

- Quorum Constitution defines explicit aggregation rules for multi-agent decisions
- Capability Access Separation enforces tiered deployment (PUBLIC → BUSINESS → TRUSTED_ACCESS → HUMAN_ONLY)
- Policy-versioned execution with content-addressed receipts

## NIST SP 800-218A

| Practice | Aevion Implementation |
|----------|----------------------|
| AM-1: Model Version Control and Provenance | ProofDB content-addressed storage with canonical SHA-256 |
| AM-2: Training Data Documentation | AI-BOM generation with content-addressed model artifacts |
| AM-6: Vulnerability Management | Byzantine adversarial agent + SIFT filtering as standing capability |
| SC-3: Continuous Monitoring | Receipt chain — every decision emits an auditable, re-derivable record |

## AI-BOM

ProofOS generates NIST SP 800-218A compliant AI Bills of Materials. Contact scott@aevion.ai for access to the generator and sample output.

## Primary citation

Vassilev, A. "Robust AI Security and Alignment: A Sisyphean Endeavor?" *IEEE Security & Privacy*, May 2026. DOI: `10.1109/MSEC.2026.3678214`.

---

NIST AI Consortium applicant — June 2026 review period.
