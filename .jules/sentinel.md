## 2025-02-13 - Path Traversal in Mirror Workflow
**Vulnerability:** The `.github/workflows/mirror-from-monorepo.yml` workflow constructs `src_path = Path(".monorepo") / src` directly from paths extracted from `MIRROR_MANIFEST.md` via Regex. If a user inputs an absolute path like `/etc/passwd` or `../path`, it allows arbitrary read from the action runner filesystem, or arbitrary write when constructing `dst_path`.
**Learning:** `pathlib.Path(base) / path` where `path` is an absolute string (like `"/etc/passwd"`) will discard `base` and evaluate to `"/etc/passwd"`.
**Prevention:** Always validate that paths constructed from untrusted text inputs evaluate to paths within the expected base directory using `resolve()` and `is_relative_to()`.
