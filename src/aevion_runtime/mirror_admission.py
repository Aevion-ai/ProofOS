"""
Mirror admission control — governed path copy decisions with SHA-256 receipts.

Every path the mirror workflow may copy is evaluated by this module before
copy. Decisions are fail-closed: traversal, escape from explicit bases, and
secret-like names are denied. Each decision emits a canonical JSON receipt whose
SHA-256 hash is independently replayable (no wall-clock in the hashed payload).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

# Same line format as .github/workflows/mirror-from-monorepo.yml inline Python.
_PATH_MAP_RE = re.compile(r"^\s*src:\s*(.+?)\s*->\s*(.+?)\s*$")


def canonical_sha256(payload: Mapping[str, Any]) -> str:
    """SHA-256 of canonical JSON (sorted keys, minimal separators)."""
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def parse_path_map_lines(text: str) -> list[tuple[str, str]]:
    """Parse MIRROR_MANIFEST.md path-map lines: ``src: <path> -> <path>``."""
    mappings: list[tuple[str, str]] = []
    for line in text.splitlines():
        match = _PATH_MAP_RE.match(line)
        if match:
            mappings.append((match.group(1), match.group(2)))
    return mappings


def _secret_deny_reason(rel_path: str) -> str | None:
    """
    Return a deny reason if any path component matches secret-like patterns.

    Patterns (fail-closed):
      - .env (exact or suffix)
      - *.pem
      - id_rsa
      - github_pat* (prefix)
      - *credentials* (substring)
    """
    for part in PurePosixPath(rel_path).parts:
        if part in (".", ".."):
            continue
        lower = part.lower()
        if lower == ".env" or lower.endswith(".env"):
            return "secret-like name: .env"
        if lower.endswith(".pem"):
            return "secret-like name: *.pem"
        if lower == "id_rsa" or lower.startswith("id_rsa"):
            return "secret-like name: id_rsa"
        if lower.startswith("github_pat"):
            return "secret-like name: github_pat*"
        if "credentials" in lower:
            return "secret-like name: *credentials*"
    return None


def _path_under_base(base: Path, rel: str) -> tuple[Path | None, str | None]:
    """
    Resolve ``rel`` under ``base``. Return (resolved_path, deny_reason).

    Fail-closed on absolute paths, empty paths, ``..`` components, and escape
    from ``base`` after normalization.
    """
    if not rel or not rel.strip():
        return None, "empty path mapping"

    stripped = rel.strip()
    if stripped != rel:
        return None, "path mapping has leading or trailing whitespace"

    if stripped.startswith("/") or stripped.startswith("\\"):
        return None, "absolute path not allowed"

    # Reject Windows drive letters and UNC paths early.
    if re.match(r"^[A-Za-z]:", stripped) or stripped.startswith("//"):
        return None, "absolute path not allowed"

    posix = PurePosixPath(stripped.replace("\\", "/"))
    if posix.is_absolute():
        return None, "absolute path not allowed"

    if not posix.parts or any(part == ".." for part in posix.parts):
        return None, "path traversal (..) not allowed"

    try:
        base_resolved = base.resolve()
        resolved = (base / stripped).resolve()
    except (OSError, ValueError) as exc:
        return None, f"path resolution failed: {exc}"

    if not resolved.is_relative_to(base_resolved):
        return None, "path escapes allowed base"

    return resolved, None


@dataclass(frozen=True)
class AdmissionDecision:
    """Governed admit/deny outcome with a replayable receipt hash."""

    decision: str  # "admit" | "deny"
    reason: str
    src: str
    dst: str
    resolved_src: str | None
    resolved_dst: str | None
    receipt_hash: str

    @property
    def admitted(self) -> bool:
        return self.decision == "admit"


def _receipt_body(
    decision: str,
    reason: str,
    src: str,
    dst: str,
    resolved_src: str | None,
    resolved_dst: str | None,
) -> dict[str, Any]:
    """Stable receipt payload (no timestamps — hash is replayable)."""
    body: dict[str, Any] = {
        "decision": decision,
        "reason": reason,
        "src": src,
        "dst": dst,
    }
    if resolved_src is not None:
        body["resolved_src"] = resolved_src
    if resolved_dst is not None:
        body["resolved_dst"] = resolved_dst
    return body


def evaluate_mapping(
    src: str,
    dst: str,
    monorepo_base: Path,
    repo_root: Path,
) -> AdmissionDecision:
    """
    Evaluate one manifest mapping. Fail-closed; emits a canonical receipt hash.
    """
    secret_src = _secret_deny_reason(src)
    if secret_src:
        body = _receipt_body("deny", secret_src, src, dst, None, None)
        return AdmissionDecision(
            decision="deny",
            reason=secret_src,
            src=src,
            dst=dst,
            resolved_src=None,
            resolved_dst=None,
            receipt_hash=canonical_sha256(body),
        )

    secret_dst = _secret_deny_reason(dst)
    if secret_dst:
        body = _receipt_body("deny", secret_dst, src, dst, None, None)
        return AdmissionDecision(
            decision="deny",
            reason=secret_dst,
            src=src,
            dst=dst,
            resolved_src=None,
            resolved_dst=None,
            receipt_hash=canonical_sha256(body),
        )

    resolved_src, src_reason = _path_under_base(monorepo_base, src)
    if src_reason:
        body = _receipt_body("deny", src_reason, src, dst, None, None)
        return AdmissionDecision(
            decision="deny",
            reason=src_reason,
            src=src,
            dst=dst,
            resolved_src=None,
            resolved_dst=None,
            receipt_hash=canonical_sha256(body),
        )

    resolved_dst, dst_reason = _path_under_base(repo_root, dst)
    if dst_reason:
        body = _receipt_body(
            "deny",
            dst_reason,
            src,
            dst,
            str(resolved_src),
            None,
        )
        return AdmissionDecision(
            decision="deny",
            reason=dst_reason,
            src=src,
            dst=dst,
            resolved_src=str(resolved_src),
            resolved_dst=None,
            receipt_hash=canonical_sha256(body),
        )

    body = _receipt_body(
        "admit",
        "mapping within governed bases",
        src,
        dst,
        str(resolved_src),
        str(resolved_dst),
    )
    return AdmissionDecision(
        decision="admit",
        reason="mapping within governed bases",
        src=src,
        dst=dst,
        resolved_src=str(resolved_src),
        resolved_dst=str(resolved_dst),
        receipt_hash=canonical_sha256(body),
    )


def _child_mapping_path(base: str, rel: str) -> str:
    if not rel:
        return base
    return f"{base}/{rel}"


def _deny_child_decision(
    mapping_src: str,
    mapping_dst: str,
    rel_child: str,
    reason: str,
    resolved_src: str | None = None,
    resolved_dst: str | None = None,
) -> AdmissionDecision:
    child_src = _child_mapping_path(mapping_src, rel_child)
    child_dst = _child_mapping_path(mapping_dst, rel_child)
    body = _receipt_body("deny", reason, child_src, child_dst, resolved_src, resolved_dst)
    return AdmissionDecision(
        decision="deny",
        reason=reason,
        src=child_src,
        dst=child_dst,
        resolved_src=resolved_src,
        resolved_dst=resolved_dst,
        receipt_hash=canonical_sha256(body),
    )


def _symlink_resolves_outside_root(path: Path, root: Path) -> bool:
    """True when a symlink's resolved target lies outside ``root`` (fail-closed)."""
    if not path.is_symlink():
        return False
    try:
        resolved = path.resolve()
        return not resolved.is_relative_to(root.resolve())
    except (OSError, ValueError):
        return True


