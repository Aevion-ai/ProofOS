## 2024-05-24 - Path Traversal in Manifest Parsing
**Vulnerability:** The Python script within the .github/workflows/mirror-from-monorepo.yml file parses paths from MIRROR_MANIFEST.md without stripping leading slashes or validating the paths. It simply concatenates them: `Path(".monorepo") / src` and `Path(dst)`.
**Learning:** In Python's pathlib, if `src` is an absolute path string (starts with `/`), concatenating it to a Path object via the `/` operator overrides the base path completely, resulting in just the absolute path `src`. This allows an attacker who can modify `MIRROR_MANIFEST.md` in the monorepo to write files anywhere on the system during the mirror sync process.
**Prevention:** Always strip leading slashes from untrusted path inputs before concatenation (e.g., using `src.lstrip('/')`). Then, resolve the combined path and validate it against the intended base directory using `pathlib.Path.is_relative_to()`.

## 2024-05-24 - Root-Equality and Control Plane Vulnerabilities
**Vulnerability:** Path containment checks via `pathlib.Path.is_relative_to()` are reflexive, meaning a path is considered relative to itself. If an attacker crafts an input (like `/`, `.`, or `foo/..`) that resolves to the root checkout directory, `is_relative_to(base_dir)` evaluates to True. This allows `shutil.rmtree()` to catastrophically delete the entire repository checkout. Additionally, paths inside the containment boundary like `.git` or `.github/workflows` (the control plane) were not protected by boundary checks, allowing deletion of git history or the security workflow itself.
**Learning:** Containment checks are insufficient on their own; they only prevent traversing *out* of a boundary, but do not protect the boundary root itself or sensitive subdirectories *within* the boundary.
**Prevention:**
1. Always explicitly reject the boundary root itself (`if resolved_path == base_dir`) before performing destructive operations.
2. Implement an explicit denylist to protect control plane directories (e.g., `.git`, `.github`, `.jules`) that reside within the containment boundary.
