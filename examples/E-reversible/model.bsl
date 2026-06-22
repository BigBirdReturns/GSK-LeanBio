# Example E — Reversible two-species mass action (the certified flagship class)
#
# `bsl certify` recognises this pattern and instantiates the verified
# steady-state schema, emitting a Lean theorem that CI kernel-checks. Parameters
# match the flagship (kf∈[1,2], kr∈[3,4], total 10) so the generated proof is
# the same shape already verified by hand.

model ReversibleAB {
  species A @init 6.0
  species B @init 4.0

  reaction forward : A -> B @mass_action(kf)
  reaction reverse : B -> A @mass_action(kr)

  param kf in [1.0, 2.0] @literature(citations=7)
  param kr in [3.0, 4.0] @experiment(replicates=5, p=0.01)

  invariant total_mass : A + B = 10.0
}
