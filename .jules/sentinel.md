## 2024-08-06 - Path Traversal via Path(/) override
**Vulnerability:** Path traversal in GitHub Actions workflow python script parsing MIRROR_MANIFEST.md.
**Learning:** Python's pathlib Path(base) / '/abs/path' evaluates to '/abs/path', ignoring the base directory.
**Prevention:** Always resolve() constructed paths and validate them against the allowed base directory using is_relative_to().
