## 2024-10-25 - Path Traversal Vulnerability in CI Workflow
**Vulnerability:** The mirror synchronization workflow parsed file paths from MIRROR_MANIFEST.md without sanitization, allowing arbitrary path traversal.
**Learning:** Even internal configuration files used in CI workflows must be treated as untrusted data sources. Parsing raw paths without resolution and validation can lead to CI exploits via PRs.
**Prevention:** Always use `pathlib.Path.is_relative_to()` to validate that dynamically generated paths resolve strictly within their intended boundaries. Enforce denylists for sensitive control-plane directories like `.git`.
