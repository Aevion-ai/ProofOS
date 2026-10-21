## 2024-10-21 - Critical Path Traversal in Mirror Workflow
**Vulnerability:** The `mirror-from-monorepo.yml` Python script parsed paths directly from `MIRROR_MANIFEST.md` using `Path(dst)` without validation. This allowed an attacker to overwrite arbitrary paths via absolute paths or `../` traversal.
**Learning:** Even internal metadata files (like manifests) must be treated as untrusted data. Path traversal checks are necessary on dynamically resolved workflow configurations.
**Prevention:** Always strip leading slashes before joining (`lstrip("/")`), fully `.resolve()` constructed paths, validate boundaries with `.is_relative_to()`, and explicitly deny writing to sensitive directories like `.git` or `.jules`.
