"""Mirror manifest guard tests.

These tests exercise the guards that keep the public mirror from publishing
private monorepo content, and the workflow wiring that makes the guards load
bearing rather than decorative.
"""

import os
import pathlib
import re
import subprocess
import textwrap

import pytest
import yaml

from scripts.mirror_paths import (
    copy_source_tree,
    resolve_dst,
    resolve_src,
    validate_source_tree,
)


@pytest.fixture
def dirs(tmp_path):
    base_dst_dir = tmp_path.resolve()
    base_src_dir = (base_dst_dir / ".monorepo").resolve()
    base_src_dir.mkdir()
    return base_dst_dir, base_src_dir


@pytest.mark.parametrize(
    "malicious_src",
    [
        "/",
        ".",
        "./",
        "//",
        "foo/..",
        "./foo/..",
        ".git",
        ".git/config",
        "nested/.git/config",
        "a/../..",
        "/etc/passwd",
    ],
)
def test_rejects_malicious_source(dirs, malicious_src):
    _base_dst, base_src = dirs
    path, reason = resolve_src(malicious_src, base_src)
    assert path is None
    assert reason is not None


@pytest.mark.parametrize(
    "malicious_dst",
    [
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
        "/tmp/abs",
    ],
)
def test_rejects_malicious_destinations(dirs, malicious_dst):
    base_dst, base_src = dirs
    path, reason = resolve_dst(malicious_dst, base_dst, base_src)
    assert path is None
    assert reason is not None


def test_allows_valid_paths(dirs):
    base_dst, base_src = dirs
    src_path, src_reason = resolve_src("docs/index.html", base_src)
    assert src_path is not None
    assert src_reason is None

    dst_path, dst_reason = resolve_dst("docs/index.html", base_dst, base_src)
    assert dst_path is not None
    assert dst_reason is None


def test_all_manifest_paths_are_permitted(dirs):
    """Every mapping in the shipped manifest must survive both resolvers."""
    base_dst, base_src = dirs
    manifest = pathlib.Path("MIRROR_MANIFEST.md").read_text(encoding="utf-8")
    mappings = re.findall(r"^src:\s*(.+?)\s*->\s*(.+?)\s*$", manifest, re.MULTILINE)

    assert mappings
    for raw_src, raw_dst in mappings:
        src_path, src_reason = resolve_src(raw_src, base_src)
        dst_path, dst_reason = resolve_dst(raw_dst, base_dst, base_src)
        assert src_path is not None, src_reason
        assert dst_path is not None, dst_reason


def test_rejects_source_tree_with_nested_git(dirs):
    """A .git dir nested inside an admitted directory must not be mirrored."""
    _base_dst, base_src = dirs
    source = base_src / "allowed" / ".git"
    source.mkdir(parents=True)

    assert validate_source_tree(source.parent) is not None


def test_rejects_source_tree_with_symlink(dirs, tmp_path):
    """Symlinks are refused so the mirror cannot leak outside the allow-list.

    Runs on POSIX (including WSL); skipped only on Windows, where unprivileged
    symlink creation is unavailable.
    """
    if os.name == "nt":
        pytest.skip("CI runs this symlink check on Ubuntu")

    _base_dst, base_src = dirs
    source = base_src / "allowed"
    source.mkdir()
    (source / "leak").symlink_to(tmp_path / "outside")

    assert validate_source_tree(source) is not None


@pytest.mark.parametrize(
    "credential_name",
    [
        ".env",
        ".env.local",
        "server.pem",
        "private.key",
        "id_rsa",
        "id_rsa.enc",
        "credentials.json",
        ".git-credentials",
    ],
)
def test_rejects_credential_shaped_files_inside_admitted_tree(dirs, credential_name):
    """A credential-shaped file nested in an allowed directory must not mirror."""
    _base_dst, base_src = dirs
    source = base_src / "allowed"
    source.mkdir(parents=True)
    (source / credential_name).write_text("SECRET", encoding="utf-8")

    reason = validate_source_tree(source)

    assert reason is not None
    assert "credential" in reason


def test_rejects_credential_shaped_single_file_source(dirs):
    """A file source that is itself credential-shaped is refused at copy time."""
    _base_dst, base_src = dirs
    source = base_src / ".env"
    source.write_text("SECRET=1", encoding="utf-8")

    # resolve_src admits the path; the content scan is what catches it.
    resolved, reason = resolve_src(".env", base_src)
    assert resolved is not None

    assert validate_source_tree(resolved) is not None


def test_rejects_credential_shaped_nested_directory(dirs):
    _base_dst, base_src = dirs
    source = base_src / "allowed"
    nested = source / "keys"
    nested.mkdir(parents=True)
    (nested / "id_rsa").write_text("SECRET", encoding="utf-8")

    assert validate_source_tree(source) is not None


def test_allows_clean_source_tree(dirs):
    """Names that merely resemble credentials are not over-blocked."""
    _base_dst, base_src = dirs
    source = base_src / "allowed"
    source.mkdir()
    (source / "environment.py").write_text("x = 1", encoding="utf-8")
    (source / "credentials.md").write_text("docs", encoding="utf-8")
    (source / "keyring.py").write_text("y = 2", encoding="utf-8")

    assert validate_source_tree(source) is None


