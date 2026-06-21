# Example A — Enzyme kinetics (single substrate, mass-action mechanism)
# E + S <-> ES -> E + P, written as elementary mass-action reactions.

model EnzymeKinetics {
  species E  @init 1.0      # free enzyme (total enzyme normalised to 1.0)
  species S  @init 10.0     # substrate
  species ES @init 0.0      # enzyme-substrate complex
  species P  @init 0.0      # product

  reaction binding   : E + S -> ES   @mass_action(kf)
  reaction unbinding : ES -> E + S   @mass_action(kr)
  reaction catalysis : ES -> E + P   @mass_action(kcat)

  param kf   in [9.0e5, 1.1e6]  @literature(citations=12)
  param kr   in [0.18, 0.22]    @assumed
  param kcat in [0.09, 0.11]    @experiment(replicates=3, p=0.01)

  # Total enzyme is conserved: d/dt (E + ES) = 0.
  invariant enzyme_conservation : E + ES = 1.0
}
