## 2024-05-23 - Enum Method Dictionary Caching
**Learning:** Recreating a dictionary on every Enum method call (like `__ge__`) causes unnecessary overhead in Python.
**Action:** Move the dictionary to a module-level constant to cache the mapping and speed up comparisons.
