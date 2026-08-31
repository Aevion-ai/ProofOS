import pathlib
import subprocess

import pytest
import yaml

from scripts.mirror_paths import resolve_dst, resolve_src


@pytest.fixture
def dirs(tmp_path):
    base_dst_dir = tmp_path.resolve()
    base_src_dir = (base_dst_dir / ".monorepo").resolve()
    base_src_dir.mkdir()
    return base_dst_dir, base_src_dir

@pytest.mark.parametrize("malicious_src", [
    "/",
    ".",
    "./",
    "//",
    "foo/..",
    "./foo/..",
    ".git",
    ".git/config",
    "a/../..",
    "/etc/passwd",
])
def test_rejects_malicious_source(dirs, malicious_src):
    _base_dst, base_src = dirs
    path, reason = resolve_src(malicious_src, base_src)
    assert path is None
    assert reason is not None

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
    "/tmp/abs",
])
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

def test_workflow_imports_guard_and_disables_persist():
    workflow_path = pathlib.Path(".github/workflows/mirror-from-monorepo.yml")
    text = workflow_path.read_text(encoding="utf-8")

    assert "from scripts.mirror_paths import resolve_src, resolve_dst" in text

    # Parse yaml to check for persist-credentials
    workflow = yaml.safe_load(text)
    checkout_step = next(
        step for step in workflow["jobs"]["mirror"]["steps"]
        if step.get("uses", "").startswith("actions/checkout") and "MONOREPO_MIRROR_TOKEN" in str(step.get("with", {}))
    )

    assert checkout_step["with"].get("persist-credentials") is False


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
