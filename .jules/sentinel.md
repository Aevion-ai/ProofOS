## 2024-05-18 - CI Manifest Path Traversal
**Vulnerability:** The mirror workflow parsed `MIRROR_MANIFEST.md` and executed file operations without bounding the source and destination paths, allowing arbitrary read/write on the CI runner via path traversal.
**Learning:** Even internal configuration files used in CI workflows must be treated as untrusted data sources. Concatenating parsed values directly to base paths without resolution can allow sandbox escapes.
**Prevention:** Always strip leading slashes, resolve constructed paths, and use `pathlib.Path.is_relative_to()` to validate they remain within the intended base directory. Implement denylists for sensitive control-plane directories like `.git` and `.jules`, and reject exact matches to the base root to prevent self-deletion.
