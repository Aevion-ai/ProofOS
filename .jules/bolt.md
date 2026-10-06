## 2024-10-06 - Cache Enum comparison logic dictionary
**Learning:** Instantiating dictionaries dynamically in Enum comparison dunder methods (like __ge__ and __gt__) causes unnecessary memory allocations and halves comparison speed. However, one must be cautious to maintain correct Enum behavior.
**Action:** Always extract repetitive mappings into module-level constants. When using `self` as a key in mapping dicts for Enums inheriting from `str`, reference the constant and pass `self` instead of `self.value` to retain proper semantic comparisons.
