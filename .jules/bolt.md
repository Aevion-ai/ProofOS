## 2024-05-24 - [Enum Comparison Optimization]
**Learning:** Recreating a dictionary mapping inside Enum comparison methods (`__ge__`, `__gt__`) for every call causes a significant performance bottleneck (over 2x slower).
**Action:** Extract static order mappings in Enums to module-level constants (e.g., `_ACCESS_TIER_ORDER`) instead of instantiating them dynamically in comparison methods.
