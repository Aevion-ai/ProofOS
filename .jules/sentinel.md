## 2026-08-30 - Prevent Path Traversal in Mirror Manifest
**Vulnerability:** The GitHub Actions mirror workflow (`mirror-from-monorepo.yml`) parsed `MIRROR_MANIFEST.md` and concatenated untrusted paths directly using `Path() / src` and `Path(dst)`. This could allow path traversal if the manifest contained absolute paths (e.g., `/etc/passwd`) or relative directory traversal (`../`).
**Learning:** In Python, concatenating an absolute path string via the `/` operator (e.g., `Path(base) / '/abs'`) evaluates to the absolute path itself, completely bypassing the intended base directory.
**Prevention:** Always strip leading slashes (e.g., using `.lstrip('/')`) before concatenating paths from untrusted input, resolve the constructed path using `.resolve()`, and validate it using `pathlib.Path.is_relative_to()` against the allowed base directory.

## 2026-08-30 - Prevent Root Deletion in Path Containment Checks
**Vulnerability:** Even when using `is_relative_to(base_dir)` to prevent path traversal, a destination path resolving exactly to `base_dir` (e.g., `./` or `/`) will pass the check, potentially leading to `shutil.rmtree(base_dir)` which deletes the entire repository. Protected internal directories like `.git` and `.github` also pass the containment check by construction.
**Learning:** `is_relative_to()` is a reflexive containment check (a directory is relative to itself). It only guarantees a path is not *above* or *outside* the base directory, not that it is strictly *inside* a safe subdirectory.
**Prevention:** Always add an explicit equality guard (`dst_path == base_dir`) and explicit denylist checks for protected subdirectories (like `.git`) before any destructive file operations based on untrusted input.
