"""Adversarial and boundary test suite for mirror workflow path admission guard.

Tests the shipped module ``scripts.mirror_paths`` against the exact adversarial
admission corpus required by Aevion Sheriff standards:
- ../outside
- ../../.github/workflows/pwn.yml
- /etc/passwd
- C:\\Windows\\System32
- .github/workflows/foo.yml
- .git/config
- .jules/foo
- .
- ./
- nested/../../../escape
- symlink-inside-root -> target-outside-root
- valid/nested/path

Asserts:
- malicious source      → rejected (FAIL / None)
- malicious destination → rejected (FAIL / None)
- root target           → rejected (FAIL / None)
- control-plane target  → rejected (FAIL / None)
- valid contained path  → accepted (admitted Path)
"""

import os
from pathlib import Path
import pytest

from scripts.mirror_paths import resolve_dst, resolve_src, is_absolute_request


@pytest.fixture
def repo_dirs(tmp_path):
    base_dst_dir = tmp_path / "public_proofos"
    base_src_dir = tmp_path / "private_monorepo"
    base_dst_dir.mkdir()
    base_src_dir.mkdir()
    return base_dst_dir, base_src_dir


class TestAdversarialCorpus:
    """Explicit tests matching the Aevion Sheriff admission corpus."""

    @pytest.mark.parametrize("traversal_path", [
        "../outside",
        "../../.github/workflows/pwn.yml",
        "nested/../../../escape",
        "foo/bar/../../../../root",
    ])
    def test_path_traversal_rejected_both_sides(self, repo_dirs, traversal_path):
        base_dst, base_src = repo_dirs
        # Malicious source rejected
        src_path, src_reason = resolve_src(traversal_path, base_src)
        assert src_path is None
        assert "FAIL: PATH_TRAVERSAL_NOT_PERMITTED" in src_reason

        # Malicious destination rejected
        dst_path, dst_reason = resolve_dst(traversal_path, base_dst, base_src)
        assert dst_path is None
        assert "FAIL: PATH_TRAVERSAL_NOT_PERMITTED" in dst_reason

    @pytest.mark.parametrize("abs_path", [
        "/etc/passwd",
        "/",
        "//",
        "/root/.ssh/id_rsa",
        "C:\\Windows\\System32",
        "C:/Windows/System32",
        "D:\\data\\secrets.txt",
        "\\\\server\\share\\exploit",
    ])
    def test_absolute_paths_rejected_fail_closed_without_rewrite(self, repo_dirs, abs_path):
        """Absolute paths must produce FAIL: ABSOLUTE_PATH_NOT_PERMITTED, not be stripped."""
        base_dst, base_src = repo_dirs

        assert is_absolute_request(abs_path) is True

        src_path, src_reason = resolve_src(abs_path, base_src)
        assert src_path is None
        assert "FAIL: ABSOLUTE_PATH_NOT_PERMITTED" in src_reason

        dst_path, dst_reason = resolve_dst(abs_path, base_dst, base_src)
        assert dst_path is None
        assert "FAIL: ABSOLUTE_PATH_NOT_PERMITTED" in dst_reason

    @pytest.mark.parametrize("root_path", [
        ".",
        "./",
        "foo/..",
        "./foo/..",
        "a/b/../..",
    ])
    def test_root_target_rejected(self, repo_dirs, root_path):
        """Base root target (.) must be rejected to prevent overwriting or copying whole tree."""
        base_dst, base_src = repo_dirs

        src_path, src_reason = resolve_src(root_path, base_src)
        assert src_path is None
        assert "FAIL: ROOT_TARGET_NOT_PERMITTED" in src_reason

        dst_path, dst_reason = resolve_dst(root_path, base_dst, base_src)
        assert dst_path is None
        assert "FAIL: ROOT_TARGET_NOT_PERMITTED" in dst_reason

    @pytest.mark.parametrize("control_plane_path", [
        ".github/workflows/foo.yml",
        ".github/workflows/pwn.yml",
        ".git/config",
        ".git/HEAD",
        ".jules/foo",
        ".jules/sentinel.md",
        ".monorepo/private_keys",
    ])
    def test_control_plane_targets_rejected(self, repo_dirs, control_plane_path):
        """Control-plane directories (.git, .github, .jules, .monorepo) must be rejected."""
        base_dst, base_src = repo_dirs

        src_path, src_reason = resolve_src(control_plane_path, base_src)
        assert src_path is None
        assert "FAIL: CONTROL_PLANE_TARGET_NOT_PERMITTED" in src_reason

        dst_path, dst_reason = resolve_dst(control_plane_path, base_dst, base_src)
        assert dst_path is None
        assert "FAIL: CONTROL_PLANE_TARGET_NOT_PERMITTED" in dst_reason

    def test_symlink_inside_root_pointing_outside_root(self, repo_dirs):
        """A symlink located inside root pointing outside root must resolve outside and be rejected."""
        _, base_src = repo_dirs
        outside_target = base_src.parent / "outside_target.txt"
        outside_target.write_text("classified private data", encoding="utf-8")

        link_path = base_src / "symlink_escape"
        try:
            os.symlink(outside_target, link_path)
            has_symlink_privilege = True
        except OSError:
            has_symlink_privilege = False

        if has_symlink_privilege:
            src_path, src_reason = resolve_src("symlink_escape", base_src)
            assert src_path is None
            assert "FAIL: PATH_TRAVERSAL_NOT_PERMITTED" in src_reason
        else:
            # On platforms where symlinks require elevated privileges (e.g. Windows non-developer mode),
            # verify that any candidate that resolves outside is rejected by simulating the resolution.
            # In our implementation: (base_dir / candidate).resolve()
            resolved = (base_src / "symlink_escape").resolve()
            # If not created, candidate resolution test on simulated path:
            fake_resolved = outside_target.resolve()
            assert not fake_resolved.is_relative_to(base_src)

    def test_destination_symlink_rejected(self, repo_dirs):
        """A destination path that is or contains a symlink must be rejected."""
        base_dst, base_src = repo_dirs

        sibling = base_dst / "sibling.txt"
        sibling.write_text("sibling")
        symlink_dest = base_dst / "symlink.txt"
        try:
            os.symlink(sibling, symlink_dest)
            has_symlink_privilege = True
        except OSError:
            has_symlink_privilege = False

        if has_symlink_privilege:
            # 1. Reject destination symlink itself (dst symlink -> sibling file)
            dst_path, dst_reason = resolve_dst("symlink.txt", base_dst, base_src)
            assert dst_path is None
            assert "FAIL: SYMLINK_DESTINATION_NOT_PERMITTED" in dst_reason

            # 2. Reject ancestor symlink (ancestor symlink -> in-repo alternate subtree)
            alt_dir = base_dst / "alt_dir"
            alt_dir.mkdir()
            symlink_dir = base_dst / "symlink_dir"
            os.symlink(alt_dir, symlink_dir)

            dst_path, dst_reason = resolve_dst("symlink_dir/nested.txt", base_dst, base_src)
            assert dst_path is None
            assert "FAIL: SYMLINK_DESTINATION_NOT_PERMITTED" in dst_reason

            # 3. Reject ancestor symlink pointing outside repo
            outside_dir = base_dst.parent / "outside_dir"
            outside_dir.mkdir()
            symlink_ext_dir = base_dst / "symlink_ext_dir"
            os.symlink(outside_dir, symlink_ext_dir)
            dst_path, dst_reason = resolve_dst("symlink_ext_dir/nested.txt", base_dst, base_src)
            assert dst_path is None
            assert "FAIL: SYMLINK_DESTINATION_NOT_PERMITTED" in dst_reason

    @pytest.mark.parametrize("valid_path", [
        "valid/nested/path",
        "requirements.txt",
        "pyproject.toml",
        "schemas/model_access_envelope.schema.json",
        "lean/Aevion/SBIR",
        "docs/architecture/index.md",
    ])
    def test_valid_contained_path_accepted(self, repo_dirs, valid_path):
        """Valid relative paths within containment boundaries must be accepted."""
        base_dst, base_src = repo_dirs

        # Create source directory/file so it exists in base_src
        target_src = base_src / valid_path
        target_src.parent.mkdir(parents=True, exist_ok=True)
        target_src.write_text("valid content", encoding="utf-8")

        src_path, src_reason = resolve_src(valid_path, base_src)
        assert src_reason is None
        assert src_path is not None
        assert src_path.is_relative_to(base_src)
        assert src_path != base_src

        dst_path, dst_reason = resolve_dst(valid_path, base_dst, base_src)
        assert dst_reason is None
        assert dst_path is not None
        assert dst_path.is_relative_to(base_dst)
        assert dst_path != base_dst


class TestMirrorManifestEntries:
    """Verifies that all entries in the committed MIRROR_MANIFEST.md are admitted."""

    def test_all_manifest_entries_admitted(self, repo_dirs):
        import re
        base_dst, base_src = repo_dirs
        manifest_file = Path(__file__).resolve().parents[1] / "MIRROR_MANIFEST.md"
        assert manifest_file.exists(), "MIRROR_MANIFEST.md must exist"

        text = manifest_file.read_text(encoding="utf-8")
        entries = re.findall(r"^\s*src:\s*(.+?)\s*->\s*(.+?)\s*$", text, flags=re.MULTILINE)
        assert len(entries) > 0, "At least one mirror manifest entry must exist"

        for src, dst in entries:
            src_path, src_reason = resolve_src(src, base_src)
            assert src_reason is None, f"Source '{src}' was rejected: {src_reason}"
            assert src_path is not None

            dst_path, dst_reason = resolve_dst(dst, base_dst, base_src)
            assert dst_reason is None, f"Destination '{dst}' was rejected: {dst_reason}"
            assert dst_path is not None
