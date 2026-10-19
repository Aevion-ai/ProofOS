## 2024-10-19 - Python Path Traversal Check
**Vulnerability:** Path Traversal
**Learning:** Python needs strict checks for directory boundaries
**Prevention:** Use `pathlib.Path.is_relative_to()` and verify it does not exactly match the root directory.
