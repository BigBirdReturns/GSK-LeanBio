# Limitations — what GSK-LeanBio does not do

This tool is deliberately scoped. Being honest about the boundary is part of the
design.

## It proves consistency, not truth

A passing model and a discharged Lean proof mean: *given the stated axioms and
parameter intervals, the conclusion follows.* They do not mean the model matches
biology. Every claim is graded by how it was justified
(`DERIVED_FROM_EXPERIMENT` / `LITERATURE_CONSENSUS` / `ASSUMED_FOR_MODELING`),
and that grade rides with the claim — precisely so a downstream consumer can see
which conclusions rest on measurement and which rest on assumption.

## Current functional boundary (v0.1)

Works:

- BSL parsing for mass-action, Michaelis–Menten, and Hill kinetics, with
  interval-bounded parameters and conservation invariants.
- Physical-invariant typechecking (non-negative concentrations and rate
  constants, well-formed stoichiometry, declared-symbol resolution, non-empty
  intervals, single-substrate arity for saturating kinetics).
- Evidence-bound, confidence-graded claim candidates (the AXM seam).
- A standalone unsigned bundle (`FileSink`).
- Lean 4 emission of the ODE vector field (`bsl lean`).
- **Discharging conservation laws with a real Lean kernel check** (`bsl verify`).
  Each invariant becomes a flux-abstract stoichiometric obligation closed by
  `omega` in Lean core — and a false invariant is *refuted* with a
  counterexample, not silently accepted.
- **Parameter-bounded steady-state flux bounds** (`bsl verify` with a
  `steady_state` declaration and `property p : flux(r) in [lo, hi]`). An
  interval-bounded influx propagates through steady-state flux balance to a
  certified interval on a downstream flux, closed by `omega`; a too-tight band
  is refuted.

Not yet:

- **Nonlinear, real-valued parameter bounds — written, CI-checked, not sandbox-checked.**
  `bsl verify` proves conservation and steady-state *flux* bounds over the
  integers with Lean core (`omega`). The flagship "∀ k ∈ [a,b], steady-state
  *concentration* ∈ [c,d]" needs ℝ, division, and nonlinear arithmetic — i.e.
  Mathlib. That proof now exists, for the reversible two-species network `A ⇌ B`,
  in [`lean/BslLean/ReversibleTwoSpecies.lean`](../lean/BslLean/ReversibleTwoSpecies.lean):

  > For every `k1 ∈ [1,2]`, `k2 ∈ [3,4]`, any mass-conserving steady state of
  > `A ⇌ B` (total 10) has `A ∈ [6,8]` and `B ∈ [2,4]`.

  It is kernel-checked in CI (`.github/workflows/lean.yml`: `lake exe cache get`
  → `lake build`), because GitHub-hosted runners can reach Mathlib's prebuilt
  `.olean` cache. In the restricted dev sandbox that cache is firewalled (HTTP
  403 on every object) and a from-source build is hours of compute, so this proof
  is **not** kernel-checked there — the CI run is the authority. The `bsl lean`
  output (the ℝ-valued vector field) remains emit-only.
- **Sealing** candidates into a signed Genesis shard. The `GenesisEmitter`
  adapter is a stub that docks the AXM kernel when it is installed.
- **PK/PD** compartment models and **Boolean** networks.
- **Stochastic semantics** (CTMC / CME / SDE). The report sketches these; they
  are research-scale and explicitly out of v0.1.

## Confidence numbers are placeholders

The mapping from grade to a confidence float (`experiment → 0.95`, etc.) is a
stand-in. Turning replicate counts, p-values, and citation counts into
calibrated confidence is the parameter-oracle layer, and it is not built yet.
