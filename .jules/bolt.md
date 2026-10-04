## 2024-10-04 - AccessTier Enum Dictionary Allocation
**Learning:** Dictionary instantiation within Enum comparison methods causes severe overhead. Defining it as a module-level constant keyed by the enum instance (`self`) avoids runtime regressions and speeds up comparisons.
**Action:** Cache enum mapping dictionaries as module-level constants below the class definition.
