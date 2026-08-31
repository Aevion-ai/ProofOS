from pathlib import Path

import pytest


def is_allowed_dst(dst: str, base_dst_dir: Path, base_src_dir: Path) -> bool:
    """Mirrors the destination path validation logic from the GitHub Action."""
    dst_clean = dst.strip().lstrip("/")
    dst_path = (base_dst_dir / dst_clean).resolve()

    # 1. Reject the root itself
    if dst_path == base_dst_dir:
        return False

    # 2. Containment checks
    if not dst_path.is_relative_to(base_dst_dir) or dst_path.is_relative_to(base_src_dir):
        return False

    # 3. Protect control plane
    PROTECTED = {".git", ".github", ".jules"}
    return dst_path.relative_to(base_dst_dir).parts[0] not in PROTECTED

@pytest.fixture
def dirs(tmp_path):
    base_dst_dir = tmp_path.resolve()
    base_src_dir = (base_dst_dir / ".monorepo").resolve()
    base_src_dir.mkdir()
    return base_dst_dir, base_src_dir

@pytest.mark.parametrize("malicious_dst", [
    "/",
    ".",
    "./",
    "//",
    "foo/..",
    "./foo/..",
    ".git",
    ".github/workflows",
    "a/../..",
    ".monorepo",
])
def test_rejects_malicious_destinations(dirs, malicious_dst):
    base_dst, base_src = dirs
    assert is_allowed_dst(malicious_dst, base_dst, base_src) is False

def test_allows_valid_destination(dirs):
    base_dst, base_src = dirs
    assert is_allowed_dst("docs", base_dst, base_src) is True
