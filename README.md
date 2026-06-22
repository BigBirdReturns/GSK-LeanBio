# GSK-LeanBio

**The smallest honest version of the claim "we built a Lean for biology."**

[![lean-flagship](https://github.com/BigBirdReturns/GSK-LeanBio/actions/workflows/lean.yml/badge.svg)](https://github.com/BigBirdReturns/GSK-LeanBio/actions/workflows/lean.yml)

Kim Branson (Chief AI Officer, GSK) posted that GSK *"needed a 'Lean for
biology' … it didn't exist so we built it. Details to come,"* and clarified that
the methods can be shared — the data is the moat. Good. Then the method should be
externally checkable, because that is the entire source of Lean's authority:
**proof terms anyone can inspect, replay, and check outside the institution that
produced them, with zero dependency on the author.**

A "Lean for biology" claim therefore carries a specific burden — a formal
language, a proof checker, runnable examples, explicit assumptions, parameter
bounds, evidence grades, proof artifacts, and **no dependency on GSK
infrastructure**. This repo discharges that burden at minimum scale, built
independently and in the open, to test whether the claim survives Lean's own
standard.

**Open. Local. Model-relative. Assumption-bounded. Machine-checkable.**

See [`docs/THESIS.md`](docs/THESIS.md) for the full argument.

## What it proves — and the ceiling it exposes

It works: a biochemical model compiles to a kernel-checked theorem. The flagship,
checked by the Lean kernel in CI ([`lean/BslLean/ReversibleTwoSpecies.lean`](lean/BslLean/ReversibleTwoSpecies.lean)):

> For all rate constants `k1 ∈ [1,2]`, `k2 ∈ [3,4]`, any mass-conserving steady
> state of the reversible network `A ⇌ B` (total 10) has `A ∈ [6,8]` and
> `B ∈ [2,4]`.

And it exposes the ceiling, which is the actual finding: **formal certainty
attaches to the model statement, not to biological truth.** Biology's axioms are
provisional, its parameters uncertain, its evidence graded. Lean does not erase
that — it makes the boundary explicit. The honest "Lean for biology" is
model-relative proof under stated assumptions, and nothing more.
See [`docs/limitations.md`](docs/limitations.md).

## Verify it yourself

No GSK infrastructure, no account, nothing fetched beyond Lean + Mathlib.

```bash
git clone https://github.com/BigBirdReturns/GSK-LeanBio
cd GSK-LeanBio

# zero-dependency: parse / typecheck / emit evidence-bound claims / emit Lean
python -m bsl check   examples/A-enzyme-kinetics/model.bsl
python -m bsl compile examples/A-enzyme-kinetics/model.bsl --out out/enzyme

# real Lean kernel checks (needs a Lean 4 toolchain, or use the Dockerfile)
python -m bsl verify  examples/D-linear-pathway/model.bsl   # parameter-bounded flux band
python -m bsl certify examples/E-reversible/model.bsl --lean-out lean/BslLean/Generated
```

The ℝ-valued flagship is kernel-checked on every push by GitHub Actions
(`lake exe cache get` → `lake build`, asserting the `.olean` is produced and the
source is `sorry`-free). Click the badge; read the log. That is the standard:
not "trust me," but "run it."

## How it works

- **BSL** (Biological Specification Language): a tiny DSL for biochemical models
  — mass-action, Michaelis–Menten, Hill kinetics; interval-bounded parameters;
  conservation invariants. Parser + physical-invariant typechecker, pure Python.
- **Evidence-bound claims**: every fact traces to exact bytes of the `.bsl`
  source and is confidence-graded by how it was justified
  (`DERIVED_FROM_EXPERIMENT` / `LITERATURE_CONSENSUS` / `ASSUMED_FOR_MODELING`).
- **`bsl verify`**: emits core-only obligations (conservation, steady-state flux
  bounds) and runs Lean's `omega` to discharge — or *refute, with a
  counterexample* — them. No Mathlib required.
- **`bsl certify`**: recognizes the one verified network class and instantiates
  the ℝ-valued steady-state schema as a Lean theorem; **fails closed** (precise
  reason, no Lean emitted) on anything outside the certified subset.
- **`lean/`**: the Mathlib-backed flagship, kernel-checked in CI.

## Status

| Capability | State |
|---|---|
| BSL parser — mass-action, Michaelis–Menten, Hill kinetics | working |
| Typechecker — non-negative conc/rates, mass-balance refs, intervals, kinetics arity | working |
| Evidence-bound, confidence-graded claims | working |
| Conservation + steady-state flux proofs (`bsl verify`, Lean `omega`) | working — real kernel check |
| Certified-subset recognizer + schema instantiation (`bsl certify`, fail-closed) | working |
| **Flagship: ∀-parameter-interval steady-state bound (ℝ, Mathlib)** | **kernel-checked in CI** |
| PK/PD, Boolean networks, CTMC / stochastic, SBML import | not built — see [THESIS](docs/THESIS.md) |

## Provenance

Built rapidly and in the open with AI assistance; the commit history shows
co-authorship. That is consistent with the point, not against it: if the honest
version of "Lean for biology" is a few days' work for one person, the method was
never the hard part or the moat — which is what the claim's author said too.

## Not affiliated with GSK

Independent work. **Not affiliated with, endorsed by, or derived from GSK** or
any GSK product or internal tool. "GSK," "Lean," and the referenced post are
named for identification and for commentary on a public statement. The critique
is of the public *claim* and its verification burden — conditional on whether the
framework ships — not of any individual.

## License

Apache-2.0
