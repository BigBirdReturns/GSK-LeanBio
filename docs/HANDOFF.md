# HANDOFF — building the real version

Audience: a fresh agent picking this up cold. Read this fully before writing code.
This repo (`GSK-LeanBio`) is **done as what it is** — a demonstration. This doc is
about the *next* thing: the narrow, actually-useful vertical.

---

## 0. The one-paragraph orientation

`GSK-LeanBio` exists to test a public claim ("we built a Lean for biology") against
Lean's own standard — open, local, machine-checkable. It succeeds at that and, in
doing so, exposes the ceiling: **formal proof certifies the model under stated
assumptions, never biological truth.** That ceiling means *general* "formal
verification for biology" has no demonstrated user and a structural value mismatch
(formal methods pay where the spec is exact and error is catastrophic — crypto,
avionics, silicon; biology is the opposite). So **do not build a broader version of
this repo.** The real product is a *narrow* vertical where the spec genuinely is
exact and error genuinely is catastrophic. That is what this handoff scopes.

Don't relitigate the above — it was the hard-won conclusion of a long process. If
you think the general thing is valuable, you are about to repeat the exact mistake
this repo was built to expose.

---

## 1. The pivot: what "the real version" is

**Lead vertical — PK/PD safety-bound certificates for Model-Informed Drug
Development (MIDD).** This is the one place the pattern fits:
- The spec is exact: an exposure **safety threshold** (`C_plasma ≤ C_toxic`), or a
  **therapeutic window** (`C_trough ≥ C_efficacy ∧ C_max ≤ C_toxic`).
- The error is catastrophic: toxicity / loss of efficacy.
- The model is a **compartment ODE** — decades of validation, well understood.
- The parameters are **fitted with known uncertainty** (a confidence interval).
- The decision is **legible and regulatory**: can we justify this dose for all
  parameter values in the fitted CI?

**Cross-cutting substrate — the provenance/audit layer.** Arguably more valuable than
the proof itself: record model version, data source, estimation method, confidence
grade, theorem statement, proof hash, validation mismatch, assumption changes. Useful
even when the proof is modest. ("Who claimed what, from which data, under which
assumptions, and what changed after validation" is a real regulated-science pain
point.) The AXM/`candidates.jsonl` → signed-shard seam already sketches this.

**Optional 2nd vertical — MEC-6 (GLP-1 discontinuation), documentation only.** See §6;
it carries a hard safety guardrail.

> Decision the next agent should confirm, not assume: PK/PD is the recommended lead.
> If the owner wants MEC-6 instead, the guardrails in §6 are mandatory.

---

## 2. The discipline that has to survive the pivot

Carry these or you will rebuild the same overclaim:
1. **Real ≠ valuable.** A kernel-checked theorem proves the *machine* works, not that
   anyone needs it. Name the **user and the decision a green check changes**, or stop
   at portfolio. (For PK/PD: a pharmacometrics / quantitative-clinical-pharmacology
   lead preparing an FDA MIDD package; the decision is dose justification / safety
   margin / avoiding a dedicated study.)
2. **Build and user-discovery run in parallel.** Do not build the whole vertical before
   one real pharmacometrician tells you whether a Lean certificate changes their
   review/submission. Their current workflow (NONMEM/Monolix + simulation) already
   "works"; regulators do not currently *demand* machine-checked proofs. The open
   question is adoption, not feasibility.
3. **Stay model-relative and conditional.** "For all parameters in the stated interval,
   the model cannot cross the declared bound." Never "the drug is safe." The proof is
   about the model, not the patient.
4. **Verify-it-yourself is the standard.** Open, local, reproducible, CI-checked. No
   "trust me," no proprietary-infra dependency. That is the whole point.

---

## 3. What already exists — reuse, don't rebuild

