## 2024-09-04 - Path traversal in mirror workflow

**Vulnerability:** The `mirror-from-monorepo.yml` workflow parses `MIRROR_MANIFEST.md` and uses `Path` to construct source and destination paths without verifying they are relative to the repository directories, allowing an attacker to override files outside the intended scope (e.g., using absolute paths like `/etc/passwd` or traversing with `../`).
**Learning:** Python's `pathlib.Path` concatenating absolute paths (`base / "/etc"`) evaluates to the absolute path, bypassing intended path construction constraints.
**Prevention:** Always strip leading slashes (`lstrip('/')`) and validate paths using `Path.is_relative_to(base_dir)`. Furthermore, ensure destination paths don't target sensitive areas by implementing a denylist for directories like `.git`, `.github`, and `.jules`.
