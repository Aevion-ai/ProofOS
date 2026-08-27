"""Tests for mirror admission control and replayable SHA-256 receipts."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from src.aevion_runtime.mirror_admission import (
    AdmissionDecision,
    canonical_sha256,
    evaluate_mapping,
    governed_copy_mapping,
    parse_path_map_lines,
)


def _load_mirror_sync() -> object:
    """Load scripts/mirror_sync.py — the workflow copy entrypoint."""
    root = Path(__file__).parent.parent
    spec = importlib.util.spec_from_file_location(
        "mirror_sync",
        root / "scripts" / "mirror_sync.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


MANIFEST_FIXTURE = """\
```text
src: requirements.txt -> requirements.txt
src: pyproject.toml -> pyproject.toml
src: package.json -> package.json
src: LICENSE -> LICENSE
src: CONTRIBUTING.md -> CONTRIBUTING.md
src: SECURITY.md -> SECURITY.md
src: schemas/proofos_model_access_envelope.schema.json -> schemas/model_access_envelope.schema.json
src: lean/Aevion/SBIR -> lean/Aevion/SBIR
```
"""


class TestParsePathMapLines:
    def test_parses_manifest_fixture_format(self) -> None:
        mappings = parse_path_map_lines(MANIFEST_FIXTURE)
        assert len(mappings) == 8
        assert mappings[0] == ("requirements.txt", "requirements.txt")
        assert mappings[-1] == ("lean/Aevion/SBIR", "lean/Aevion/SBIR")

    def test_ignores_non_mapping_lines(self) -> None:
        text = "# comment\nsrc: a.txt -> b.txt\nnot a mapping"
        mappings = parse_path_map_lines(text)
        assert mappings == [("a.txt", "b.txt")]

    def test_real_manifest_admits_all_listed_mappings(self, tmp_path: Path) -> None:
        manifest = Path(__file__).parent.parent / "MIRROR_MANIFEST.md"
        text = manifest.read_text(encoding="utf-8")
        mappings = parse_path_map_lines(text)
        assert len(mappings) >= 8

        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        monorepo.mkdir()
        repo.mkdir()

        for src, dst in mappings:
            decision = evaluate_mapping(src, dst, monorepo, repo)
            assert decision.admitted, f"expected admit for {src} -> {dst}: {decision.reason}"


class TestCanonicalSha256:
    def test_replayable_hash(self) -> None:
        payload = {
            "decision": "admit",
            "reason": "mapping within governed bases",
            "src": "LICENSE",
            "dst": "LICENSE",
            "resolved_src": "/tmp/.monorepo/LICENSE",
            "resolved_dst": "/tmp/LICENSE",
        }
        h1 = canonical_sha256(payload)
        h2 = canonical_sha256(dict(payload))
        assert h1 == h2
        assert len(h1) == 64


class TestAdmissionAdmit:
    def test_legitimate_file_mapping(self, tmp_path: Path) -> None:
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        monorepo.mkdir()
        repo.mkdir()
        (monorepo / "LICENSE").write_text("MIT", encoding="utf-8")

        decision = evaluate_mapping("LICENSE", "LICENSE", monorepo, repo)
        assert decision.admitted
        assert decision.resolved_src.endswith("LICENSE")
        assert decision.resolved_dst.endswith("LICENSE")
        assert len(decision.receipt_hash) == 64

    def test_legitimate_nested_directory(self, tmp_path: Path) -> None:
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        nested = monorepo / "lean" / "Aevion" / "SBIR"
        nested.mkdir(parents=True)
        (nested / "Proof.lean").write_text("-- proof", encoding="utf-8")

        decision = evaluate_mapping(
            "lean/Aevion/SBIR",
            "lean/Aevion/SBIR",
            monorepo,
            repo,
        )
        assert decision.admitted

    def test_receipt_replay_same_inputs_same_hash(self, tmp_path: Path) -> None:
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        monorepo.mkdir()
        repo.mkdir()

        d1 = evaluate_mapping("pyproject.toml", "pyproject.toml", monorepo, repo)
        d2 = evaluate_mapping("pyproject.toml", "pyproject.toml", monorepo, repo)
        assert d1.receipt_hash == d2.receipt_hash
        assert d1.decision == "admit"


class TestAdmissionDenyTraversal:
    def test_deny_src_traversal(self, tmp_path: Path) -> None:
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        monorepo.mkdir()
        repo.mkdir()

        decision = evaluate_mapping("../outside.txt", "safe.txt", monorepo, repo)
        assert not decision.admitted
        assert "traversal" in decision.reason or "escapes" in decision.reason

    def test_deny_dst_traversal(self, tmp_path: Path) -> None:
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        monorepo.mkdir()
        (monorepo / "ok.txt").write_text("ok", encoding="utf-8")
        repo.mkdir()

        decision = evaluate_mapping("ok.txt", "../../escaped.txt", monorepo, repo)
        assert not decision.admitted

    def test_deny_absolute_src(self, tmp_path: Path) -> None:
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        monorepo.mkdir()
        repo.mkdir()

        decision = evaluate_mapping("/etc/passwd", "passwd", monorepo, repo)
        assert not decision.admitted
        assert "absolute" in decision.reason

    def test_deny_empty_mapping(self, tmp_path: Path) -> None:
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        monorepo.mkdir()
        repo.mkdir()

        decision = evaluate_mapping("", "dst.txt", monorepo, repo)
        assert not decision.admitted
        assert "empty" in decision.reason


class TestAdmissionDenySecrets:
    """Deny is the success case for attack-like path names (fake tokens only)."""

    @pytest.mark.parametrize(
        "src,dst",
        [
            (".env", "config.env"),
            ("secrets/.env", "out/.env"),
            ("keys/private.pem", "keys/private.pem"),
            ("ssh/id_rsa", "ssh/id_rsa"),
            ("tokens/github_pat_fake_fixture_abc123", "tokens/pat.txt"),
            ("internal/my_credentials_backup.json", "backup.json"),
        ],
    )
    def test_deny_secret_like_names(
        self,
        tmp_path: Path,
        src: str,
        dst: str,
    ) -> None:
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        monorepo.mkdir()
        repo.mkdir()

        decision = evaluate_mapping(src, dst, monorepo, repo)
        assert not decision.admitted
        assert decision.decision == "deny"
        assert "secret-like" in decision.reason
        assert len(decision.receipt_hash) == 64

    def test_deny_dst_secret_name(self, tmp_path: Path) -> None:
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        monorepo.mkdir()
        (monorepo / "readme.md").write_text("ok", encoding="utf-8")
        repo.mkdir()

        decision = evaluate_mapping("readme.md", ".env", monorepo, repo)
        assert not decision.admitted
        assert "secret-like" in decision.reason

    def test_deny_receipt_hash_stable(self, tmp_path: Path) -> None:
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        monorepo.mkdir()
        repo.mkdir()

        d1 = evaluate_mapping("github_pat_fixture_token", "out.txt", monorepo, repo)
        d2 = evaluate_mapping("github_pat_fixture_token", "out.txt", monorepo, repo)
        assert not d1.admitted
        assert d1.receipt_hash == d2.receipt_hash


class TestAdmissionDecisionType:
    def test_frozen_dataclass(self) -> None:
        d = AdmissionDecision(
            decision="deny",
            reason="test",
            src="a",
            dst="b",
            resolved_src=None,
            resolved_dst=None,
            receipt_hash="abc",
        )
        assert not d.admitted


class TestGovernedCopyPath:
    """Regression tests through scripts/mirror_sync.copy_mapping (real copy path)."""

    def test_nested_secret_child_denies_and_does_not_copy(
        self,
        tmp_path: Path,
    ) -> None:
        mirror_sync = _load_mirror_sync()
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        pkg = monorepo / "pkg"
        pkg.mkdir(parents=True)
        repo.mkdir()
        (pkg / "ok.txt").write_text("ok", encoding="utf-8")
        nested = pkg / "nested"
        nested.mkdir()
        (nested / ".env").write_text("FAKE_SECRET=fixture", encoding="utf-8")

        result = mirror_sync.copy_mapping("pkg", "pkg", monorepo, repo)
        assert result == 1
        assert not (repo / "pkg" / "nested" / ".env").exists()

    def test_nested_secret_deny_preserves_preexisting_dest(
        self,
        tmp_path: Path,
    ) -> None:
        mirror_sync = _load_mirror_sync()
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        pkg = monorepo / "pkg"
        nested = pkg / "nested"
        nested.mkdir(parents=True)
        repo.mkdir()

        dest_pkg = repo / "pkg"
        dest_pkg.mkdir(parents=True)
        (dest_pkg / "keep_me.txt").write_text("preserve me", encoding="utf-8")

        (nested / ".env").write_text("FAKE_SECRET=fixture", encoding="utf-8")

        result = mirror_sync.copy_mapping("pkg", "pkg", monorepo, repo)
        assert result == 1
        assert (dest_pkg / "keep_me.txt").read_text(encoding="utf-8") == "preserve me"
        assert not (dest_pkg / "nested" / ".env").exists()
        assert not (dest_pkg / ".env").exists()

    def test_outbound_child_symlink_denies_and_does_not_copy_target(
        self,
        tmp_path: Path,
    ) -> None:
        mirror_sync = _load_mirror_sync()
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "escaped.txt").write_text("ESCAPED_BYTES_FIXTURE", encoding="utf-8")

        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        pkg = monorepo / "pkg"
        pkg.mkdir(parents=True)
        repo.mkdir()
        (pkg / "ok.txt").write_text("ok", encoding="utf-8")
        (pkg / "escape_link").symlink_to(outside / "escaped.txt")

        result = mirror_sync.copy_mapping("pkg", "pkg", monorepo, repo)
        assert result == 1
        assert not (repo / "pkg" / "escape_link").exists()
        dst_pkg = repo / "pkg"
        if dst_pkg.exists():
            for path in dst_pkg.rglob("*"):
                if path.is_file() and not path.is_symlink():
                    assert "ESCAPED_BYTES_FIXTURE" not in path.read_text(encoding="utf-8")

    def test_legitimate_nested_file_copies_via_mirror_sync(
        self,
        tmp_path: Path,
    ) -> None:
        mirror_sync = _load_mirror_sync()
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        pkg = monorepo / "pkg"
        nested = pkg / "nested"
        nested.mkdir(parents=True)
        repo.mkdir()
        (nested / "readme.md").write_text("hello nested", encoding="utf-8")

        result = mirror_sync.copy_mapping("pkg", "pkg", monorepo, repo)
        assert result == 0
        assert (repo / "pkg" / "nested" / "readme.md").read_text(encoding="utf-8") == "hello nested"

    def test_governed_copy_mapping_matches_mirror_sync_entrypoint(
        self,
        tmp_path: Path,
    ) -> None:
        mirror_sync = _load_mirror_sync()
        monorepo = tmp_path / "monorepo"
        repo = tmp_path / "repo"
        nested = monorepo / "pkg" / "nested"
        nested.mkdir(parents=True)
        repo.mkdir()
        (nested / "note.txt").write_text("synced", encoding="utf-8")

        decision = governed_copy_mapping("pkg", "pkg", monorepo, repo)
        assert decision.admitted
        assert mirror_sync.copy_mapping("pkg", "pkg", monorepo, repo) == 0
        assert (repo / "pkg" / "nested" / "note.txt").exists()
