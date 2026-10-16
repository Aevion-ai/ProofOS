## 2024-05-24 - CI Artifact Path Traversal
**Vulnerability:** The mirror workflow copies files based on `MIRROR_MANIFEST.md` without path traversal protections.
**Learning:** `shutil` operations on untrusted manifest files can overwrite arbitrary files via absolute paths or directory traversal (`../`).
**Prevention:** Always `lstrip('/')`, `resolve()`, and validate paths using `is_relative_to` against the base directory, explicit checking for base root equivalence to prevent self-deletion, and blocklisting control-plane directories like `.git` and `.jules`.
