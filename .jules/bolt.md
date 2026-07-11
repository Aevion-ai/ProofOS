## 2024-05-24 - Python Enum method optimization
**Learning:** In Python, Enum methods (like `__ge__`) that re-allocate a dictionary for mapping Enum values to integers repeatedly are much slower than moving the dictionary to the module level. I found that allocating a dict inside `__ge__` vs looking up from a module level dictionary gives a substantial speedup when checking many values (60%+).
**Action:** Always check if constant data structures used for logic in Enum methods can be lifted out to module level constants to save repeated allocation cost on hot paths.