def test_copy_rejects_nested_git_without_destination_mutation(dirs):
    base_dst, base_src = dirs
    source = base_src / "allowed"
    (source / ".git").mkdir(parents=True)
    (source / "normal.txt").write_text("new", encoding="utf-8")
    destination = base_dst / "published"
    destination.write_text("original", encoding="utf-8")

    reason = copy_source_tree(source, destination)

    assert reason is not None
    assert destination.read_text(encoding="utf-8") == "original"


def test_copy_rejects_credentials_without_destination_mutation(dirs):
    """Rejection must happen before the destination is deleted or replaced."""
    base_dst, base_src = dirs
    source = base_src / "allowed"
    source.mkdir(parents=True)
    (source / "normal.txt").write_text("new", encoding="utf-8")
    (source / ".env").write_text("SECRET=1", encoding="utf-8")
    destination = base_dst / "published"
    destination.write_text("original", encoding="utf-8")

    reason = copy_source_tree(source, destination)

    assert reason is not None
    assert destination.read_text(encoding="utf-8") == "original"


def test_copy_valid_source_replaces_destination(dirs):
    base_dst, base_src = dirs
    source = base_src / "allowed"
    source.mkdir()
    (source / "normal.txt").write_text("new", encoding="utf-8")
    destination = base_dst / "published"
    destination.write_text("original", encoding="utf-8")

    assert copy_source_tree(source, destination) is None
    assert (destination / "normal.txt").read_text(encoding="utf-8") == "new"


def test_copy_rejects_symlink_without_destination_mutation(dirs, tmp_path):
    if os.name == "nt":
        pytest.skip("Linux checkride exercises real symlink semantics")

    base_dst, base_src = dirs
    source = base_src / "allowed"
    source.mkdir()
    (source / "normal.txt").write_text("new", encoding="utf-8")
    (source / "leak").symlink_to(tmp_path / "outside")
    destination = base_dst / "published"
    destination.write_text("original", encoding="utf-8")

    reason = copy_source_tree(source, destination)

    assert reason is not None
    assert destination.read_text(encoding="utf-8") == "original"


def test_workflow_imports_guard_and_disables_persist():
    """The workflow must call the module guard and drop the monorepo token."""
    workflow_path = pathlib.Path(".github/workflows/mirror-from-monorepo.yml")
    text = workflow_path.read_text(encoding="utf-8")

    assert "from scripts.mirror_paths import copy_source_tree, resolve_src, resolve_dst" in text
    assert "copy_reason = copy_source_tree(src_path, dst_path)" in text

    workflow = yaml.safe_load(text)
    checkout_step = next(
        step
        for step in workflow["jobs"]["mirror"]["steps"]
        if step.get("uses", "").startswith("actions/checkout")
        and "MONOREPO_MIRROR_TOKEN" in str(step.get("with", {}))
    )

    assert checkout_step["with"].get("persist-credentials") is False


def test_workflow_sync_script_compiles():
    """The inline Python heredoc must still be syntactically valid."""
    text = pathlib.Path(".github/workflows/mirror-from-monorepo.yml").read_text(
        encoding="utf-8"
    )
    script = text.split("python3 - <<'PY'\n", 1)[1].split("\n          PY", 1)[0]

    compile(textwrap.dedent(script), "mirror-from-monorepo.yml", "exec")


def test_monorepo_checkout_path_is_ignored():
    """The private checkout must not be committable by the workflow's `git add -A`.

    Asserted through git itself rather than by reading .gitignore, so the test
    fails if the rule is present but ineffective (wrong order, wrong anchor,
    later negation).
    """
    workflow = yaml.safe_load(
        pathlib.Path(".github/workflows/mirror-from-monorepo.yml").read_text(
            encoding="utf-8"
        )
    )
    checkout_step = next(
        step
        for step in workflow["jobs"]["mirror"]["steps"]
        if step.get("uses", "").startswith("actions/checkout")
        and "MONOREPO_MIRROR_TOKEN" in str(step.get("with", {}))
    )
    checkout_path = checkout_step["with"]["path"]

    # Two independent failure modes, both of which have actually occurred:
    #   1. the path is committed as a gitlink, which .gitignore cannot undo
    #      because git never ignores a tracked path;
    #   2. the path is untracked but not ignored, so `git add -A` stages it.
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", checkout_path],
        capture_output=True,
    )
    assert tracked.returncode != 0, (
        f"{checkout_path!r} is tracked in this public repository. It is the "
        "private monorepo checkout and must never be committed; .gitignore "
        "has no effect on an already-tracked path, so it must be removed "
        "with `git rm --cached`."
    )

    ignored = subprocess.run(
        ["git", "check-ignore", "-q", checkout_path],
        capture_output=True,
    )
    assert ignored.returncode == 0, (
        f"the monorepo checkout path {checkout_path!r} is not gitignored, so "
        "`git add -A` in this public repository will stage it. Note a "
        "directory-only pattern is not matched while the path is absent."
    )
