## 2024-10-15 - Prevent path traversal in mirror manifest sync

**Vulnerability:** The CI workflow parsing `MIRROR_MANIFEST.md` constructs file paths directly from untrusted input without validation, allowing path traversal (e.g., `../../.git/config` or `/etc/passwd`) which could lead to arbitrary read/write or self-deletion within the CI runner.
**Learning:** Even internal configuration files mapped in CI must be treated as untrusted data. Path traversal checks must account for absolute path overrides and explicitly prevent operations on the base directory or sensitive control plane folders like `.git` and `.jules`.
**Prevention:** Always strip leading slashes before path concatenation, resolve the path, and use `pathlib.Path.is_relative_to()` combined with an explicit check to reject the root itself and denylist sensitive directories.
