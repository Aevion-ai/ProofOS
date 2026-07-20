
## 2024-05-24 - Avoid dictionary re-allocation in Enum dunder methods
**Learning:** Re-allocating static mapping dictionaries within Enum comparison methods (e.g. `__ge__`) in Python results in significant, continuous memory churn and CPU overhead. In environments where enum comparisons happen frequently, this overhead is surprisingly large (~3x penalty) compared to a module-level constant lookup.
**Action:** When implementing custom comparison logic for Enums or similar classes that rely on fixed order mappings, always hoist the mapping to a module-level or class-level constant instead of allocating it locally inside the method body.