| Piece | Where | Status |
|---|---|---|
| BSL DSL (mass-action/MM/Hill, interval params, conservation) | `bsl/` | working, pure Python |
| Physical-invariant typechecker | `bsl/typecheck.py` | working |
| Evidence-bound, confidence-graded claims | `bsl/candidates.py` | working |
| `bsl verify` — conservation + steady-state flux, Lean core `omega` | `bsl/verify.py`, `bsl/lean/verify_emit.py` | working, refutes false claims |
| `bsl certify` — certified-subset recognizer + ℝ schema instantiation, fail-closed | `bsl/certify.py` | working |
| Flagship ℝ proof (parameter-bounded steady state) | `lean/BslLean/ReversibleTwoSpecies.lean` | kernel-checked in CI |
| Mathlib-in-CI pattern | `.github/workflows/lean.yml` | green (runs #1, #2) |
| Provenance seam (`candidates.jsonl` → optional signed shard) | `bsl/emit/` | port + stub adapter |

The `certify.py` "recognize a class → compute tight bounds → emit a Lean instance of a
verified schema → fail closed otherwise" pattern is the template for the PK/PD work.
Copy its shape.

---

## 4. Hard-won technical lessons (do not relearn these the slow way)

- **Mathlib will not build in a restricted sandbox.** Its prebuilt `.olean` cache is
  firewalled in this dev environment (HTTP 403 on every object); a from-source build is
  hours. **Kernel-check ℝ/Mathlib proofs in CI on GitHub runners** (open network) via
  `lake exe cache get` → `lake build`. Lean *core* (`omega`, `decide`, `native_decide`)
  runs anywhere — use it for anything linear/finite.
- **The omega/Mathlib boundary is the whole game.** Conservation and *flux* bounds stay
  linear → `omega`, no Mathlib. *Concentration* bounds need ℝ, division, and nonlinear
  arithmetic → `nlinarith`/`field_simp` → Mathlib. PK/PD concentration/exposure bounds
  are the Mathlib kind.
- **Schema, not models.** Hardcode one verified theorem class; a recognizer instantiates
  it for any conforming model; **fail closed** (precise reason, no Lean emitted) on
  everything else. This is the line between "I proved one toy" and "a system."
- **Tight interval bounds are provable** (the `≤` is achieved at a box corner). Compute
  them as exact rationals in the generator; emit literals; let `nlinarith` close it.
- **Robust proof template:** implicit formulation (variables satisfying the model
  equations ⇒ bounds), `linear_combination` for the algebraic identity, `nlinarith` for
  the inequalities, `linarith` for the leftovers. See `ReversibleTwoSpecies.lean`.
- **CI is the authority, not the agent.** You cannot see the kernel verdict locally
  (no Mathlib). Push, read the run, fix on red. Keep a `sorry`/`admit` grep gate in CI.

---

## 5. Concrete first build (PK/PD)

Do **not** start with a single IV bolus — `C(t) = C0·e^(−k_e·t)` decays, so its max is
just `C0`; the "safety bound" collapses to `C0 ≤ T` and proves nothing interesting (same
triviality trap as the reversible toy).

Start with the smallest **non-trivial** case: **constant infusion to steady state.**

```
Continuous infusion rate R, one compartment:
  C(t) = (R / CL) · (1 − exp(−k_e · t)),   CL = k_e · V
  k_e ∈ [ke_lo, ke_hi],  V ∈ [V_lo, V_hi],  all > 0,  R > 0,  threshold T

Theorem (Mathlib):
  for all k_e, V in those intervals, for all t ≥ 0,
    C(t) ≤ T
  given the certificate condition  R / (ke_lo · V_lo) ≤ T.
```

Why it's the right first target: `C(t) ≤ C_ss = R/(k_e·V)` because `1 − exp(−k_e·t) ≤ 1`
(`Real.exp_nonneg`); and `R/(k_e·V) ≤ R/(ke_lo·V_lo)` by product + division monotonicity
of positives. Same toolkit as the flagship (`nlinarith`, positivity, division). Real,
non-trivial, parameter-bounded, and it maps to an actual exposure-safety question.

Then, in order:
1. **Repeated-dose accumulation / therapeutic window:** `C_max,ss` and `C_trough,ss` for
   a fixed schedule; prove `C_trough ≥ C_eff ∧ C_max ≤ C_tox` for all params in the CI.
   This is the real MIDD claim. (Sum-of-exponentials; bounded horizon; still Mathlib.)
2. **The recognizer + certificate report.** Mirror `certify.py`: classify a
   one-compartment, first-order, constant-input model with parameter intervals + a
   threshold; emit the Lean instance; **fail closed** on multi-compartment, nonlinear
   elimination, time-varying input, etc., each with a precise reason.
3. **The MIDD-style report artifact:** theorem statement, assumptions, **parameter
   provenance** (which fit, which dataset, which method, which CI), proof hash,
   model-risk note, validation hook. This is where the provenance substrate (§1) plugs in.

---

## 6. MEC-6 (only if chosen) — mandatory guardrails

MEC-6 (GLP-1 discontinuation "clearance") is, by its own header, a **proposed framework
pending validation**. Software that gates whether a real patient may stop a medication is
**clinical decision support** — regulated, liability-bearing, safety-critical.

- **Build it ONLY as documentation / evidence-map / audit / provenance**, plus optional
  PK/PD steady-state simulation for *this patient's* dosing (the one place a real bound
  helps: e.g. "time to sub-therapeutic exposure after a missed dose").
- **Do NOT build a "PASS/FAIL — safe to discontinue" verdict engine.** The clinician
  decides; the tool documents *what was considered, from which evidence, what was missing,
  and what the clinician overrode.* Ship the audit trail, never the verdict.

---

## 7. What NOT to do

- Don't chase SBML/BioModels breadth. Ingesting more approximate models proves you can
  ingest approximate models; no decision changes.
- Don't build a general "prove biology" framework. That's the dead end this repo exposed.
- Don't ship clinical verdicts (see §6).
- Don't build the distributed worker-pool / plugin-runtime / "generic verification job"
  infrastructure. It was never on the critical path for a single useful check.
- Don't overclaim against GSK. The critique is structural and conditional ("publish the
  framework or it was branding"), never a claim about a person's intent or about what does
  or doesn't exist inside GSK. Keep the non-affiliation disclaimer.

---

## 8. Repo state at handoff

- Default work branch: `claude/cool-edison-texasb`; open PR **#1** into `main`.
- Two green Lean CI runs on record (flagship + generated instance).
- Public framing lives in `README.md` and `docs/THESIS.md`; limits in `docs/limitations.md`.
- Open reconciliation items for the **owner** (not an agent task): confirm the public link
  (`jonathansandhu/GSK-LeanBio`) resolves to the repo holding this work
  (`BigBirdReturns/GSK-LeanBio`), and that PR #1 is merged so the exhibit is on the default
  branch. Swap badge/clone owner in `README.md` if the canonical owner differs.

---

## 9. First move for the next agent

Build §5 step 0 (infusion-to-steady-state safety bound) as a new Mathlib flagship in
`lean/`, kernel-checked in CI, in a `Bio/PKPD/` namespace. Keep `GSK-LeanBio`'s demo
intact and unmodified — the new vertical is additive, and ideally its own repo once it has
legs. In parallel, write the one-paragraph question for a real pharmacometrician: *"Would a
machine-checked certificate that your model's exposure stays below threshold for all
parameters in your fitted CI change anything about your MIDD package or review?"* If the
answer is no, stop and report that — it's the most valuable finding available.
