## 2024-10-25 - Enum Comparison Optimization

**Learning:** When evaluating Enum classes inheriting from `str` for performance, overriding `__ge__` and `__gt__` with hardcoded dictionaries for mapping ordering incurs substantial overhead on instantiation of those dictionaries at every comparison call. In `src/aevion_runtime/model_access_envelope.py`, `AccessTier` overrides these methods by rebuilding a mapping dictionary on every call.

**Action:** Move the mapping dictionary to a module-level constant (or cache it on the class) to avoid rebuilding the dictionary on each comparison. This reduces the time complexity of the comparison from O(N) (where N is the number of enum items and mapping elements) to O(1). Because creating Enums and mapping can be slow if done locally in methods, caching them globally optimizes frequent comparison checks. Be careful not to cause multiple data type exceptions (e.g. TypeError: too many data types) by inheriting from both `str` and `IntEnum`.
