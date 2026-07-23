## 2026-07-23 - Cache Enum Mappings as Module Constants
**Learning:** When optimizing Python classes or Enums, avoid dynamically monkey-patching methods outside the class definition as it breaks semantics and type checking. Define the methods normally within the class, and if dictionary mapping caching is needed, reference module-level constants defined below the class instead.
**Action:** Extract dictionary mappings used in Enum methods to module-level constants defined immediately after the class to improve performance without breaking type semantics.
