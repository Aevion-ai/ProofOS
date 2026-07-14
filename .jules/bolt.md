## 2024-05-24 - Avoid recalculating constants in __ge__ and __gt__

**Learning:** Creating dictionaries inside hot dunder methods like `__ge__` and `__gt__` is surprisingly expensive in Python. Re-allocating the same order map every time these comparison operators are invoked reduces comparison performance.
**Action:** Extract the map to module-level constants or class variables to double performance for operations using these comparators.
