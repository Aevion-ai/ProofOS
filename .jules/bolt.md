## 2024-07-16 - [Dictionary Allocation in Magic Methods]
**Learning:** Instantiating dictionaries inside frequently called magic methods like `__ge__` and `__gt__` causes significant performance overhead due to repeated reallocation.
**Action:** Extract such static mapping dictionaries to module-level constants or class-level attributes to avoid unnecessary overhead in hot paths.
