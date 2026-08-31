import pathlib

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
