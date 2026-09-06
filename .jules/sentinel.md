## 2024-05-24 - [Fix Path Traversal in Mirror Workflow]
**Vulnerability:** The `mirror-from-monorepo.yml` workflow blindly joins `src` and `dst` paths from `MIRROR_MANIFEST.md` without bounds checking, allowing an attacker to escape the workspace and overwrite sensitive files (e.g. `.git`, `.github`).
**Learning:** Python's `Path` joining does not prevent absolute path overrides or `../` escapes automatically; explicit validation is required.
**Prevention:** Always strip leading slashes from user-controlled paths, resolve them, and validate using `is_relative_to` against the intended base directory. Explicitly deny exact root matches and sensitive control directories.
