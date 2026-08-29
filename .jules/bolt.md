## 2025-01-20 - [Avoid Dictionary Redefinition in Python Enums]
 **Learning:** Dictionary redefinition inside Python Enum comparison methods causes significant overhead on every comparison. Creating a dictionary literal `order = {...}` inside `__ge__` or `__gt__` results in ~2.5x slower execution compared to a cached mapping.
 **Action:** Define the ordering mapping as a module-level constant (e.g. `_ACCESS_TIER_ORDER`) below the Enum class and reference it in the comparison methods.
