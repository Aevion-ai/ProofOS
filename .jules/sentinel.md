## 2024-10-06 - Prevent CI arbitrary file write via manifest path traversal
**Vulnerability:** `mirror-from-monorepo.yml` read paths directly from `MIRROR_MANIFEST.md` and used `shutil.copy2`/`copytree` without verifying the path bounds, leading to potential path traversal and arbitrary file write.
**Learning:** Even internal configuration files like repository manifests used in CI workflows must be treated as untrusted data sources when parsing their values for file operations.
**Prevention:** Always strip leading slashes before concatenating paths, resolve paths, and validate bounds using `.is_relative_to()`. Explicitly reject the base root itself to prevent self-deletion and implement denylists for sensitive control-plane directories (`.git`, `.jules`).
