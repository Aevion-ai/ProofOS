## 2024-03-24 - Cache Enum Dictionary Lookups
**Learning:** Re-allocating a dictionary inside enum comparison methods (`__ge__`, `__gt__`) introduces significant performance overhead (~100% execution time increase) on hot paths.
**Action:** Extract such dictionaries to module-level constants below the class and use `self` as the key, preventing runtime dictionary allocation.
