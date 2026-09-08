
## 2024-05-18 - [CRITICAL] Fix Path Traversal in Mirror Manifest Workflow
**Vulnerability:** The automated mirror workflow python script used `Path(".monorepo") / src` where `src` and `dst` were read from the unvalidated `MIRROR_MANIFEST.md`. Malicious PRs could introduce absolute paths (e.g. `/etc/passwd`) or relative traversal (e.g. `../../`) causing catastrophic self-deletion (e.g. overwriting `.git`) or arbitrary file read/write on the runner.
**Learning:** Python's `pathlib.Path` overrides the base path if the concatenated string is an absolute path. `is_relative_to` returns `True` for the root itself, requiring explicit checks against the base root to prevent self-deletion.
**Prevention:** Always strip leading slashes before path concatenation, resolve the constructed path, validate it against the base directory using `is_relative_to`, explicitly reject paths matching the base root, and implement denylists for sensitive control-plane directories like `.git` and `.github`.
