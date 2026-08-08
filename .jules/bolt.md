## 2024-05-18 - AccessTier __ge__ and __gt__ dictionary allocation optimization
**Learning:** Python Enum methods that recreate a dictionary mapping Enum members to integers on every invocation (like `__ge__` and `__gt__` in `AccessTier`) suffer a massive performance penalty. Defining a module-level constant mapping and referencing it within the Enum methods improves performance by ~60%.
**Action:** Extract inline dictionary creation in Enum comparison methods to module-level constants to avoid per-call allocation overhead.