@dataclass(frozen=True)
class _GovernedEntry:
    src_path: Path
    rel_child: str
    is_symlink: bool


def _collect_governed_entries(
    src_dir: Path,
    src_root: Path,
    mapping_src: str,
    mapping_dst: str,
    monorepo_base: Path,
    repo_root: Path,
) -> tuple[list[_GovernedEntry], AdmissionDecision | None]:
    """
    Walk ``src_dir`` without following symlinks; validate every child name/path.
    """
    entries: list[_GovernedEntry] = []

    for dirpath, dirnames, filenames in os.walk(
        src_dir,
        topdown=True,
        followlinks=False,
    ):
        current = Path(dirpath)
        rel_dir = current.relative_to(src_dir)
        rel_dir_str = rel_dir.as_posix() if rel_dir.parts else ""

        for name in dirnames:
            path = current / name
            rel_child = f"{rel_dir_str}/{name}" if rel_dir_str else name

            child_decision = evaluate_mapping(
                _child_mapping_path(mapping_src, rel_child),
                _child_mapping_path(mapping_dst, rel_child),
                monorepo_base,
                repo_root,
            )
            if not child_decision.admitted:
                return entries, child_decision

            if path.is_symlink():
                if _symlink_resolves_outside_root(path, src_root):
                    return entries, _deny_child_decision(
                        mapping_src,
                        mapping_dst,
                        rel_child,
                        "symlink resolves outside admitted root",
                        str(path),
                    )
                entries.append(_GovernedEntry(path, rel_child, is_symlink=True))

        for name in filenames:
            path = current / name
            rel_child = f"{rel_dir_str}/{name}" if rel_dir_str else name

            child_decision = evaluate_mapping(
                _child_mapping_path(mapping_src, rel_child),
                _child_mapping_path(mapping_dst, rel_child),
                monorepo_base,
                repo_root,
            )
            if not child_decision.admitted:
                return entries, child_decision

            if path.is_symlink():
                if _symlink_resolves_outside_root(path, src_root):
                    return entries, _deny_child_decision(
                        mapping_src,
                        mapping_dst,
                        rel_child,
                        "symlink resolves outside admitted root",
                        str(path),
                    )

            entries.append(_GovernedEntry(path, rel_child, path.is_symlink()))

    return entries, None


