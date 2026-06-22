# Example D — Open linear pathway at steady state (certified flux bound)
#
# A zeroth-order influx feeds A; A converts to B; B leaves the system. At steady
# state every internal flux equals the influx, so the efflux flux inherits the
# influx's measured interval. This is a parameter-bounded steady-state result:
# the uncertainty on the influx rate propagates to a certified flux band, proved
# by Lean.

model LinearPathway {
  species A @init 0.0
  species B @init 0.0

  reaction influx :  -> A   @mass_action(vin)   # zeroth-order source
  reaction step   : A -> B  @mass_action(k1)
  reaction efflux : B ->    @mass_action(k2)    # sink

  param vin in [10.0, 20.0] @experiment(replicates=4, p=0.01)
  param k1  in [1.0, 5.0]   @literature(citations=6)
  param k2  in [1.0, 5.0]   @assumed

  steady_state
  property efflux_in_band : flux(efflux) in [10.0, 20.0]
}
