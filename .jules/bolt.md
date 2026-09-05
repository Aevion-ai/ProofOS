## 2026-09-05 - Enum Comparison Dictionary Overhead
**Learning:** Re-instantiating dictionaries inside Enum comparison methods (like `__ge__`) causes significant overhead in Python. Caching the dictionary at the module level yields roughly a 3.5x speedup.
**Action:** Extract static mapping dictionaries used in frequent comparisons to module-level constants instead of defining them locally within methods.
