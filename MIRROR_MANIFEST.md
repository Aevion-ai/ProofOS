# ProofOS Mirror Manifest

ProofOS is the **governed public mirror** of a curated subset of the canonical
Aevion monorepo: [`Aevion-ai/Aevion-Verifiable-AI`](https://github.com/Aevion-ai/Aevion-Verifiable-AI).

This manifest defines the only paths that may be copied from the monorepo into
this repository by the automated mirror workflow. Anything not listed here is
out of scope for the public mirror.

## Mirror rules

1. **Allow-list only.** Only paths listed under [Path map](#path-map) are copied.
2. **No secrets.** `.env` files, key directories, internal evidence with
d credentials, and full git history are never mirrored.
3. **Scan before commit.** Every sync runs a secret scan (TruffleHog) on the
   candidate commit and aborts on any verified finding.
4. **Tests must pass.** The mirror runs the ProofOS test suite and aborts on
   failure.
5. **No force pushes.** The workflow commits normally and pushes to `main` only
   when all gates pass.
6. **Human override.** `workflow_dispatch` may be used by maintainers to trigger
   a sync; auto-merges are limited to the paths below.

## Path map

Each line maps a path inside the monorepo (`src`) to a path inside this repo
(`dst`). Directory paths are copied recursively; missing source paths are
skipped.

```text
src: requirements.txt -> requirements.txt
src: pyproject.toml -> pyproject.toml
src: package.json -> package.json
src: LICENSE -> LICENSE
src: CONTRIBUTING.md -> CONTRIBUTING.md
src: SECURITY.md -> SECURITY.md
src: schemas/proofos_model_access_envelope.schema.json -> schemas/model_access_envelope.schema.json
src: lean/Aevion/SBIR -> lean/Aevion/SBIR
```

## Sync metadata

| Field | Value |
|-------|-------|
| `source_commit` | `TBD` |
| `last_sync` | `TBD` |
| `source_repo` | `Aevion-ai/Aevion-Verifiable-AI` |
| `mirror_branch` | `main` |

## Expanding the manifest

Additions require:
- Confirmation that the source path contains no credentials or internal-only
  evidence.
- A successful dry-run of the mirror workflow in a fork or branch.
- Approval from a repo admin (RED lane for boundary-crossing changes).
