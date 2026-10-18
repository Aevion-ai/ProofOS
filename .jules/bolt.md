## 2024-05-14 - Enum method comparison overhead
**Learning:** Re-creating mapping dictionaries inside Enum magic methods like `__ge__` and `__gt__` causes significant runtime overhead per comparison. In Python 3.12, combining `str` and `IntEnum` causes metaclass conflicts, so creating an external module-level constant map is the safest and most performant pattern for caching Enum orders.
**Action:** Always move static lookup dictionaries out of hot path methods into module-level variables for Enum comparisons.
