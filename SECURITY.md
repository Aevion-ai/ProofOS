# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, please report it responsibly.

**Do not open a public issue.** Instead, email security concerns to the repository maintainers via GitHub's private vulnerability reporting feature, or contact the maintainers directly through the channels listed on the organization profile.

We will acknowledge receipt within 48 hours and provide a timeline for resolution.

## Multirepo findings

Org-wide Snyk items (Next.js EOL, `exec` in `agentic_reasoning_engine.py`, pickle in
`optimized_semantic_similarity.py`, vetproof.ai CSP, Docker root user, etc.) are triaged in
`docs/ops/security_remediation_queue_multirepo_v0.1.md`. Most Critical rows apply to **other**
Aevion repositories, not this proof corpus.

## Scope

This policy covers:

- Source code in this repository
- CI/CD workflow configurations
- Published packages and artifacts
- Documentation that may inadvertently expose sensitive information

## Expectations

- We treat all committed secrets as compromised and rotate them immediately.
- We do not store credentials, API keys, private keys, or tokens in this repository.
- Test fixtures use synthetic data only.
- The `.gitignore` and `.gitattributes` files are configured to prevent accidental inclusion of sensitive files.

## Supported Versions

Only the latest version on the default branch (`main`) is actively maintained. Security patches for older releases are provided on a best-effort basis.