def _materialize_governed_entries(
    entries: list[_GovernedEntry],
    dst_dir: Path,
) -> None:
    for entry in entries:
        dst_path = dst_dir / entry.rel_child
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        if entry.is_symlink:
            dst_path.symlink_to(entry.src_path.readlink())
        else:
            shutil.copy2(entry.src_path, dst_path)


def governed_copy_mapping(
    src: str,
    dst: str,
    monorepo_base: Path,
    repo_root: Path,
) -> AdmissionDecision:
    """
    Evaluate and copy one manifest mapping with per-child admission checks.

    Directory copies validate every child path/name before writing anything.
    Outbound symlinks (resolved target outside the admitted source root) are
    denied; inbound symlinks are copied as links without following them.
    """
    decision = evaluate_mapping(src, dst, monorepo_base, repo_root)
    if not decision.admitted:
        return decision

    src_path = Path(decision.resolved_src)
    dst_path = Path(decision.resolved_dst)

    if not src_path.exists():
        return decision

    if src_path.is_symlink():
        if _symlink_resolves_outside_root(src_path, monorepo_base.resolve()):
            return _deny_child_decision(
                src,
                dst,
                "",
                "symlink resolves outside admitted root",
                str(src_path),
            )

    if dst_path.exists():
        if dst_path.is_dir():
            shutil.rmtree(dst_path)
        else:
            dst_path.unlink()

    if src_path.is_dir():
        entries, deny = _collect_governed_entries(
            src_path,
            src_path.resolve(),
            src,
            dst,
            monorepo_base,
            repo_root,
        )
        if deny is not None:
            return deny

        dst_path.mkdir(parents=True, exist_ok=True)
        _materialize_governed_entries(entries, dst_path)
        return decision

    if src_path.is_symlink():
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        dst_path.symlink_to(src_path.readlink())
        return decision

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dst_path)
    return decision
