## 2024-08-23 - Path Traversal in GitHub Actions Manifest Parser
**Vulnerability:** The Python script in mirror-from-monorepo.yml reads untrusted path mappings from MIRROR_MANIFEST.md and constructs paths like Path(".monorepo") / src. If src starts with a /, Path evaluates to the absolute path, allowing path traversal.
**Learning:** Concatenating paths with / when the right-hand side is an absolute path string discards the left-hand side base directory in Python's pathlib.
**Prevention:** Always strip leading slashes (e.g., .lstrip("/")) from untrusted inputs before concatenating them with a base path, and use .resolve().is_relative_to(base) to validate the resulting path remains within boundaries.
