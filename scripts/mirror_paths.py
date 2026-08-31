"""Path admission guard for the monorepo mirror workflow.

The mirror workflow copies an allow-listed subset of the **private** monorepo
into this **public** repository and then commits and pushes the result. Any
source path that escapes the allow-list is therefore a private-source
disclosure, not merely a traversal, so admission is decided here and the
workflow calls into this module rather than inlining a copy of the rules.

Every rejection is returned as an explicit reason string; a caller that gets a
``None`` path must not copy anything.
"""

from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Optional, Tuple

# Control-plane directories that may never be written in the mirror checkout.
PROTECTED_DST_ROOTS = frozenset({".git", ".github", ".jules"})

# Reading the monorepo's git directory would expose remote credentials and the
# full private history.
PROTECTED_SRC_ROOTS = frozenset({".git"})

Decision = Tuple[Optional[Path], Optional[str]]


def is_absolute_request(raw: str) -> bool:
    """Report whether ``raw`` asks for an absolute location under any syntax.

    Both POSIX and Windows forms are considered so that the answer does not
    depend on which platform evaluates the manifest.
    """
    if raw.startswith(("/", "\\")):
        return True
    return PurePosixPath(raw).is_absolute() or PureWindowsPath(raw).is_absolute()


def _resolve_within(raw: str, base_dir: Path) -> Decision:
    """Resolve ``raw`` under ``base_dir``, rejecting anything not strictly inside."""
    candidate = raw.strip()

    if not candidate:
        return None, "empty path"

    # An absolute request is rejected outright rather than rewritten into a
    # relative one: a security parser must not reinterpret an invalid request
    # as a different valid request.
    if is_absolute_request(candidate):
        return None, f"absolute path not permitted: {raw}"

    resolved = (base_dir / candidate).resolve()

    # The base directory itself is never a legal target: it is how `.`, `./`,
    # `foo/..` and friends smuggle the whole tree past a containment check that
    # is reflexive.
    if resolved == base_dir:
        return None, f"path resolves to the base directory: {raw}"

    if not resolved.is_relative_to(base_dir):
        return None, f"path escapes the base directory: {raw}"

    return resolved, None


def resolve_src(raw: str, base_src_dir: Path) -> Decision:
    """Admit a manifest source path inside the private monorepo checkout."""
    base_src_dir = Path(base_src_dir).resolve()
    resolved, reason = _resolve_within(raw, base_src_dir)
    if resolved is None:
        return None, reason

    if resolved.relative_to(base_src_dir).parts[0] in PROTECTED_SRC_ROOTS:
        return None, f"source targets protected path: {raw}"

    return resolved, None


def resolve_dst(raw: str, base_dst_dir: Path, base_src_dir: Path) -> Decision:
    """Admit a manifest destination path inside the public mirror checkout."""
    base_dst_dir = Path(base_dst_dir).resolve()
    base_src_dir = Path(base_src_dir).resolve()
    resolved, reason = _resolve_within(raw, base_dst_dir)
    if resolved is None:
        return None, reason

    # The monorepo checkout lives inside the mirror checkout, so containment
    # alone does not exclude it.
    if resolved.is_relative_to(base_src_dir):
        return None, f"destination targets the monorepo checkout: {raw}"

    if resolved.relative_to(base_dst_dir).parts[0] in PROTECTED_DST_ROOTS:
        return None, f"destination targets protected path: {raw}"

    return resolved, None
