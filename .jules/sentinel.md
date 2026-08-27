## 2025-02-27 - Path Traversal in Manifest Parsing
**Vulnerability:** Path traversal in `mirror-from-monorepo.yml` via `MIRROR_MANIFEST.md` parsing, caused by concatenating absolute path strings or using `../` with `pathlib.Path`.
**Learning:** `Path(base) / '/abs'` evaluates to the absolute path `/abs`, bypassing the intended base directory.
**Prevention:** Always use `.lstrip('/')` on untrusted path input, call `.resolve()`, and validate with `.is_relative_to()` against the allowed base directory.
