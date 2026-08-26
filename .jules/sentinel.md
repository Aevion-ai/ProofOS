## 2024-05-24 - Path Traversal in Mirror Workflow
**Vulnerability:** Path traversal and arbitrary file read/write in `.github/workflows/mirror-from-monorepo.yml` via manifest parsing.
**Learning:** `pathlib.Path(base) / abs_path` evaluates to `abs_path`. Untrusted paths must have leading slashes stripped and be resolved before validation.
**Prevention:** Always strip leading slashes before concatenating paths, use `.resolve()`, and validate with `.is_relative_to(base)`.
