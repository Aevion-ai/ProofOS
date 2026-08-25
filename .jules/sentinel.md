## 2026-08-25 - Path Traversal in Mirror Workflow
**Vulnerability:** The python script embedded in `.github/workflows/mirror-from-monorepo.yml` concatenates user-controlled paths from `MIRROR_MANIFEST.md` using `Path(".monorepo") / src` without sanitizing leading slashes or resolving paths. This allows path traversal and arbitrary file read/write (e.g. `src: /etc/passwd -> ...`).
**Learning:** Python's `pathlib.Path` concatenation with a string starting with a slash results in the absolute path, bypassing the base directory completely.
**Prevention:** Always strip leading slashes before concatenating paths (`.lstrip('/')`), resolve the resulting path, and validate it using `.is_relative_to(base_dir)`.
