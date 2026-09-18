## 2026-09-18 - [Path Traversal in Mirror Workflow]
**Vulnerability:** The python script in `mirror-from-monorepo.yml` uses `Path(dst)` directly from the `MIRROR_MANIFEST.md` without validation. This allows writing to arbitrary locations (like `.git/config` or outside the workspace via `../`).
**Learning:** In automated synchronization tasks, manifest paths must be treated as untrusted input. `pathlib.Path` resolution does not natively prevent traversal or absolute path overrides without explicit checks.
**Prevention:** Always strip leading slashes, resolve paths, and validate using `.is_relative_to()` against the workspace root. Additionally, explicitly deny overwriting the root directory itself or control-plane directories like `.git` and `.github`.
