import Mathlib

/-!
# Flagship: parameter-bounded steady state of a reversible two-species network

Reaction network:  `A ⇌ B`,  with  `A → B` at rate `k1 * A`  and  `B → A` at
rate `k2 * B`.

This is the smallest biochemical network that exhibits the headline claim — a
*parameter-bounded steady-state* property — and it does so **algebraically**, with
no ODE solving. Any state `(A, B)` that conserves mass (`A + B = 10`) and sits at
steady state (`k1 * A = k2 * B`) has its concentrations pinned to certified
intervals, for ALL rate constants in the assumed ranges.

This is a machine-checked proof of MODEL CONSISTENCY under explicitly stated,
bounded assumptions. It is not a claim about biological ground truth: the model
equations (`hmass`, `hss`) and the parameter ranges are hypotheses, and the
theorem says only that the conclusion follows from them.

Checked by the Lean kernel via Mathlib; see `.github/workflows/lean.yml`.
-/

namespace BSL.ReversibleTwoSpecies

/-- For every pair of rate constants `k1 ∈ [1,2]`, `k2 ∈ [3,4]`, any
mass-conserving (`A + B = 10`) steady state (`k1 * A = k2 * B`) of the reversible
network `A ⇌ B` satisfies `A ∈ [6,8]` and `B ∈ [2,4]`. -/
theorem steady_state_bounds
    (k1 k2 A B : ℝ)
    (hk1lo : 1 ≤ k1) (hk1hi : k1 ≤ 2)
    (hk2lo : 3 ≤ k2) (hk2hi : k2 ≤ 4)
    (hmass : A + B = 10)
    (hss : k1 * A = k2 * B) :
    6 ≤ A ∧ A ≤ 8 ∧ 2 ≤ B ∧ B ≤ 4 := by
  have hpos : 0 < k1 + k2 := by linarith
  -- Eliminate B via mass conservation: (k1 + k2) * A = 10 * k2.
  have hsum : (k1 + k2) * A = 10 * k2 := by linear_combination hss + k2 * hmass
  -- Lower/upper bounds on A follow by multiplying through by (k1 + k2) > 0.
  have hA6 : 6 ≤ A := by nlinarith [hsum, hpos, hk1hi, hk2lo]
  have hA8 : A ≤ 8 := by nlinarith [hsum, hpos, hk1lo, hk2hi]
  -- B bounds are then linear, via A + B = 10.
  refine ⟨hA6, hA8, ?_, ?_⟩ <;> linarith

end BSL.ReversibleTwoSpecies
