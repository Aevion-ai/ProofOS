## 2026-08-24 - Path Traversal Vulnerability in Sync Script
**Vulnerability:** Path traversal in GitHub Actions sync script due to unsanitized paths from untrusted manifest files.
**Learning:** Concatenating absolute paths via `/` operator (e.g., `Path(base) / '/abs'`) evaluates to the absolute path, bypassing the base directory constraint. Unchecked manifest paths could write arbitrary files to the local file system.
**Prevention:** Always strip leading slashes before path concatenation (`lstrip('/')`), use `.resolve()`, and validate paths strictly against the allowed base directory with `is_relative_to()`.
