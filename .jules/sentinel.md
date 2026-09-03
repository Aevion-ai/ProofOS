## 2024-09-03 - Path Traversal in Mirror Workflow
**Vulnerability:** Inline Python script in .github/workflows/mirror-from-monorepo.yml concatenated unvalidated paths from MIRROR_MANIFEST.md, allowing absolute paths to override the base directory (`Path(base) / "/absolute" == Path("/absolute")`).
**Learning:** Python's `pathlib.Path` behaves unexpectedly with absolute paths, enabling path traversal and arbitrary file read/write vulnerabilities when parsing external or user-provided manifests.
**Prevention:** Always strip leading slashes with `.lstrip("/")`, resolve the path, and explicitly validate it with `is_relative_to()` against the base directory, excluding sensitive directories via denylists and the root path itself.
