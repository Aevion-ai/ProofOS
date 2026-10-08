## 2024-10-08 - Optimize Enum comparisons
**Learning:** Recreating a dictionary on every comparison method call in an Enum (like `__ge__` or `__gt__`) creates significant overhead.
**Action:** Use a single module-level constant for hierarchy lookups to avoid redundant dictionary instantiations.
