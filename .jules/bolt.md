## 2025-02-27 - Cache Enum Ordering dictionaries
**Learning:** Dictionary instantiation inside Enum comparison magic methods (`__ge__`, `__gt__`) incurs significant overhead on every call.
**Action:** Extract these dictionaries to module-level constants and index them using the enum instance (`self`) to improve comparison performance by ~50%.
