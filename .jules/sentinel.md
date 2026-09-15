## 2024-05-18 - Path Traversal in Sync Workflow
**Vulnerability:** The `.github/workflows/mirror-from-monorepo.yml` script copies files from a monorepo submodule to paths dictated by `MIRROR_MANIFEST.md` without validation.
**Learning:** The Python `Path(dst)` constructor implicitly accepts absolute paths and `../` sequences. A malicious modification to the manifest could override CI configurations (e.g. `.git/config`) or delete root components.
**Prevention:** Strip leading slashes from paths (`lstrip('/')`), use `resolve()` and `.is_relative_to(base)` to enforce boundaries, and block specific sensitive directories via a denylist.
