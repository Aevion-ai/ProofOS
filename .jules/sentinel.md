## 2024-05-18 - [Path Traversal in Mirror Manifest]
**Vulnerability:** [The python script syncing allowed paths didn't check for path traversal via `../` or absolute paths like `/etc/passwd`.]
**Learning:** [When combining paths and reading manifests, user input needs to be validated against an allowed base directory using `is_relative_to` to avoid traversing out of intended scope.]
**Prevention:** [Always resolve paths constructed from untrusted inputs and explicitly check they reside within the expected base directory.]
