from enum import Enum

class AccessTier(str, Enum):
    PUBLIC = "PUBLIC"
    BUSINESS = "BUSINESS"
    TRUSTED_ACCESS = "TRUSTED_ACCESS"
    HUMAN_ONLY = "HUMAN_ONLY"

    def __ge__(self, other) -> bool:
        return _ACCESS_TIER_ORDER[self] >= _ACCESS_TIER_ORDER[other]

    def __gt__(self, other) -> bool:
        return _ACCESS_TIER_ORDER[self] > _ACCESS_TIER_ORDER[other]

_ACCESS_TIER_ORDER = {
    AccessTier.PUBLIC: 0,
    AccessTier.BUSINESS: 1,
    AccessTier.TRUSTED_ACCESS: 2,
    AccessTier.HUMAN_ONLY: 3,
}

print(AccessTier.BUSINESS >= AccessTier.PUBLIC)
print(AccessTier.BUSINESS > AccessTier.PUBLIC)
print(AccessTier.PUBLIC >= AccessTier.BUSINESS)
