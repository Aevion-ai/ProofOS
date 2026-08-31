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

## 2024-05-24 - Source-Side Disclosure & Absolute Path Rejection
**Vulnerability:** A path traversal or manipulation on the source `src` side could lead to private-source disclosure (copying unexpected files out of a private monorepo into the public mirror). Furthermore, `persist-credentials: true` (default in checkout) allowed the `MONOREPO_MIRROR_TOKEN` to be silently persisted in `.monorepo/.git/config`, potentially allowing token exfiltration. Relying on `.lstrip('/')` for rewriting hostile absolute paths creates a new issue: security parsers should explicitly reject malformed security-relevant inputs, not attempt to "fix" them, as this can easily lead to bypass logic.
**Learning:** Destructive operations inside sync-loops must apply the exact same strict boundaries (absolute path rejection, root-equality prevention, control plane denylists) to both the `src` read target AND the `dst` write target. Access tokens MUST NOT be persisted into checkout boundaries that will be subsequently published.
**Prevention:**
1. Always add `persist-credentials: false` to GitHub Actions `actions/checkout` when downloading from private sources that are subsequently exposed or synced.
2. Abstract path validation logic into an importable python module.
3. Reject hostile input via `pathlib.Path.is_absolute()` rather than attempting to rewrite it, and reject it outright by returning early.
