## 2024-05-30 - [AccessTier comparisons performance]
**Learning:** `__ge__` and `__gt__` on the string Enum `AccessTier` recalculates the dictionary every call `order = { ... }` in `model_access_envelope.py`. It is very slow.
**Action:** Move order mapping out of method for O(1) performance boost in Enum comparisons, using module-level variable mapping. Wait, my test worked perfectly!
