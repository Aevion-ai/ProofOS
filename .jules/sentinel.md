## 2024-09-24 - Path Traversal in CI Workflow
**Vulnerability:** Found path traversal vulnerability in `.github/workflows/mirror-from-monorepo.yml` python script where `dst` from `MIRROR_MANIFEST.md` is processed.
**Learning:** Hardcoded manifest parsing in CI can lead to path traversal if the manifest is manipulated to include leading slashes or `../`. This can overwrite system files or control-plane files like `.git`.
**Prevention:** Sanitize paths by stripping leading slashes, resolving paths, ensuring they are relative to the workspace root using `is_relative_to()`, explicitly rejecting the workspace root itself, and blocking sensitive control-plane directories like `.git` and `.jules` from being overwritten.
