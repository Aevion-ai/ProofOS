## 2026-09-12 - Path Traversal in Mirror Workflow
**Vulnerability:** The python script in `.github/workflows/mirror-from-monorepo.yml` blindly joined `Path(".monorepo")` with the `src` and `dst` paths from `MIRROR_MANIFEST.md`, allowing arbitrary file read/write if absolute paths or `../` were used.
**Learning:** Python's `pathlib.Path(base) / path` does not prevent path traversal if `path` is absolute (it drops the base) or uses `..`.
**Prevention:** Use `.lstrip('/')` on inputs, `.resolve()` on the combined path, and `.is_relative_to(base)` to ensure the path stays within bounds. Also explicitly reject if it resolves exactly to the base to avoid root deletion, and implement denylists for sensitive `.git`, `.github`, and `.jules` directories.
