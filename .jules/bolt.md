## 2024-10-03 - Cache AccessTier order dictionary
**Learning:** The `__ge__` and `__gt__` magic methods in the `AccessTier` Enum recreated a dictionary mapping on every call, causing unnecessary overhead for comparison operations.
**Action:** Extract the dictionary mapping into a module-level constant (`_ACCESS_TIER_ORDER`) defined below the enum class to cache the mapping, significantly speeding up comparisons.
