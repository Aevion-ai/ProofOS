import time
from enum import Enum

class AccessTierOld(str, Enum):
    PUBLIC = "PUBLIC"
    BUSINESS = "BUSINESS"
    TRUSTED_ACCESS = "TRUSTED_ACCESS"
    HUMAN_ONLY = "HUMAN_ONLY"

    def __ge__(self, other) -> bool:
        order = {
            AccessTierOld.PUBLIC: 0,
            AccessTierOld.BUSINESS: 1,
            AccessTierOld.TRUSTED_ACCESS: 2,
            AccessTierOld.HUMAN_ONLY: 3,
        }
        return order[self] >= order[other]

class AccessTierNew(str, Enum):
    PUBLIC = "PUBLIC"
    BUSINESS = "BUSINESS"
    TRUSTED_ACCESS = "TRUSTED_ACCESS"
    HUMAN_ONLY = "HUMAN_ONLY"

    def __ge__(self, other) -> bool:
        return _ACCESS_TIER_ORDER_NEW[self] >= _ACCESS_TIER_ORDER_NEW[other]

_ACCESS_TIER_ORDER_NEW = {
    AccessTierNew.PUBLIC: 0,
    AccessTierNew.BUSINESS: 1,
    AccessTierNew.TRUSTED_ACCESS: 2,
    AccessTierNew.HUMAN_ONLY: 3,
}

t0 = time.time()
for _ in range(1000000):
    _ = AccessTierOld.BUSINESS >= AccessTierOld.PUBLIC
t1 = time.time()
print(f"Old: {t1 - t0:.4f}s")

t0 = time.time()
for _ in range(1000000):
    _ = AccessTierNew.BUSINESS >= AccessTierNew.PUBLIC
t1 = time.time()
print(f"New: {t1 - t0:.4f}s")
