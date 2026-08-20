## 2024-05-24 - Python Enum Dict Instantiation Overhead
**Learning:** Re-instantiating dictionaries inside Python special methods like `__ge__` and `__gt__` within an `Enum` definition incurs a substantial performance penalty. Each comparison creates a new dictionary, leading to unnecessary allocations and garbage collection overhead in comparison-heavy operations.
**Action:** Extract the mapping to a module-level constant defined directly beneath the Enum class. Doing so resulted in a ~3-4x performance improvement (from ~2.9s to ~0.8s for 5,000,000 operations).
