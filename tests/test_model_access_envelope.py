"""Tests for ModelAccessEnvelope — CapabilityAccessSeparationLemma runtime.

Validates the access envelope constraints confirmed by Anthropic Fable 5 / Mythos 5.
"""

import pytest
from src.aevion_runtime.model_access_envelope import (
    AccessTier,
    CapabilityClass,
    ModelAccessEnvelope,
    SafeguardMode,
)


class TestAccessTierOrdering:
    """Access tier partial order: more restrictive >= less restrictive."""

    def test_public_is_least_restrictive(self) -> None:
        assert AccessTier.BUSINESS >= AccessTier.PUBLIC
        assert AccessTier.TRUSTED_ACCESS >= AccessTier.PUBLIC
        assert AccessTier.HUMAN_ONLY >= AccessTier.PUBLIC

    def test_human_only_is_most_restrictive(self) -> None:
        assert AccessTier.HUMAN_ONLY >= AccessTier.PUBLIC
        assert AccessTier.HUMAN_ONLY >= AccessTier.BUSINESS
        assert AccessTier.HUMAN_ONLY >= AccessTier.TRUSTED_ACCESS
        assert AccessTier.HUMAN_ONLY >= AccessTier.HUMAN_ONLY

    def test_transitive(self) -> None:
        assert AccessTier.TRUSTED_ACCESS >= AccessTier.BUSINESS
        assert AccessTier.BUSINESS >= AccessTier.PUBLIC
        assert AccessTier.TRUSTED_ACCESS >= AccessTier.PUBLIC

    def test_not_less_restrictive_reverse(self) -> None:
        assert not (AccessTier.PUBLIC >= AccessTier.BUSINESS)
        assert not (AccessTier.BUSINESS >= AccessTier.TRUSTED_ACCESS)
        assert not (AccessTier.PUBLIC >= AccessTier.HUMAN_ONLY)


class TestModelAccessEnvelope:
    """ModelAccessEnvelope construction and validation."""

    def test_basic_envelope(self) -> None:
        e = ModelAccessEnvelope(
            model_id="test-model",
            capability_class=CapabilityClass.GENERAL,
            access_tier=AccessTier.BUSINESS,
            safeguard_mode=SafeguardMode.FULL,
            fallback_model="safe-model",
        )
        assert e.is_safe_deployable()

    def test_public_tier_requires_fallback(self) -> None:
        with pytest.raises(ValueError, match="fallback_model"):
            ModelAccessEnvelope(
                model_id="test",
                capability_class=CapabilityClass.GENERAL,
                access_tier=AccessTier.PUBLIC,
                safeguard_mode=SafeguardMode.FULL,
                fallback_model="",  # Should fail
            )

    def test_public_tier_requires_full_safeguards(self) -> None:
        with pytest.raises(ValueError, match="FULL safeguard"):
            ModelAccessEnvelope(
                model_id="test",
                capability_class=CapabilityClass.GENERAL,
                access_tier=AccessTier.PUBLIC,
                safeguard_mode=SafeguardMode.PARTIAL,
                fallback_model="safe",
            )

    def test_human_only_requires_human_gate(self) -> None:
        with pytest.raises(ValueError, match="human_gate"):
            ModelAccessEnvelope(
                model_id="test",
                capability_class=CapabilityClass.GENERAL,
                access_tier=AccessTier.HUMAN_ONLY,
                safeguard_mode=SafeguardMode.FULL,
                human_gate_required=False,
            )

    def test_human_only_requires_receipt(self) -> None:
        with pytest.raises(ValueError, match="receipt"):
            ModelAccessEnvelope(
                model_id="test",
                capability_class=CapabilityClass.GENERAL,
                access_tier=AccessTier.HUMAN_ONLY,
                safeguard_mode=SafeguardMode.FULL,
                receipt_required=False,
            )

    def test_dual_use_critical_requires_elevated_access(self) -> None:
        with pytest.raises(ValueError, match="DUAL_USE_CRITICAL"):
            ModelAccessEnvelope(
                model_id="test",
                capability_class=CapabilityClass.DUAL_USE_CRITICAL,
                access_tier=AccessTier.PUBLIC,
                safeguard_mode=SafeguardMode.FULL,
                fallback_model="safe",
            )

    def test_dual_use_critical_requires_30_day_retention(self) -> None:
        with pytest.raises(ValueError, match="retention"):
            ModelAccessEnvelope(
                model_id="test",
                capability_class=CapabilityClass.DUAL_USE_CRITICAL,
                access_tier=AccessTier.TRUSTED_ACCESS,
                safeguard_mode=SafeguardMode.FULL,
                retention_policy_days=7,
            )

    def test_dual_use_critical_accepts_trusted_access(self) -> None:
        e = ModelAccessEnvelope(
            model_id="test",
            capability_class=CapabilityClass.DUAL_USE_CRITICAL,
            access_tier=AccessTier.TRUSTED_ACCESS,
            safeguard_mode=SafeguardMode.FULL,
            fallback_model="safe",
        )
        assert e.is_safe_deployable()

    def test_not_safe_without_receipt(self) -> None:
        e = ModelAccessEnvelope(
            model_id="test",
            capability_class=CapabilityClass.GENERAL,
            access_tier=AccessTier.BUSINESS,
            safeguard_mode=SafeguardMode.FULL,
            fallback_model="safe",
            receipt_required=False,
        )
        assert not e.is_safe_deployable()

    def test_fallback_produces_safer_envelope(self) -> None:
        e = ModelAccessEnvelope(
            model_id="test",
            capability_class=CapabilityClass.MYTHOS_CLASS,
            access_tier=AccessTier.PUBLIC,
            safeguard_mode=SafeguardMode.FULL,
            fallback_model="safe-model",
        )
        fb = e.fallback_envelope()
        assert fb.model_id == "safe-model"
        assert fb.capability_class == CapabilityClass.GENERAL
        assert fb.access_tier >= e.access_tier  # More restrictive

    def test_can_serve_lower_tier(self) -> None:
        e = ModelAccessEnvelope(
            model_id="test",
            capability_class=CapabilityClass.GENERAL,
            access_tier=AccessTier.BUSINESS,
            safeguard_mode=SafeguardMode.FULL,
            fallback_model="safe",
        )
        assert e.can_serve(AccessTier.PUBLIC)
        assert e.can_serve(AccessTier.BUSINESS)
        assert not e.can_serve(AccessTier.TRUSTED_ACCESS)


