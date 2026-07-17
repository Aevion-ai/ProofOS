## 2024-05-24 - Inline Dictionary Allocation in Magic Methods
**Learning:** Instantiating dictionaries inside frequently called magic methods (like `__ge__` and `__gt__` on Enums) creates a significant performance bottleneck due to continuous O(N) memory allocation per comparison. String Enums can be particularly vulnerable if mapping logic isn't hoisted to the module/class level.
**Action:** Extract mapping dictionaries to module-level constants to ensure single-time allocation and fast O(1) dictionary lookups during Enum comparison.
