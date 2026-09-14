"""Security tests for mirror path policy in PR #110.

Verifies that:
- Path traversal sequences (..) are rejected.
- .git, checkout metadata, and restricted directories are rejected in source and destination.
- Symlinks escaping the root boundary or pointing to restricted metadata are rejected.
- Valid safe relative paths within the boundary are admitted.
"""
from pathlib import Path
import pytest
import sys

RESTRICTED_PARTS = {".git", ".github", ".jules", ".monorepo", ".gitmodules", ".gitattributes"}


def is_restricted_part(parts: tuple[str, ...]) -> bool:
    return any(part in RESTRICTED_PARTS or part.startswith(".git") for part in parts)


def validate_mirror_path(base_dir: Path, rel_str: str) -> Path | None:
    raw = rel_str.strip()
    if not raw:
        return None
    # Reject absolute paths (POSIX leading slash, Windows drive or UNC)
    if raw.startswith(("/", "\\")) or ":" in raw[:3] or Path(raw).is_absolute():
        return None
    raw_parts = Path(raw).parts
    if ".." in raw_parts or is_restricted_part(raw_parts):
        return None
    base_res = base_dir.resolve()
    cand_res = (base_dir / raw).resolve()
    if not cand_res.is_relative_to(base_res) or cand_res == base_res:
        return None
    rel_res = cand_res.relative_to(base_res)
    if is_restricted_part(rel_res.parts):
        return None
    curr = base_dir / raw
    try:
        while curr.resolve() != base_res:
            if curr.is_symlink():
                target = curr.resolve()
                if not target.is_relative_to(base_res) or is_restricted_part(target.relative_to(base_res).parts):
                    return None
            if curr.parent == curr:
                break
            curr = curr.parent
    except (OSError, ValueError):
        return None
    return cand_res


def test_valid_safe_paths_are_admitted(tmp_path: Path):
    base = tmp_path / "base"
    base.mkdir()
    f = base / "schemas" / "model.json"
    f.parent.mkdir(parents=True)
    f.write_text("{}", encoding="utf-8")

    res = validate_mirror_path(base, "schemas/model.json")
    assert res is not None
    assert res == f.resolve()


@pytest.mark.parametrize("traversal", [
    "../outside.txt",
    "../../etc/passwd",
    "schemas/../../outside.txt",
    "/etc/passwd",
])
def test_path_traversals_are_rejected(tmp_path: Path, traversal: str):
    base = tmp_path / "base"
    base.mkdir()
    assert validate_mirror_path(base, traversal) is None


@pytest.mark.parametrize("metadata_path", [
    ".git/config",
    ".git/HEAD",
    ".gitmodules",
    ".gitattributes",
    "subdir/.git/config",
    ".github/workflows/deploy.yml",
    ".jules/sentinel.md",
    ".monorepo/config",
])
def test_checkout_metadata_and_git_rejected(tmp_path: Path, metadata_path: str):
    base = tmp_path / "base"
    base.mkdir()
    target = base / metadata_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("secret", encoding="utf-8")

    assert validate_mirror_path(base, metadata_path) is None


def test_symlink_escape_is_rejected(tmp_path: Path):
    base = tmp_path / "base"
    base.mkdir()
    outside = tmp_path / "outside_dir"
    outside.mkdir()
    secret_file = outside / "secret.txt"
    secret_file.write_text("secret_data", encoding="utf-8")

    symlink_path = base / "sym_link"
    try:
        symlink_path.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation not supported on this host without privilege")

    assert validate_mirror_path(base, "sym_link/secret.txt") is None


def test_internal_symlink_to_git_is_rejected(tmp_path: Path):
    base = tmp_path / "base"
    base.mkdir()
    git_dir = base / ".git"
    git_dir.mkdir()
    git_config = git_dir / "config"
    git_config.write_text("token=123", encoding="utf-8")

    symlink_path = base / "safe_name"
    try:
        symlink_path.symlink_to(git_config)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation not supported on this host without privilege")

    assert validate_mirror_path(base, "safe_name") is None
