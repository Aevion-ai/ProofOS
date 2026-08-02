## 2024-08-02 - Optimize Enum Comparisons
**Learning:** Instantiating a dictionary inside `__ge__` and `__gt__` magic methods for Python Enums adds unnecessary overhead on every comparison. Creating the order dictionary locally in each method invocation results in a ~3.5x slowdown compared to a module-level constant lookup.
**Action:** Extract static mapping dictionaries used in frequently called magic methods to module-level constants below the class definition to avoid recreating the dict on each call, while respecting memory constraints regarding monkey-patching.
