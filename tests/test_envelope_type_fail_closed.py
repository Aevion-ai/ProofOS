"""Regression: ModelAccessEnvelope must reject non-enum classified fields.

Fail-open confirmed 2026-10-25 (adversarial self-audit): is_safe_deployable()
never reads access_tier / safeguard_mode / capability_class, and a plain string
such as "UNKNOWN" stored in access_tier passes every tier validator by
early-return, so the deployment gate returned True for an envelope whose
classified fields were never typed.

Fix: __post_init__ raises ValueError on non-enum instances of the three
classified fields. These tests pin that behavior; removing the check must
turn them red.
"""

import pytest

from src.aevion_runtime.model_access_envelope import (
    AccessTier,
    CapabilityClass,
    ModelAccessEnvelope,
    SafeguardMode,
)


def _base_kwargs(**overrides):
    kwargs = dict(
        model_id="test-model",
        capability_class=CapabilityClass.GENERAL,
        access_tier=AccessTier.BUSINESS,
        safeguard_mode=SafeguardMode.FULL,
        fallback_model="safe-fallback",
        retention_policy_days=30,
        receipt_required=True,
        human_gate_required=True,
    )
    kwargs.update(overrides)
    return kwargs


@pytest.mark.parametrize(
    "field,value",
    [
        ("access_tier", "UNKNOWN"),   # the exact adversarial finding
        ("access_tier", "PUBLIC"),    # valid-looking string must still be rejected
        ("access_tier", "HUMAN_ONLY"),
        ("safeguard_mode", "FULL"),
        ("safeguard_mode", "LIFTED_BY_APPROVAL"),
        ("capability_class", "GENERAL"),
        ("capability_class", "DUAL_USE_CRITICAL"),
    ],
)
def test_non_enum_classified_fields_rejected(field, value):
    with pytest.raises(ValueError, match=field):
        ModelAccessEnvelope(**_base_kwargs(**{field: value}))


def test_enum_fields_still_construct_and_deployable():
    env = ModelAccessEnvelope(**_base_kwargs())
    assert env.is_safe_deployable() is True


def test_none_and_dict_still_fail_closed():
    """None / missing fields raise (TypeError) — fail-closed, not a bypass."""
    with pytest.raises(TypeError):
        ModelAccessEnvelope(None)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ModelAccessEnvelope({})  # type: ignore[arg-type]


def test_classmethods_unaffected():
    """Named constructors use real enum members and must keep working."""
    assert ModelAccessEnvelope.fable_5().access_tier is AccessTier.PUBLIC
    assert ModelAccessEnvelope.mythos_5().access_tier is AccessTier.TRUSTED_ACCESS
    assert ModelAccessEnvelope.aevion_proof_os("m").is_safe_deployable()
