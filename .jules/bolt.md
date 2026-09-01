## 2024-09-01 - Optimize AccessTier dictionary cache
**Learning:** Rebuilding a dictionary mapping inside a class magic method like `__ge__` or `__gt__` on every comparison results in O(N) allocations for an O(1) lookup, which can significantly degrade performance in hot paths.
**Action:** Use a module-level constant dictionary defined below the class to cache the mappings, and reference it inside the magic methods.
