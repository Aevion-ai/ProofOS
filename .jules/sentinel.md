## 2026-07-22 - [Security Vulnerability Fixes in Dependencies]
**Vulnerability:** Playwright downloads and installs browsers without verifying the authenticity of the SSL certificate (<1.55.1). Minimatch has multiple ReDoS vulnerabilities in versions <9.0.7 (via @typescript-eslint/eslint-plugin).
**Learning:** Outdated dependencies expose the environment to significant security risks, even in test or build environments.
**Prevention:** Keep dependencies up to date, especially those related to browser automation and parsers, and periodically run `pnpm audit` to check for known CVEs in the dependency tree.
