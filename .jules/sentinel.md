## 2024-11-20 - Fix path traversal in GitHub Actions mirror workflow
**Vulnerability:** The mirror-from-monorepo.yml workflow reads paths from MIRROR_MANIFEST.md without validation, allowing path traversal (e.g., ../) and overwriting sensitive files (.git, .github) if a malicious actor compromised the monorepo.
**Learning:** When using Python within a GitHub Action to parse paths, naive `Path()` construction and concatenation are vulnerable to path traversal. You must resolve paths, enforce boundaries using `.is_relative_to()`, and strip leading slashes.
**Prevention:** Always use `.resolve()`, check `.is_relative_to(base_dir)`, ensure the path is not exactly the base dir, and explicitly denylist sensitive directories like `.git` and `.github`.
