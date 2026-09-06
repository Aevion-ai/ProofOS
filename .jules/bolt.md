## 2024-05-23 - [Python Enum Method Dictionary Instantiation]
**Learning:** Instantiating a dictionary inside Enum comparison methods (`__ge__`, `__gt__`) creates significant overhead (over 2x slower) as the dict is created on every call.
**Action:** Extract static mapping dictionaries out of comparison methods to module-level constants (defined after the Enum class) to cache the ordering and improve comparison speed. When doing so for Enums inheriting from `str`, use the enum instance (`self`) as the dictionary key rather than `self.value` to prevent runtime regressions.
