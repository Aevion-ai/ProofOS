## 2024-05-24 - Dictionary recreation in Enum comparison methods
**Learning:** Recreating a mapping dictionary inside Python magic methods (like `__ge__`) on every invocation causes severe overhead for Enums inheriting from `str`.
**Action:** Extract mapping dictionaries to module-level constants defined below the class, and use the enum instance (`self`) rather than `self.value` as the key to prevent runtime regressions while boosting speed.
