"""Tests for mirror admission control and replayable SHA-256 receipts."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.aevion_runtime.mirror_admission import (
    AdmissionDecision,
    canonical_sha256,
    evaluate_mapping,
    parse_path_map_lines,
)


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
