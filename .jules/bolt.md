## 2024-05-23 - [Optimize Enum Comparisons]
**Learning:** Python creates a new dictionary on every method call if defined inside the method. For Enum comparison methods (`__ge__`, `__gt__`), defining the order dictionary inside the method causes significant overhead.
**Action:** Extract static mapping dictionaries out of methods and into module-level constants below the class definition to cache the mapping and improve performance. Use `self` as the key.
