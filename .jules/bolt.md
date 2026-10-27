## 2026-10-27 - Optimize Enum Partial Order Comparisons
**Learning:** Enum comparison methods (`__ge__`, `__gt__`) that redefine a mapping dictionary internally will incur substantial overhead (up to ~3x slower), as the dictionary is re-created on every invocation.
**Action:** Extract the mapping to a module-level dictionary to avoid instantiation overhead during comparisons, using the enum instance (`self`) as the dictionary key to maintain compatibility.
