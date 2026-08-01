## 2024-08-01 - Path Traversal in Mirror Workflow
**Vulnerability:** Path traversal in `.github/workflows/mirror-from-monorepo.yml` where untrusted paths from `MIRROR_MANIFEST.md` were directly joined using `pathlib.Path() / untrusted_string`.
**Learning:** When `untrusted_string` is an absolute path (e.g., `/etc/passwd`), `Path(base) / untrusted_string` evaluates to the absolute path itself, bypassing the intended `base` directory entirely.
**Prevention:** Always resolve the constructed path and validate it against the allowed base directory using `pathlib.Path.resolve().is_relative_to(base.resolve())` to prevent traversal and absolute path bypasses.
