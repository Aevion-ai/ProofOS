## 2026-06-30 - [Path Traversal in CI Sync Action]
**Vulnerability:** The mirror action parsed paths from `MIRROR_MANIFEST.md` and copied files without ensuring paths resolved securely.
**Learning:** Even internal markdown manifests are untrusted data boundaries when processed in CI automation.
**Prevention:** Always use `.resolve()` and `.is_relative_to()` to validate all source and destination paths against the monorepo submodule directory and the repo root respectively, and deny writes to sensitive paths like `.git` and `.jules`.
