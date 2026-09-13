"""Path resolution and copy guards for the public mirror workflow.

The mirror workflow is the only mechanism that moves content from the private
monorepo into this public repository. Every rule enforced here exists because a
mirror path is attacker-controllable: the manifest is a file in this repository,
so a malicious or mistaken manifest edit must not be able to read arbitrary
files out of the monorepo checkout, nor plant content into this repository's
governance surfaces.

Three layers of defence:

1. ``resolve_src`` / ``resolve_dst`` constrain where a mapping may point before
   anything is touched on disk.
2. ``validate_source_tree`` inspects the CONTENTS of an admitted source tree,
   so a nested ``.git`` directory, a symlink, or a credential-shaped file
   inside an otherwise allowed directory cannot be mirrored.
3. ``copy_source_tree`` validates first and only then mutates the destination,
   so a rejected mapping leaves the published tree exactly as it was.
"""

from __future__ import annotations

import fnmatch
import os
import pathlib
import shutil

# Names that are credential-bearing by shape. Any file or directory with one of
# these names is refused regardless of where in the source tree it sits, because
# the mirror allow-list governs directories and cannot vouch for every entry
# that appears inside them.
CREDENTIAL_FILE_PATTERNS: tuple[str, ...] = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "id_rsa*",
    "credentials.json",
    ".git-credentials",
)


def _is_credential_shaped(name: str) -> bool:
    """Return True when *name* is a credential-bearing file or directory name.

    Matched case-insensitively: on case-insensitive filesystems ``.ENV`` and
    ``.env`` are the same file, so a case-sensitive check would be a bypass.
    """
    lowered = name.lower()
    return any(fnmatch.fnmatch(lowered, pattern) for pattern in CREDENTIAL_FILE_PATTERNS)


def resolve_src(raw: str, base_src_dir: pathlib.Path) -> tuple[pathlib.Path | None, str | None]:
    """Resolve a manifest source path against the monorepo checkout root."""
    if not raw.strip():
        return None, "empty source path"

    path_obj = pathlib.Path(raw)
    if path_obj.is_absolute():
        return None, f"absolute source path rejected: {raw}"

    source_candidate = base_src_dir / path_obj
    if source_candidate.is_symlink():
        return None, f"source symlink rejected: {raw}"

    src_path = source_candidate.resolve()

    if src_path == base_src_dir:
        return None, f"source resolves to checkout root: {raw}"

    if not src_path.is_relative_to(base_src_dir):
        return None, f"source path traversal detected: {raw}"

    if ".git" in src_path.relative_to(base_src_dir).parts:
        return None, f"source targets protected path: {raw}"

    return src_path, None


def validate_source_tree(src_path: pathlib.Path) -> str | None:
    """Reject source trees whose copy would expose metadata or credentials.

    Returns ``None`` when the tree is safe to copy, otherwise a human-readable
    reason. A symlinked root, any ``.git`` entry at any depth, any symlink at
    any depth, and any credential-shaped name are all refused.
    """
    if src_path.is_symlink():
        return f"source symlink rejected: {src_path}"

    if _is_credential_shaped(src_path.name):
        return f"source matches credential-shaped path: {src_path}"

    if not src_path.is_dir():
        return None

    for root, dirs, files in os.walk(src_path, followlinks=False):
        for name in dirs + files:
            candidate = pathlib.Path(root) / name
            if name == ".git":
                return f"source targets protected path: {candidate}"
            if candidate.is_symlink():
                return f"source tree contains symlink: {candidate}"
            if _is_credential_shaped(name):
                return f"source tree contains credential-shaped file: {candidate}"

    return None


def copy_source_tree(src_path: pathlib.Path, dst_path: pathlib.Path) -> str | None:
    """Copy an admitted source tree, leaving the destination untouched on rejection.

    Validation happens before any destination mutation, so a refused mapping can
    never leave a half-written or deleted published path behind.
    """
    reason = validate_source_tree(src_path)
    if reason:
        return reason

    if dst_path.exists():
        shutil.rmtree(dst_path) if dst_path.is_dir() else dst_path.unlink()
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    if src_path.is_dir():
        shutil.copytree(src_path, dst_path)
    else:
        shutil.copy2(src_path, dst_path)

    return None


def resolve_dst(raw: str, base_dst_dir: pathlib.Path, base_src_dir: pathlib.Path) -> tuple[pathlib.Path | None, str | None]:
    """Resolve a manifest destination path against this repository's root."""
    if not raw.strip():
        return None, "empty destination path"

    path_obj = pathlib.Path(raw)
    if path_obj.is_absolute():
        return None, f"absolute destination path rejected: {raw}"

    dst_path = (base_dst_dir / path_obj).resolve()

    if dst_path == base_dst_dir:
        return None, f"destination resolves to checkout root: {raw}"

    if not dst_path.is_relative_to(base_dst_dir) or dst_path.is_relative_to(base_src_dir):
        return None, f"destination path traversal detected: {raw}"

    protected = {".git", ".github", ".jules"}
    if dst_path.relative_to(base_dst_dir).parts[0] in protected:
        return None, f"destination targets protected path: {raw}"

    return dst_path, None
