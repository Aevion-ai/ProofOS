## 2024-05-15 - [Initial]
**Learning:** Initializing journal.
**Action:** Use this journal for performance insights.
## 2024-05-15 - [Enum Comparison Optimization]
**Learning:** Instantiating dictionaries within frequently called Enum comparison methods (like __ge__, __gt__) is a significant performance bottleneck due to continuous allocation.
**Action:** Extract mapping dictionaries to module-level constants defined immediately below the Enum class and use the enum instance (self) as the key to achieve ~70% speedup per comparison.
