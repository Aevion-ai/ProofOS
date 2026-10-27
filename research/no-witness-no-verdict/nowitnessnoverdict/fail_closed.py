"""No Witness, No Verdict — core fail-closed transition gate.

Every consequential state transition x_t --a_t--> x_{t+1} must discharge
typed obligations for identity, authority, evidence, ACP binding, XAL
verification, continuity, and effect scope. Missing any mandatory
obligation yields HOLD or REJECT — never ADMIT.

Formal claim 1 (executable form):
    not (all obligations discharged)  =>  disposition in {HOLD, REJECT}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


class Disposition(str, Enum):
    ADMIT = "ADMIT"
    HOLD = "HOLD"
    REJECT = "REJECT"


class ObligationKind(str, Enum):
    IDENTITY = "identity"
    AUTHORITY = "authority"
    EVIDENCE = "evidence"
    ACP_BINDING = "acp_binding"
    XAL_VERIFICATION = "xal_verification"
    CONTINUITY = "continuity"
    EFFECT_SCOPE = "effect_scope"


#: Mandatory obligations for any consequential transition.
MANDATORY_OBLIGATIONS: frozenset[ObligationKind] = frozenset(
    {
        ObligationKind.IDENTITY,
        ObligationKind.AUTHORITY,
        ObligationKind.EVIDENCE,
        ObligationKind.ACP_BINDING,
        ObligationKind.XAL_VERIFICATION,
        ObligationKind.CONTINUITY,
        ObligationKind.EFFECT_SCOPE,
    }
)


@dataclass(frozen=True)
class Obligation:
    kind: ObligationKind
    obligation_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ObligationKind):
            raise ValueError(f"unknown obligation kind: {self.kind!r}")
        if not self.obligation_id:
            raise ValueError("obligation_id must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind.value, "obligation_id": self.obligation_id}


@dataclass(frozen=True)
class ObligationDischarge:
    obligation_id: str
    evidence_ref: str

    def to_dict(self) -> dict[str, Any]:
        return {"obligation_id": self.obligation_id, "evidence_ref": self.evidence_ref}


def obligations_met(
    discharges: Sequence[ObligationDischarge],
    mandatory: frozenset[ObligationKind] = MANDATORY_OBLIGATIONS,
) -> tuple[bool, list[str]]:
    """Return (met, missing). REJECT when any mandatory obligation is absent.

    Formal claim 1: not (all o in O discharged) => REJECT/HOLD.
    """
    discharged_ids = {d.obligation_id for d in discharges}
    missing = [o.value for o in mandatory if o.value not in discharged_ids]
    return (not missing, missing)


@dataclass(frozen=True)
class TransitionRequest:
    transition_id: str
    action: str
    actor_identity: str | None
    authority_lease: str | None
    evidence: Sequence[str] = field(default_factory=list)
    acp_digest: str | None = None
    xal_verification: str | None = None
    continuity_ref: str | None = None
    effect_scope: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "action": self.action,
            "actor_identity": self.actor_identity,
            "authority_lease": self.authority_lease,
            "evidence": list(self.evidence),
            "acp_digest": self.acp_digest,
            "xal_verification": self.xal_verification,
            "continuity_ref": self.continuity_ref,
            "effect_scope": self.effect_scope,
        }


def decide_transition(
    request: TransitionRequest,
    mandatory: frozenset[ObligationKind] = MANDATORY_OBLIGATIONS,
) -> tuple[Disposition, list[str]]:
    """Fail-closed disposition for a consequential transition.

    - Any mandatory obligation missing  -> REJECT
    - Identity/authority present but evidence unverifiable -> HOLD
    - Everything discharged            -> ADMIT
    """
    reasons: list[str] = []

    missing_obligations: list[str] = []
    if request.actor_identity is None:
        missing_obligations.append(ObligationKind.IDENTITY.value)
    if request.authority_lease is None:
        missing_obligations.append(ObligationKind.AUTHORITY.value)
    if not request.evidence:
        missing_obligations.append(ObligationKind.EVIDENCE.value)
    if request.acp_digest is None:
        missing_obligations.append(ObligationKind.ACP_BINDING.value)
    if request.xal_verification is None:
        missing_obligations.append(ObligationKind.XAL_VERIFICATION.value)
    if request.continuity_ref is None:
        missing_obligations.append(ObligationKind.CONTINUITY.value)
    if request.effect_scope is None:
        missing_obligations.append(ObligationKind.EFFECT_SCOPE.value)

    if missing_obligations:
        reasons.append("missing_obligations:" + ",".join(sorted(missing_obligations)))
        return Disposition.REJECT, reasons

    # Evidence admissibility: a present-but-unverifiable evidence chain holds.
    if not any(e.startswith("sha256:") for e in request.evidence):
        reasons.append("evidence_not_content_bound")
        return Disposition.HOLD, reasons

    return Disposition.ADMIT, reasons


def reject_is_absorbing(
    hard_fault: bool,
    disposition: Disposition,
) -> bool:
    """Executable form of theorem reject_is_absorbing.

    Once a hard fault exists, downstream components cannot convert the
    transition into ADMIT/PASS/PROMOTE.
    """
    if hard_fault:
        return disposition == Disposition.REJECT
    return True  # no hard fault: obligation not triggered
