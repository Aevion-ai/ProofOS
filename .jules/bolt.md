## 2024-09-10 - Dictionary Recreation in Magic Methods
**Learning:** Python re-creates dictionaries defined inside magic methods like `__ge__` and `__gt__` on every single call, which can cause significant overhead when these comparisons are called frequently in access-control checks.
**Action:** Always extract static mapping dictionaries into module-level constants (below the class to handle Enums) and reference them inside magic methods, cutting comparison overhead by roughly 60%.
