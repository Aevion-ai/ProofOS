## 2024-07-25 - Optimize Enum comparisons with module-level dictionary

**Learning:** Re-instantiating the dictionary on each method call like `__ge__` in Enum class significantly drops performance. But putting the map mapping caching as method/property directly breaks semantics, so you must define the module-level constants *below* the class for dictionary mapping caching instead.

**Action:** Extract repeated dictionary instantiation into a module-level constant when optimizing Python classes or Enums, but place it below the class if it refers to the class itself.
