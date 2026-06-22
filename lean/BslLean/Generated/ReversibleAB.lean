import Mathlib

/- Auto-generated from model.bsl by `bsl certify`. -/
/- Instance of the verified reversible two-species mass-action schema
   (see BslLean.ReversibleTwoSpecies). Kernel-checked in CI. -/
namespace BSL.Generated.ReversibleAB

theorem steady_state_bounds (kf kr A B : ℝ)
    (hkf_lo : 1 ≤ kf) (hkf_hi : kf ≤ 2)
    (hkr_lo : 3 ≤ kr) (hkr_hi : kr ≤ 4)
    (hmass : A + B = 10)
    (hss : kf * A = kr * B) :
    6 ≤ A ∧ A ≤ 8 ∧ 2 ≤ B ∧ B ≤ 4 := by
  have hpos : 0 < kf + kr := by linarith
  have hsum : (kf + kr) * A = 10 * kr := by linear_combination hss + kr * hmass
  have hAlo : 6 ≤ A := by nlinarith [hsum, hpos, hkf_lo, hkf_hi, hkr_lo, hkr_hi]
  have hAhi : A ≤ 8 := by nlinarith [hsum, hpos, hkf_lo, hkf_hi, hkr_lo, hkr_hi]
  refine ⟨hAlo, hAhi, ?_, ?_⟩ <;> linarith

end BSL.Generated.ReversibleAB
