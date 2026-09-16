"""Path admission guard for the monorepo mirror workflow.

The mirror workflow copies an allow-listed subset of the **private** monorepo
into this **public** repository and then commits and pushes the result. Any
source path that escapes the allow-list is therefore a private-source
disclosure, not merely a traversal, so admission is decided here and the
workflow calls into this module rather than inlining an unchecked copy of the rules.

Every rejection is returned as an explicit reason string; a caller that gets a
``None`` path must not copy anything.
"""

from pathlib import Path, PureWindowsPath
from typing import Optional, Tuple

# Control-plane directories that may never be written in the mirror checkout
# or read from the monorepo checkout.
PROTECTED_CONTROL_PLANE = frozenset({".git", ".github", ".jules", ".monorepo"})

Decision = Tuple[Optional[Path], Optional[str]]


def is_absolute_request(raw: str) -> bool:
    """Report whether ``raw`` asks for an absolute location under any syntax.

    Both POSIX and Windows forms (including drive letters and UNC paths)
    are considered so that the answer does not depend on which platform evaluates
    the manifest.
    """
    return raw.startswith(("/", "\\")) or PureWindowsPath(raw).is_absolute()


def _resolve_within(raw: str, base_dir: Path) -> Decision:
    """Resolve ``raw`` under ``base_dir``, rejecting anything not strictly inside."""
    candidate = raw.strip()

    if not candidate:
        return None, "FAIL: EMPTY_PATH"

    # An absolute request is rejected outright rather than rewritten into a
    # relative one: a security parser must not reinterpret an invalid request
    # as a different valid request.
    if is_absolute_request(candidate):
        return None, f"FAIL: ABSOLUTE_PATH_NOT_PERMITTED: {raw}"

    resolved = (base_dir / candidate).resolve()

    # The base directory itself is never a legal target: it is how `.`, `./`,
    # `foo/..` and friends smuggle the whole tree past a containment check that
    # is reflexive.
    if resolved == base_dir:
        return None, f"FAIL: ROOT_TARGET_NOT_PERMITTED: {raw}"

    if not resolved.is_relative_to(base_dir):
        return None, f"FAIL: PATH_TRAVERSAL_NOT_PERMITTED: {raw}"

    return resolved, None


def resolve_src(raw: str, base_src_dir: Path) -> Decision:
    """Admit a manifest source path inside the private monorepo checkout."""
    base_src_dir = Path(base_src_dir).resolve()
    resolved, reason = _resolve_within(raw, base_src_dir)
    if resolved is None:
        return None, reason

    rel_parts = resolved.relative_to(base_src_dir).parts
    if any(p in PROTECTED_CONTROL_PLANE for p in rel_parts):
        return None, f"FAIL: CONTROL_PLANE_TARGET_NOT_PERMITTED: {raw}"

    return resolved, None


def resolve_dst(raw: str, base_dst_dir: Path, base_src_dir: Optional[Path] = None) -> Decision:
    """Admit a manifest destination path inside the public mirror checkout."""
    base_dst_dir = Path(base_dst_dir).resolve()

    # Reject if destination or any ancestor in the relative path is a symlink.
    # We inspect this *before* _resolve_within so that an escaping symlink
    # correctly returns SYMLINK_DESTINATION_NOT_PERMITTED rather than a generic
    # PATH_TRAVERSAL_NOT_PERMITTED.
    candidate = raw.strip()
    if candidate and not is_absolute_request(candidate):
        current = base_dst_dir
        for part in Path(candidate).parts:
            if part == '..':
                current = current.parent
            elif part != '.':
                current = current / part
                if current.is_symlink():
                    return None, f"FAIL: SYMLINK_DESTINATION_NOT_PERMITTED: {raw}"

    resolved, reason = _resolve_within(raw, base_dst_dir)
    if resolved is None:
        return None, reason

    # The monorepo checkout lives inside the mirror checkout, so containment
    # alone does not exclude it.
    if base_src_dir is not None:
        base_src_dir = Path(base_src_dir).resolve()
        if resolved.is_relative_to(base_src_dir):
            return None, f"FAIL: DESTINATION_TARGETS_SOURCE_CHECKOUT: {raw}"

    rel_parts = resolved.relative_to(base_dst_dir).parts
    if any(p in PROTECTED_CONTROL_PLANE for p in rel_parts):
        return None, f"FAIL: CONTROL_PLANE_TARGET_NOT_PERMITTED: {raw}"

    return resolved, None
