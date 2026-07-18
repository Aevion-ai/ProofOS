## 2024-06-25 - [Enum Performance Optimization]
**Learning:** In Python, defining a dictionary inside Enum comparison methods (like `__ge__` or `__gt__`) creates the dictionary on every single call, significantly degrading performance (from ~0.16µs to ~0.58µs per call).
**Action:** Always move static mappings (like tier orders) to module-level constants to avoid per-call allocation overhead while retaining safety and correctness.
