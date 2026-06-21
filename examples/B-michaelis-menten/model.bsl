# Example B — Michaelis-Menten conversion (reduced single-substrate kinetics)
# S -> P with saturating enzyme kinetics; total mass S + P is conserved.

model SubstrateConversion {
  species S @init 100.0     # substrate
  species P @init 0.0       # product

  reaction convert : S -> P @michaelis_menten(vmax, km)

  param vmax in [0.8, 1.2]  @experiment(replicates=4, p=0.02)   # umol/s
  param km   in [5.0, 15.0] @literature(citations=8)            # umol

  # Substrate is converted to product one-for-one: d/dt (S + P) = 0.
  invariant mass_conservation : S + P = 100.0
}
