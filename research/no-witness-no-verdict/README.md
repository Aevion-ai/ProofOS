# No Witness, No Verdict

**Fail-Closed, Receipt-Bound State Transitions for Long-Horizon Agents**

An agent may propose changes to itself, its memory, or its harness, but it
cannot grant those changes authority. Every consequential state transition
requires an independently verifiable witness.

This is the governed public research extraction for the paper of the same
name. The full Aevion monorepo remains private; this directory is the
publishable artifact.

## Scientific contribution (six formal claims)

1. `reject_is_absorbing` — once a hard fault exists, downstream components
   cannot convert the transition into ADMIT/PASS/PROMOTE.
2. `candidate_only_cannot_authorize` — reflection, memory compilers, and
   self-improvement emit candidates; they cannot produce authority.
3. `no_same_epoch_self_certification` — reflection generated in epoch E
   cannot authorize an action in epoch E.
4. `same_authority_root_is_not_independent` — two identities from the same
   authority root are not an independent quorum.
5. `resume_cannot_repeat_consumed_effect` — a consumed resume must not fire
   twice (resume semantics).
6. `receipt_divergence_invalidates_transition` — digest divergence between
   a signed receipt and current bindings invalidates replay/promotion.

## Layout

```
paper/          manuscript source (main.tex, references.bib, figures/)
src/            canonical Python source
nowitnessnoverdict/  importable package (mirrors src/)
lean/           Lean 4 formal statements (NoWitnessNoVerdict.*)
tests/          evaluation battery (10-fixture adversarial matrix + resume)
schemas/        receipt/transition schemas
fixtures/       machine-readable fixtures
evidence/       reproduction receipts
reproduce.sh    clean-environment reproduction
CITATION.cff    citation metadata
LICENSE         Apache-2.0
```

## Evaluation battery (abridged)

| Fixture | Expected |
|---|---|
| Missing authority lease | REJECT |
| Inferred evidence as observed | REJECT |
| Self-asserted capability | REJECT |
| Route/action mismatch | REJECT |
| Receipt body altered after signing | REJECT |
| Environment digest changed | REJECT |
| Same-root review | HOLD/REJECT |
| Same-epoch authority request | REJECT |
| Valid transition | ADMIT |
| Execution fails after valid admission | ADMIT + FAILURE |

## Reproduction

```bash
bash reproduce.sh          # Python battery + artifact digests
cd ../../../ && lake build NoWitnessNoVerdict   # Lean (WSL preferred)
```

## Claim ceiling

```
OPEN RESEARCH ARTIFACT
LOCAL AND CI-REPRODUCIBLE SOFTWARE EVIDENCE
NOT PRODUCT, REGULATORY, OR SAFETY CERTIFICATION
```

Results apply only to the released configuration. No claim of production
certification, court admissibility, FedRAMP readiness, independent
reproduction, or hardware-rooted attestation is made.
