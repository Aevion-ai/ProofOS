## 2024-05-24 - Caching Dictionary in Enum Comparisons
**Learning:** Recreating a dictionary on every comparison in `__ge__` and `__gt__` within an Enum is a significant performance bottleneck in Python.
**Action:** Use a module-level constant to cache the ordering dictionary to prevent overhead on every invocation.
