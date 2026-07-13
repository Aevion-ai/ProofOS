## 2024-05-18 - Fast Enum Comparisons
**Learning:** In Python Enums, custom `__ge__` and `__gt__` magic methods that dynamically compute mappings each time they are called can add unnecessary overhead. Replacing them with class-level precomputed dictionaries mapping instances to their numerical order avoids dictionary instantiation per comparison and speeds up ordering significantly.
**Action:** When implementing comparisons on Python Enums, use class-level precomputed dictionaries or property lookups against class constants instead of rebuilding the lookup map in every method call.
