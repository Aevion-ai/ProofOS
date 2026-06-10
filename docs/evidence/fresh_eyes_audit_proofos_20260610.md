# Fresh-Eyes Audit — ProofOS (evidence-integrity)

**Classification:** INTERNAL_ONLY
**Authority lane:** OWNER_REVIEW_QUEUE (contains CLEARANCE_REQUIRED / RED items — see §9)
**Date:** 2026-06-10
**Repo under audit:** `Aevion-ai/ProofOS` @ branch `claude/funny-goldberg-vqc095` (HEAD `11b7faa`; `main` @ `5eb2579`, tag `v1.0.0` @ `efc9123`)
**Method:** Same fresh-eyes method as `Aevion-Verifiable-AI` PR #144 (`docs/reports/fresh_eyes_audit_four_repo_20260609.md`), applied to the fifth repo, which was out of scope at the time of that audit. This report **confirms and extends** the open hypothesis recorded in PR #144 §11.

> **Claim hygiene note.** Every advertised metric quoted below (theorem counts, density, NIST/Anthropic framing, quantum-tile names) is reproduced **QUOTED_AS_DATA** — it is evidence of the finding, not an Aevion claim made by this report. This report makes no novelty claim and proves nothing new.

---

## 0. TL;DR

ProofOS advertises a **1,252-theorem, 343-file, 96%-density** Lean corpus with **104 open obligations across 32 files**. The repository actually contains **2 Lean files, 152 lines, 6 theorem declarations** — of which 4 are genuinely proved, 1 is trivialized to `:= True`, and 1 ends in `sorry`. The advertised numbers describe a corpus that is **not in this repository**, and the specific figure "104 open obligations across 32 files" is a **byte-for-byte match** to the `aevion-shield` `lean_stats.py` scan (`sorry_word_in_code = 104`, `sorry_file_count_proof = 32`) — exactly the cross-repo fossilized-metric hypothesis PR #144 left open. The inflated metrics and a RED-gated "NIST published the proof" framing are **already live on the public site** (`aevion.ai`, via `docs/CNAME`), and the Playwright CI smoke test **enforces** the inflated number `1,252` as a pass condition.

