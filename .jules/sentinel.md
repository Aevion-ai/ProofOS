## 2024-05-24 - [Title]
**Vulnerability:** [What you found]
**Learning:** [Why it existed]
**Prevention:** [How to avoid next time]

## 2024-05-24 - [Path Traversal in File Manifest Processing]
**Vulnerability:** The Python script embedded in the `.github/workflows/mirror-from-monorepo.yml` GitHub Action processed paths from an external manifest file (`MIRROR_MANIFEST.md`) without validating that the resulting path resolved inside the expected directory. Specifically, `src_path = Path(".monorepo") / src` could be manipulated by `src` containing absolute paths like `/etc/passwd` or parent traversals like `../../secret`.
**Learning:** Concatenating paths via `pathlib.Path` with untrusted input can easily bypass intended base directories because `Path(base) / '/abs'` evaluates directly to the absolute path `/abs`, completely ignoring the base directory. This is a common and dangerous footgun with `pathlib`.
**Prevention:** Always resolve the constructed path and explicitly validate that it is contained within the allowed base directory using `pathlib.Path.resolve().is_relative_to(base.resolve())` before performing any file operations.
