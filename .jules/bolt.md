## 2024-10-02 - Optimize Enum comparisons in AccessTier
**Learning:** Recreating dictionaries inside Enum magic methods like `__ge__` and `__gt__` incurs significant overhead on every comparison. Creating the order dictionary at the module level significantly improves performance.
**Action:** Move order dictionaries for Enum comparison methods to module-level constants to avoid per-call allocation overhead.
