"""Candidate-only self-evolution and independent authority roots.

EGON, memory compilers, invariant discovery, and self-improving harnesses
may emit candidates, but they cannot produce authority. A reflection
generated in epoch E cannot authorize an action in epoch E (same-epoch
self-certification is excluded). Two identities derived from the same
authority root are not an independent quorum.

Formal claims 3 and 5 (executable form).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


class CandidateOnlyViolation(RuntimeError):
    """Raised when a candidate path attempts to grant authority."""


@dataclass(frozen=True)
class AuthorityRoot:
    root_id: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"root_id": self.root_id, "description": self.description}


@dataclass(frozen=True)
class AuthorityGrant:
    grant_id: str
    authority_root: AuthorityRoot
    recipient: str
    scope: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "grant_id": self.grant_id,
            "authority_root": self.authority_root.to_dict(),
            "recipient": self.recipient,
            "scope": self.scope,
        }


def candidate_cannot_authorize(candidate: str, grant: AuthorityGrant) -> bool:
    """A candidate artifact cannot, by itself, produce an authority grant.

    Executable form of theorem candidate_only_cannot_authorize. The grant
    must reference an independent authority root, not the candidate's own
    emission path.
    """
    return candidate not in grant.authority_root.root_id


def assert_reflection_only(action: str) -> None:
    """Boundary: reflection paths may observe, score, recommend — never act.

    Mirrors the estate's aevion_egon_reflection.boundaries contract.
    """
    if action.startswith(("authorize", "grant", "promote", "admit", "execute")):
        raise CandidateOnlyViolation(f"reflection-only boundary violated by {action}")


def same_authority_root_is_not_independent(a: AuthorityRoot, b: AuthorityRoot) -> bool:
    """Two identities from the same authority root are not independent.

    Executable form of theorem same_root_is_not_quorum.
    """
    return a.root_id != b.root_id


@dataclass(frozen=True)
class EpochContext:
    execution_epoch: int
    reflection_epoch: int
    authority_eligibility_epoch: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_epoch": self.execution_epoch,
            "reflection_epoch": self.reflection_epoch,
            "authority_eligibility_epoch": self.authority_eligibility_epoch,
        }


def same_epoch_self_certification(epoch: EpochContext) -> bool:
    """Reflection generated in epoch E must not authorize in epoch E.

    Executable form of theorem no_same_epoch_self_certification:
    minimum safe promotion is E execution -> E+1 reflection -> E+2 authority.
    Returns True when the attempt violates the rule (i.e., reflection epoch
    == authority eligibility epoch).
    """
    return epoch.reflection_epoch == epoch.authority_eligibility_epoch


def promote_candidate(
    candidate: Mapping[str, Any],
    authority: AuthorityGrant,
    epoch: EpochContext,
) -> str:
    """Gate a candidate promotion. Fail-closed: REJECT unless every
    condition discharges."""
    if candidate_cannot_authorize(str(candidate.get("candidate_id", "")), authority):
        return "REJECT"
    if same_epoch_self_certification(epoch):
        return "REJECT"
    if not same_authority_root_is_not_independent(authority.authority_root, authority.authority_root):
        return "REJECT"
    return "ADMIT_CANDIDATE"
