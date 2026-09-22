## 2026-09-22 - Path Traversal Vulnerability in GitHub Actions mirror workflow
**Vulnerability:** The python script embedded in `.github/workflows/mirror-from-monorepo.yml` read paths from a manifest payload without validation, enabling path traversal during file writes.
**Learning:** `pathlib.Path` resolution does not automatically prevent path traversal. If the input contains a leading slash or traverses outside bounds, it can write anywhere.
**Prevention:** Always strip leading slashes and use `pathlib.Path.is_relative_to()` against the intended base directory, rejecting the root itself and denylisted directories.
