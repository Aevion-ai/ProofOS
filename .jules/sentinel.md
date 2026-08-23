## 2025-02-19 - [Path Traversal in Python Path Construction]
**Vulnerability:** Constructing paths from untrusted manifest strings using `Path(base) / src` without `.lstrip('/')` or `.resolve()` validation allows path traversal to sensitive files like `.git/config` if the string contains `../` or starts with `/`.
**Learning:** Python's `pathlib.Path` evaluation of `/` operation will evaluate to an absolute path if the right-hand operand starts with `/`, and concatenating `../` will allow traversing outside the base directory.
**Prevention:** Always strip leading slashes using `.lstrip('/')` before concatenating, resolve the constructed path, and validate it using `pathlib.Path.is_relative_to()` against the allowed base directory.