Separately, while crosswalking the certificate scheme ProofOS depends on, the audit found a **committed ML-DSA-65 private signing key** in `aevion-shield` (new since PR #144 — see §8). That is a RED security finding requiring key rotation; it is reported here because it is the cryptographic root ProofOS's "receipt chain" story rests on, but the remediation belongs to `aevion-shield`.

> **Redaction note (this published copy).** The exact file path, introducing commit, and `key_id` of the leaked key in §8 are **withheld** from this committed/pushed copy to avoid broadcasting the leak location before rotation. The structural facts establishing severity are retained. The unredacted finding is delivered out-of-band to the owner; the full local report verifies to SHA-256 `12410cb3293f9be1e16d128115e0bd3bef902a8109a6c66b1114f9801ca03ccd`.

---

## 1. What the repository actually contains

Full Lean inventory (`lean/`):

| File | LOC | Declarations | Proof state |
|------|-----|--------------|-------------|
| `lean/LeishmanBerger.lean` | 21 | `def HonestMajority`; `theorem haltSoundness` | **Proved** (`omega`), 0 sorry |
| `lean/CapabilityAccessSeparation.lean` | 131 | `theorem accessTier_le_trans`, `humanOnly_is_top`, `public_is_bottom` | **Proved**, 0 sorry |
| | | `theorem envelope_composition_monotonic (e1 e2 …) : True := by … trivial` | **Trivialized** — statement is `True` (line 110–115) |
| | | `theorem fallback_preserves_safety …` | **Open** — body is `sorry` (line 129) |

**Totals:** 2 files · 152 LOC · 6 theorem declarations · **4 substantive proofs, 1 `:= True` stub, 1 live `sorry`.**

The `envelope_composition_monotonic` stub is the same construction flagged as **S1 trivialization** in PR #144 (`aevion-shield` `SafetyTheorems.lean`): the safety predicate is replaced by `True` and discharged with `trivial`, so a `0 sorry` count reads as "proved" while the theorem asserts nothing. ProofOS's own file header is honest about it ("2 sorry stubs … 1 proven theorem"), but the README's "Proven theorems" table (§3) is not.

---

## 2. The advertised corpus does not exist in this repo

The headline metric appears, identically, in four surfaces:

| Surface | Quoted text (QUOTED_AS_DATA) |
|---------|------------------------------|
| `README.md:8` | "1,252 theorems at 96% density across 343 files" |
| `paper.md:161` | "1,252 active theorems across 343 Lean files … 96.02% proof density, 104 open proof-shaped obligations across 32 files" |
| `architecture.md:81–84` | "1,252 theorems / 96% density / 104 obligations / 32 files" |
| `docs/index.html` + `docs/assets/index-*.js` (public site) | "1,252 theorems at 96% density", "104 open obligations", "343 files" |

Reality: **6 theorem declarations in 2 files.** The gap is ~209× on theorems and ~171× on files. There is no `343`-file Lean tree, no `colony.py`, no `CounselArbiterEnv`, no `eval` harness, and no receipt-chain implementation anywhere in the repository — `quorum.md:179` points to `integrations/tinker_cookbook/src/counsel/colony.py`, which **does not exist** in this repo (the path resolves to zero files). The 150-case colony evaluation (`paper.md` §3.1, `README:78`, `architecture.md:94`) has **no runnable code or receipt** in-repo; the cited numbers are unbacked here.

### 2a. The "104 / 32" figure is a fossil from a *different* repo

PR #144 §11 hypothesized that ProofOS's "104 open obligations across 32 files" is a copy-paste of the `aevion-shield` `lean_stats.py` scan. **Confirmed.** The shield canonical scan reports `sorry_word_in_code = 104` and `sorry_file_count_proof = 32`; ProofOS reproduces both numbers verbatim while shipping neither that corpus nor those obligations. The metric is fossilized: it was lifted from one repo's tool output and pasted into another repo's prose and product page, where it no longer corresponds to anything on disk.

### 2b. The fossil is internally inconsistent

Even the advertised numbers disagree with each other:

- Theorem count: **1,252** (README, paper §161, architecture, site) vs **1,203** (`paper.md:32`, abstract).
- Density: **96% / 96.02%** (everywhere) vs **"~91% discharged"** (`paper.md:32`, `paper.md:161`).
- Open obligations: **104** (everywhere) vs **"59 active sorries in the safety-critical subset"** (`paper.md:84`).

A single corpus measured once cannot produce 1,252 and 1,203 simultaneously. Two different fossil values are in circulation.

---

## 3. The README "Proven theorems" table advertises theorems that are not here

`README.md:82–91` presents seven named theorems as ProofOS deliverables. Presence check against `lean/`:

| Advertised theorem | In ProofOS repo? | Actually located in |
|--------------------|------------------|---------------------|
| `haltSoundness` | ✅ yes | `lean/LeishmanBerger.lean` |
| `accessTier_le_trans` | ✅ yes | `lean/CapabilityAccessSeparation.lean` |
| `barrierInvariance` | ❌ no | not found in any in-scope repo |
| `byzantineGovernance` | ❌ no | `Aevion-Verifiable-AI/lean-proofs/Aevion/AuthorityCalculus/ByzantineGovernance.lean` |
| `barabanov_norm_implies_GAS` | ❌ no | `aevion-shield/Aristotle/extracted/.../Safety/BarabanovStability.lean` |
| `interaction_bounded` | ❌ no | not found in any in-scope repo |
| `etaRecurrenceFinite` | ❌ no | not found in any in-scope repo |

**5 of 7** advertised theorems are absent from ProofOS; the two that resolve at all live in *other* repos. The table mixes the repo's two real theorems with five borrowed or unlocated names, presented uniformly as "Proved (0 sorry)". The same disease as the metrics: the README describes a federation of corpora as if it were this repository.

---

## 4. CI is green but enforces the inflated number

`.github/workflows/ci.yml` runs three jobs:

1. `python-tests` — `pytest tests/` → **20 passed** (reproduced locally, `tests/test_model_access_envelope.py`). Genuine and healthy.
2. `playwright` — `e2e/smoke.spec.ts:17,28` asserts the literal string **`1,252`** is visible on the rendered page. **CI fails if the inflated theorem count is ever corrected.** The inflated metric is load-bearing in the test suite.
3. `lean-check` — `lake build` over `lean/`. The `sorry` in `fallback_preserves_safety` is a Lean **warning, not an error**, so the build is green despite the open obligation. `lake build` only ever touches the 2 local files; it cannot and does not validate the advertised 343-file corpus.

Net: a passing CI badge certifies (a) a 20-test Python suite, (b) that the website still displays "1,252", and (c) that 2 Lean files elaborate with a tolerated sorry. It certifies **nothing** about the advertised corpus.

---

## 5. RED-gated claims are already public

`docs/CNAME` = `aevion.ai`; the `docs/` build is the deployed product page. Strings extracted from the shipped bundle (`docs/assets/index-*.js`, QUOTED_AS_DATA):

- **NIST framing:** *"NIST published the proof. Anthropic shipped the architecture. We built the receipted governance for Frontier AI."*
- **Quantum tiles:** *"Quantum Witness … Wukong Bell + QGOV Predict tiles"*.
- **Corpus metrics:** *"1,252 theorems at 96% density"*, *"104 open obligations"*, *"343 files"*.
- **Status:** *"NIST AI Consortium applicant."*

Two governance problems:

1. **The NIST framing is RED-gated internally but live externally.** `paper.md` carries an explicit fence — `INTERNAL DRAFT v4.4 — NOT FOR SUBMISSION`, `arXiv submission is RED (owner approval + final claim review required)`. The paper's entire thesis rests on **Vassilev, *IEEE S&P*, DOI `10.1109/MSEC.2026.3678214`, "published June 9 2026"** (i.e. the day before this audit). That citation could not be verified from this container (no general web egress; `aevion.ai` returns HTTP 403 to the fetch tool). Whether or not the DOI resolves, the public site already runs the "NIST published the proof" framing **without** the owner approval the paper says is required — and "NIST published the proof / we built the architecture" risks reading as **NIST endorsement of ProofOS**, which neither the paper nor any evidence supports. `architecture.md:4` compounds this by labeling itself *"Canonical — use for all external communication (papers, proposals, product page)"* while importing the same RED-gated framing.
2. **Quantum-tile names on a public surface.** `Aevion-Verifiable-AI/.claude/rules/quantum-claims.md` (KIRIN-FOLD-001) sets `QGOV = INTERNAL_ONLY`, `PUBLIC_RELEASE: HELD` until an owner token records `APPROVED`. Naming "Wukong Bell" / "QGOV Predict" on `aevion.ai` is at least a channel-control concern against that ceiling. (Naming a tile is softer than a quantum-advantage claim — no "advantage/supremacy/outperforms" string was found on the site — but the governance rule gates the names themselves, not only the superlatives.)

---

## 6. What is genuinely healthy

In fairness, and consistent with the PR #144 pattern (code better than its claims):

- **`tests/test_model_access_envelope.py` — 20/20 pass.** Real runtime, real tests.
- **`src/aevion_runtime/model_access_envelope.py`** (208 LOC) is a coherent, honestly-documented implementation of the access-envelope idea. The Fable 5 / Mythos 5 capability-vs-access-policy separation it formalizes is a **defensible architectural observation**.
- **The 4 genuinely-proved Lean theorems are real and correct-looking** (`haltSoundness` by `omega`; the three `AccessTier` ordering lemmas by case split). `haltSoundness` (`3f < n → 2f < n`) is a valid, if elementary, honest-majority arithmetic fact.
- **The "published open-obligation surface" thesis is itself sound** — a system that publishes its gap list *is* more auditable. The problem is not the thesis; it is that the published surface (104/32) describes a different repository.

The repository is a clean, modest, ~6-theorem demo with a 20-test runtime. The defect is entirely in the **claims layer** wrapped around it.

---

## 7. Severity-classified gap list

| ID | Severity | Finding | Evidence |
|----|----------|---------|----------|
| P1 | **S1** | Advertised corpus (1,252 thm / 343 files / 96%) absent; repo has 6 thm / 2 files | §1, §2 |
| P2 | **S1** | "104 obligations / 32 files" fossilized from `aevion-shield` `lean_stats.py` | §2a |
| P3 | **S1** | README "Proven theorems" table: 5 of 7 not in repo | §3 |
| P4 | **S1 / RED** | Committed ML-DSA-65 **private key** in `aevion-shield` (cert root) | §8 |
| P5 | **S2** | Inflated metric (`1,252`) enforced as a CI pass condition | §4 |
| P6 | **S2 / RED** | "NIST published the proof" framing live on `aevion.ai`, RED-gated internally | §5.1 |
| P7 | **S2** | QGOV/Wukong tile names on public site vs `PUBLIC_RELEASE: HELD` | §5.2 |
| P8 | **S2** | Internal metric self-contradiction (1,252 vs 1,203; 96% vs 91%) | §2b |
| P9 | **S2** | Sole in-repo safety obligation is a `:= True` stub + a `sorry` | §1 |
| P10 | **S3** | `architecture.md` flagged "external comms" while carrying RED framing | §5.1 |
| P11 | **S3** | `quorum.md`/`paper.md` reference `colony.py`/eval harness absent from repo | §2 |

---

## 8. New RED finding — committed private signing key (aevion-shield)

Surfaced while crosswalking the ML-DSA-65 certificate scheme ProofOS's receipt-chain narrative depends on. **Not present in PR #144.**

- **File:** `aevion-shield/certificates/[REDACTED — owner-only]` (tracked in git; **not** gitignored; introduced in a single commit). *Exact path + commit withheld from this published copy; delivered out-of-band.*
- **Contents:** `algorithm: ML-DSA-65`, `public_key_hex` (1,952 bytes — correct ML-DSA-65 pk length) **and** `secret_key_hex` (**4,032 bytes — exactly the ML-DSA-65 secret-key length**).
- **Reality check (not a placeholder):** the `secret_key_hex` uses all 16 hex symbols with max single-symbol frequency 8.9% — genuine high-entropy key material, not a zero-fill or test stub. It sits beside `certificates/proof_receipts/`.
- **Why it matters:** ML-DSA-65 is the signature scheme behind Aevion's "proof certificate" / "court-admissible receipt" story. A committed secret key is **compromised by definition** — anyone with repo read access can forge any "signed" certificate under the affected key_id (`[REDACTED]`). This directly violates CLAUDE.md hard-prohibition *"add secrets"*.

**This report does not remediate it.** Key rotation and git-history scrub are destructive, cross-repo, RED-lane actions requiring owner clearance (`appr_scott_007`). Recommended (owner-gated): treat the affected key as compromised → rotate → re-issue affected certificates → purge from history (e.g. `git filter-repo`) → add `certificates/*keys*.json` to `.gitignore` → rotate any receipts that chain to it. **No autonomous action taken.** *(Exact path, commit, and key_id provided to the owner out-of-band.)*

---

## 9. Authority lanes

| Item | Lane | Owner action |
|------|------|--------------|
| This report + receipt (additive, audit-only) | `OWNER_REVIEW_QUEUE` | Review |
| P4 secret-key rotation (shield) | `CLEARANCE_REQUIRED` (RED) | `appr_scott_007` |
| P6 public-site NIST claim / RED-gated framing | `CLEARANCE_REQUIRED` (RED) | Owner + claim review |
| P1–P3, P5, P8 metric/README/CI correction | `OWNER_REVIEW_QUEUE` (YELLOW) | One session, pending decision |
| P7 quantum tile names on public site | `OWNER_REVIEW_QUEUE` (YELLOW) | KIRIN-FOLD-001 owner token |

Nothing in this audit merges to `main` without `appr_scott_007`. Draft PR only.

---

## 10. Required Engineering Output

1. **Breakthrough summary.** No novelty claimed. Newly executable: a ProofOS prose↔repo reconciliation that confirms the PR #144 cross-repo fossil hypothesis, plus a reproducible local Lean inventory (6 theorems / 2 files) against the advertised 1,252/343.
2. **Repo map.** ProofOS @ `11b7faa` — healthy 20-test runtime + 4 real Lean proofs, wrapped in a claims layer describing a corpus that lives in other repos; metrics + RED NIST framing already public via `aevion.ai`.
3. **Files changed.** 2 new files in ProofOS only: this report + `fresh_eyes_audit_proofos_receipt_20260610.json`. Zero modifications to existing files; no other repo touched.
4. **Commands run.** Lean inventory (`rg`/`wc` over `lean/`), `pytest tests/` → 20 passed, public-bundle string extraction (`grep -oE` over `docs/`), shield key-file inspection (length + entropy), `git ls-remote` (tags/HEAD), `git check-ignore`. Full list in the receipt.
5. **Tests / Lean results.** ProofOS `pytest tests/` = **20 passed**. Lean build **SKIPPED(env)** — elan release channel unreachable from this container, same environment limit recorded in PR #144; not a corpus statement. Static inventory used instead.
6. **Proof status.** Nothing proved by this audit (sorry/axiom delta = 0). In-repo state: 4 proved, 1 `:= True` stub, 1 `sorry`. The 1,252/343 corpus is **unverifiable in-repo** (absent).
7. **Artifacts & hashes.** See receipt `fresh_eyes_audit_proofos_receipt_20260610.json` (SHA-256 of this report + receipt recorded there).
8. **Claim hygiene.** This report makes no novelty/superiority claim; all advertised metrics quoted **QUOTED_AS_DATA**; DOI `10.1109/MSEC.2026.3678214` explicitly marked **unverified** rather than asserted true or false.
9. **DOT/SBIR relevance.** Submission-blocking. Any reviewer who clones ProofOS and runs `find lean -name '*.lean'` sees 2 files against a "1,252 theorem / 343 file" claim on the same page; the public `aevion.ai` site already carries the inflated metrics and an unverified NIST-endorsement framing. P1–P4 must be resolved before any external packet cites ProofOS.
10. **Next three tasks.** (a) Owner decision on metric correction — replace 1,252/343/104 everywhere with the in-repo `lean_stats.py` of *this* repo, and fix the Playwright assertion (YELLOW); (b) P4 secret-key rotation + history scrub in `aevion-shield` (RED — owner); (c) gate the public site behind the same claim-review the paper requires, and add a CI check that fails when a prose metric diverges from a live `lean_stats.py` scan of the repo it ships in.
11. **Authority lane.** `OWNER_REVIEW_QUEUE` overall; P4 and P6 are `CLEARANCE_REQUIRED`. Draft PR; nothing merges without `appr_scott_007`.

---

*Generated by the fresh-eyes audit method. Audit-only — no source files modified, no claims repaired, no keys rotated. INTERNAL_ONLY.*
