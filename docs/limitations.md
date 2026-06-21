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

Not yet:

- **Running the ℝ-valued ODE proofs.** `bsl verify` discharges conservation over
  the integers (the structural, kinetics-independent statement) using Lean core.
  The richer `bsl lean` output — the real-valued vector field with existence /
  uniqueness and the `ring`-closed conservation theorem — needs a Mathlib build
  and is currently emit-only.
- **Sealing** candidates into a signed Genesis shard. The `GenesisEmitter`
  adapter is a stub that docks the AXM kernel when it is installed.
- **PK/PD** compartment models and **Boolean** networks.
- **Stochastic semantics** (CTMC / CME / SDE). The report sketches these; they
  are research-scale and explicitly out of v0.1.

## Confidence numbers are placeholders

The mapping from grade to a confidence float (`experiment → 0.95`, etc.) is a
stand-in. Turning replicate counts, p-values, and citation counts into
calibrated confidence is the parameter-oracle layer, and it is not built yet.
