## 2024-05-19 - Enum Comparison Optimization
**Learning:** Python Enum comparison methods like `__ge__` and `__gt__` that create a mapping dictionary on every call can introduce significant overhead. This is a common pattern in this codebase.
**Action:** When implementing custom comparison logic for Enums, always cache the ordering dictionary at the module level (below the class definition to avoid type errors) instead of recreating it inside the comparison methods.
