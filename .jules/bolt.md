## 2024-10-07 - Optimize Enum comparisons
**Learning:** Enums in Python recreate objects in the class body dictionary dynamically, leading to slower performance if comparing them requires instantiation of objects (e.g. creating dictionary mapped weights in overridden `__ge__` and `__gt__` magic methods). It is faster to initialize it once at a module level.
**Action:** When redefining comparison behaviors for Enum strings that rely on weight-based ordering, extract mapping dictionaries to module-level constants to avoid initialization overhead on every comparison.
