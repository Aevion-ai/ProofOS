## 2024-06-25 - Caching Enum comparisons
**Learning:** Python re-creates the dictionary on every call to `__ge__` and `__gt__` if it's defined inside the method. By moving it to a module-level constant mapping, we can get a ~3x speedup on enum comparisons. Since this is used in `can_serve` which could be called frequently for access control, this is a measurable performance win.
**Action:** Extract static dictionaries to module-level constants for enum comparison methods.
