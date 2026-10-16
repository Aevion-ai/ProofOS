from enum import Enum
import time

class AccessTierOriginal(str, Enum):
    PUBLIC = "PUBLIC"
    BUSINESS = "BUSINESS"
    TRUSTED_ACCESS = "TRUSTED_ACCESS"
    HUMAN_ONLY = "HUMAN_ONLY"

    def __ge__(self, other) -> bool:
        order = {
            AccessTierOriginal.PUBLIC: 0,
            AccessTierOriginal.BUSINESS: 1,
            AccessTierOriginal.TRUSTED_ACCESS: 2,
            AccessTierOriginal.HUMAN_ONLY: 3,
        }
        return order[self] >= order[other]

class AccessTierOptimized(str, Enum):
    PUBLIC = "PUBLIC"
    BUSINESS = "BUSINESS"
    TRUSTED_ACCESS = "TRUSTED_ACCESS"
    HUMAN_ONLY = "HUMAN_ONLY"

    def __ge__(self, other) -> bool:
        return _ACCESS_TIER_ORDER[self] >= _ACCESS_TIER_ORDER[other]

_ACCESS_TIER_ORDER = {
    AccessTierOptimized.PUBLIC: 0,
    AccessTierOptimized.BUSINESS: 1,
    AccessTierOptimized.TRUSTED_ACCESS: 2,
    AccessTierOptimized.HUMAN_ONLY: 3,
}

t0 = time.time()
for _ in range(1000000):
    _ = AccessTierOriginal.BUSINESS >= AccessTierOriginal.PUBLIC
t1 = time.time()
print(f"Original: {t1 - t0:.4f}s")

t0 = time.time()
for _ in range(1000000):
    _ = AccessTierOptimized.BUSINESS >= AccessTierOptimized.PUBLIC
t1 = time.time()
print(f"Optimized: {t1 - t0:.4f}s")