class TestAnthropicMapping:
    """Validate Anthropic Fable 5 / Mythos 5 mapping."""

    def test_fable_5_is_public_mythos_class(self) -> None:
        fable = ModelAccessEnvelope.fable_5()
        assert fable.model_id == "claude-mythos-5"
        assert fable.capability_class == CapabilityClass.MYTHOS_CLASS
        assert fable.access_tier == AccessTier.PUBLIC
        assert fable.safeguard_mode == SafeguardMode.FULL
        assert fable.fallback_model == "claude-opus-4-8"

    def test_mythos_5_is_trusted_access(self) -> None:
        mythos = ModelAccessEnvelope.mythos_5()
        assert mythos.model_id == "claude-mythos-5"
        assert mythos.capability_class == CapabilityClass.MYTHOS_CLASS
        assert mythos.access_tier == AccessTier.TRUSTED_ACCESS

    def test_fable_mythos_same_model(self) -> None:
        """CapabilityAccessSeparationLemma: same model, different envelopes."""
        fable = ModelAccessEnvelope.fable_5()
        mythos = ModelAccessEnvelope.mythos_5()
        assert fable.model_id == mythos.model_id  # Same underlying model
        assert fable.access_tier != mythos.access_tier  # Different access
        assert fable.safeguard_mode != mythos.safeguard_mode  # Different safeguards

    def test_aevion_envelope_is_safe_deployable(self) -> None:
        aevion = ModelAccessEnvelope.aevion_proof_os("any-model")
        assert aevion.is_safe_deployable()
        assert aevion.receipt_required
        assert aevion.human_gate_required
        assert aevion.retention_policy_days >= 30


class TestSchemaValidation:
    """Validate Python implementation against JSON Schema."""

    def test_schema_validation_roundtrip(self) -> None:
        import json
        from pathlib import Path
        import jsonschema

        schema_path = Path(__file__).parent.parent / "schemas" / "model_access_envelope.schema.json"
        schema = json.loads(schema_path.read_text())

        for e in [
            ModelAccessEnvelope.fable_5(),
            ModelAccessEnvelope.mythos_5(),
            ModelAccessEnvelope.aevion_proof_os("test-model"),
            ModelAccessEnvelope(
                model_id="public-model",
                capability_class=CapabilityClass.GENERAL,
                access_tier=AccessTier.PUBLIC,
                safeguard_mode=SafeguardMode.FULL,
                fallback_model="safe-fallback",
            ),
            ModelAccessEnvelope(
                model_id="restricted-model",
                capability_class=CapabilityClass.DUAL_USE_CRITICAL,
                access_tier=AccessTier.TRUSTED_ACCESS,
                safeguard_mode=SafeguardMode.FULL,
                fallback_model="safe-fallback",
            ),
        ]:
            jsonschema.validate(e.to_dict(), schema)

    def test_schema_rejects_invalid(self) -> None:
        """Schema should reject envelopes that violate constraints."""
        import json
        from pathlib import Path
        import jsonschema

        schema_path = Path(__file__).parent.parent / "schemas" / "model_access_envelope.schema.json"
        schema = json.loads(schema_path.read_text())

        # PUBLIC tier without fallback
        with pytest.raises((jsonschema.ValidationError, ValueError)):
            invalid = ModelAccessEnvelope(
                model_id="bad-public",
                capability_class=CapabilityClass.GENERAL,
                access_tier=AccessTier.PUBLIC,
                safeguard_mode=SafeguardMode.FULL,
                fallback_model="",
            )
            jsonschema.validate(invalid.to_dict(), schema)


class TestSerialization:
    """Envelope serialization."""

    def test_to_dict_roundtrip(self) -> None:
        e = ModelAccessEnvelope(
            model_id="test",
            capability_class=CapabilityClass.MYTHOS_CLASS,
            access_tier=AccessTier.BUSINESS,
            safeguard_mode=SafeguardMode.FULL,
            fallback_model="safe",
        )
        d = e.to_dict()
        assert d["model_id"] == "test"
        assert d["capability_class"] == "MYTHOS_CLASS"
        assert d["access_tier"] == "BUSINESS"
