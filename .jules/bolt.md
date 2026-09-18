## 2024-09-18 - Optimize Python Enum Comparisons
**Learning:** In Python Enums, defining dictionaries within comparison operators (like `__ge__`) creates a new dictionary instance on every evaluation, causing a significant performance bottleneck (over 2x slowdown) for frequent capability checks.
**Action:** Always extract static mapping dictionaries into module-level constants (e.g., `_ORDER_MAP`) and reference them using `self` within Enum comparison methods.
