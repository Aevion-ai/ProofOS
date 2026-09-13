## 2024-05-24 - Enum Dictionary Lookup Caching
**Learning:** In Python, string Enums used as dictionary keys must be referenced by their enum instance (`self`) rather than their underlying string value (`self.value`) to avoid runtime regressions when caching enum methods like `__ge__` and `__gt__`.
**Action:** Define dictionary caching at the module level below the Enum class and ensure the keys map directly to the Enum instance, not its string value.
