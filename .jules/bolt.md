## 2024-05-24 - Fast Enum comparison caching
**Learning:** Dynamically monkey-patching methods for caching can break semantics and type checking. When caching dictionary mappings for Enums inheriting from `str`, use module-level constants and use the enum instance (`self`) as the dictionary key rather than `self.value` to prevent runtime regressions.
**Action:** Always extract static dictionaries out of frequently called methods into module-level constants, especially in Enums where `self` is hashable.
