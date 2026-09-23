## 2026-06-30 - Prevent Path Traversal in Mirror Workflows
**Vulnerability:** The mirror workflow used string concatenation without sanitization (`Path(".monorepo") / src`), which allowed path traversal vulnerabilities.
**Learning:** CI workflows parsing manifest files must strictly validate file paths. Using pathlib's `is_relative_to()` is necessary, but because it's reflexive, explicit checks must also reject exact root matches. A denylist is required for sensitive control-plane directories like `.git` and `.jules`.
**Prevention:** Always strip leading slashes before path construction, resolve the path, and enforce both boundary restrictions (`is_relative_to`) and targeted denylists for sensitive destinations.
