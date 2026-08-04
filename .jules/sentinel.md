## 2026-08-04 - Path Traversal via pathlib.Path
**Vulnerability:** Path traversal possible when concatenating untrusted absolute paths using pathlib.Path (e.g. `Path(base) / '/abs'` evaluates to `/abs`).
**Learning:** Python's pathlib operator `/` ignores the left operand if the right operand is an absolute path, bypassing intended directory boundaries.
**Prevention:** Always resolve() constructed paths and validate them using `.is_relative_to(allowed_base)`.
