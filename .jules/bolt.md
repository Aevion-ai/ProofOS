## 2024-05-18 - Enum comparison optimization
**Learning:** Re-creating a dictionary in Python on every invocation of special methods like `__ge__` and `__gt__` is computationally expensive, especially for Enum types used in frequent comparisons.
**Action:** When overriding comparison methods for Enums, define the ordering dictionary as a module-level constant below the class and use the enum instance (`self`) as the dictionary key rather than re-declaring it locally.
