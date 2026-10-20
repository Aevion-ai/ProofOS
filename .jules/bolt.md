## 2024-10-20 - [Enum Comparison Optimization]
**Learning:** Instantiating dictionary inline inside enum `__ge__` and `__gt__` magic methods causes a new dictionary allocation on every comparison, significantly slowing down operations.
**Action:** Extract the mapping dictionary to a module-level constant defined directly below the class, and use the enum instance (`self`) as the dictionary key (not `self.value`) to avoid breaking runtime while benefiting from ~3.5x speedup.
