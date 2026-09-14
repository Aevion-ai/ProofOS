## 2024-09-14 - Optimize enum comparison by hoisting dictionary
**Learning:** Instantiating a dictionary repeatedly inside an Enum comparison method (`__ge__`, `__gt__`) incurs significant overhead. Moving the dictionary outside as a module-level constant provides a ~4x speedup.
**Action:** Always hoist static dictionary lookups or constant data structures outside of frequently called methods or comparison operators.
