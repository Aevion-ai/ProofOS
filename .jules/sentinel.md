## 2024-05-18 - Path Traversal Vulnerability in Sync Script
**Vulnerability:** Path traversal vulnerability in `.github/workflows/mirror-from-monorepo.yml` allowing arbitrary source read and arbitrary destination write.
**Learning:** `Path(A) / B` is vulnerable to path traversal if `B` is not sanitized or checked, e.g., if `B` has `../` or is absolute. This bypasses directory bounds and can write to sensitive areas like `.git`.
**Prevention:** Always use `path.resolve()` and `is_relative_to()` when computing paths based on external config or inputs. Strip leading slashes to prevent absolute path override. Ensure the target path is strictly within the intended directory boundary.
