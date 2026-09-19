## 2024-05-14 - Python Enum Method Caching Overhead
**Learning:** Recreating mapping dictionaries inside Enum comparison methods (like `__ge__` and `__gt__`) incurs significant overhead, and they can be pulled out to module-level constants to cut execution time by more than half.
**Action:** Extract repeated dictionary instantiations in Enum comparison methods to module-level constants to eliminate instantiation overhead during hot paths.
