## 2025-02-13 - Path Traversal in pathlib.Path
**Vulnerability:** Path traversal vulnerability in Python workflow script when parsing untrusted manifest files.
**Learning:** Concatenating an absolute path string via `/` operator (e.g., `Path(base) / '/abs'`) will evaluate to the absolute path itself, bypassing the intended base directory.
**Prevention:** Always strip leading slashes (e.g., using `.lstrip('/')`) before concatenating, resolve the constructed path, and validate it using `pathlib.Path.is_relative_to()` against the allowed base directory.
