## 2025-01-14 - Path Traversal in Mirror Workflow
**Vulnerability:** The mirror-from-monorepo.yml workflow constructs file paths by directly concatenating user-provided inputs (src and dst) from MIRROR_MANIFEST.md without validation.
**Learning:** Python's Path object allows absolute path overrides if the joined string has a leading slash, and .. components can escape the base directory, allowing reads/writes outside intended bounds.
**Prevention:** Always strip leading slashes with .lstrip('/') before concatenation, resolve paths with .resolve(), and validate bounds using .is_relative_to() while explicitly checking against the base path to prevent self-deletion. Use denylists for sensitive directories like .git.
