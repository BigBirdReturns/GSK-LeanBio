# Example C — Cooperative ligand binding (Hill kinetics)
# R <-> RL with cooperative (Hill, n=2) association; total receptor conserved.

model CooperativeBinding {
  species R  @init 1.0      # free receptor (total normalised to 1.0)
  species RL @init 0.0      # ligand-bound receptor

  reaction bind   : R -> RL @hill(kon, kd, 2)   # cooperative association (n = 2)
  reaction unbind : RL -> R @mass_action(koff)  # dissociation

  param kon  in [1.0, 3.0]   @literature(citations=5)
  param kd   in [0.4, 0.6]   @experiment(replicates=3, p=0.05)
  param koff in [0.05, 0.15] @assumed

  # Receptors are neither created nor destroyed: d/dt (R + RL) = 0.
  invariant receptor_conservation : R + RL = 1.0
}
