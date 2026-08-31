"""Negative and positive matrix for the mirror workflow's path admission guard.

These tests import the shipped module that
``.github/workflows/mirror-from-monorepo.yml`` calls, so the suite cannot pass
while the workflow diverges.
"""

import pytest

from scripts.mirror_paths import resolve_dst, resolve_src

# Forms that collapse to the base directory itself, which would copy or
# overwrite an entire tree.
ROOT_FORMS = ["/", ".", "./", "//", "foo/..", "./foo/..", "a/b/../.."]

ABSOLUTE_FORMS = ["/etc/passwd", "/", "//etc/passwd", "/.git/config"]

ESCAPE_FORMS = ["..", "../outside", "a/../../outside"]


@pytest.fixture
def dirs(tmp_path):
    base_dst_dir = tmp_path.resolve()
    base_src_dir = (base_dst_dir / ".monorepo").resolve()
    base_src_dir.mkdir()
    return base_dst_dir, base_src_dir


def test_workflow_imports_the_guard():
    """The guard is only meaningful if the shipped workflow calls it."""
    from pathlib import Path

    workflow = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "mirror-from-monorepo.yml"
    text = workflow.read_text(encoding="utf-8")
    assert "from scripts.mirror_paths import resolve_dst, resolve_src" in text
    assert "persist-credentials: false" in text


# --------------------------------------------------------------------------
# Source side: the monorepo is private, so an over-broad source is disclosure.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("bad_src", ROOT_FORMS + ABSOLUTE_FORMS + ESCAPE_FORMS + [
    ".git",
    ".git/config",
    "./.git/config",
    ".git/refs/heads/main",
    "",
    "   ",
])
def test_rejects_malicious_sources(dirs, bad_src):
    _, base_src = dirs
    path, reason = resolve_src(bad_src, base_src)
    assert path is None
    assert reason


@pytest.mark.parametrize("good_src", [
    "requirements.txt",
    "pyproject.toml",
    "lean/Aevion/SBIR",
    "schemas/proofos_model_access_envelope.schema.json",
    ".github/workflows/ci.yml",  # readable in the source; the dst guard decides where it lands
    "docs/../docs/index.md",
])
def test_allows_legitimate_sources(dirs, good_src):
    _, base_src = dirs
    path, reason = resolve_src(good_src, base_src)
    assert reason is None
    assert path is not None
    assert path.is_relative_to(base_src)
    assert path != base_src


# --------------------------------------------------------------------------
# Destination side.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("bad_dst", ROOT_FORMS + ABSOLUTE_FORMS + ESCAPE_FORMS + [
    ".git",
    ".git/config",
    ".github",
    ".github/workflows",
    ".github/workflows/mirror-from-monorepo.yml",
    ".jules",
    ".jules/sentinel.md",
    ".monorepo",
    ".monorepo/secrets",
    "./.monorepo/x",
    "",
    "   ",
])
def test_rejects_malicious_destinations(dirs, bad_dst):
    base_dst, base_src = dirs
    path, reason = resolve_dst(bad_dst, base_dst, base_src)
    assert path is None
    assert reason


@pytest.mark.parametrize("good_dst", [
    "docs",
    "requirements.txt",
    "pyproject.toml",
    "lean/Aevion/SBIR",
    "schemas/model_access_envelope.schema.json",
    "docs/../docs/index.md",
    ".gitignore",  # a dotfile, not the .git directory
])
def test_allows_legitimate_destinations(dirs, good_dst):
    base_dst, base_src = dirs
    path, reason = resolve_dst(good_dst, base_dst, base_src)
    assert reason is None
    assert path is not None
    assert path.is_relative_to(base_dst)
    assert not path.is_relative_to(base_src)
    assert path != base_dst


def test_manifest_entries_are_all_admitted(dirs):
    """Every path in the committed manifest must survive both guards."""
    import re
    from pathlib import Path

    base_dst, base_src = dirs
    manifest = (Path(__file__).resolve().parents[1] / "MIRROR_MANIFEST.md").read_text(encoding="utf-8")
    entries = re.findall(r"^\s*src:\s*(.+?)\s*->\s*(.+?)\s*$", manifest, flags=re.MULTILINE)
    assert entries, "manifest contains no path map entries"

    for src, dst in entries:
        assert resolve_src(src, base_src)[0] is not None, src
        assert resolve_dst(dst, base_dst, base_src)[0] is not None, dst
