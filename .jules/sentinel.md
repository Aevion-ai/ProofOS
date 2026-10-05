## 2024-05-18 - [Fix Path Traversal in Mirror Workflow]
**Vulnerability:** The GitHub Actions workflow `mirror-from-monorepo.yml` read paths from `MIRROR_MANIFEST.md` and applied them directly to `Path()` and `shutil` operations without checking if they resolved outside intended directories.
**Learning:** Even internal configuration files used in CI workflows (like repo manifests) must be treated as untrusted data sources when parsed for file operations.
**Prevention:** Paths parsed from these files must always be bounded, stripped of leading slashes, resolved, and validated using `is_relative_to()` against the intended base directories, explicitly rejecting catastrophic self-deletion and denying sensitive control-plane paths.
