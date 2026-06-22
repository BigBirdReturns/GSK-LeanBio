"""Certified-subset recognizer + Lean instantiator.

This is the demo->system step: instead of hand-writing one proof, we hardcode a
*theorem schema* (the verified reversible two-species mass-action steady state,
see `lean/BslLean/ReversibleTwoSpecies.lean`) and instantiate it for any model
that fits the certified subset. Anything outside the subset fails closed with a
precise reason and emits no Lean — that is how the system stays honest.

Certified subset (v0): exactly two species `A`, `B`; exactly two unit-stoichiometry
mass-action reactions forming an inverse pair `A -> B` and `B -> A`; a declared
conservation invariant `A + B = M`; strictly positive rate-constant lower bounds.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .nodes import Model


class Unsupported(Exception):
    """Raised when a model is outside the certified subset (fail closed)."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass
class ReversiblePattern:
    sp_a: str
    sp_b: str
    kf: str            # forward rate-constant parameter
    kr: str            # reverse rate-constant parameter
    M: Fraction
    kf_lo: Fraction
    kf_hi: Fraction
    kr_lo: Fraction
    kr_hi: Fraction


def _frac(x: float) -> Fraction:
    return Fraction(x).limit_denominator(10**6)


def classify(model: Model) -> ReversiblePattern:
    if len(model.species) != 2:
        raise Unsupported("UnsupportedConstruct",
                          f"expected 2 species, found {len(model.species)}")
    if len(model.reactions) != 2:
        raise Unsupported("UnsupportedConstruct",
                          f"expected 2 reactions, found {len(model.reactions)}")

    for r in model.reactions:
        if r.rate_law != "mass_action":
            raise Unsupported("UnsupportedKineticLaw",
                              f"reaction {r.name!r} uses {r.rate_law}, "
                              f"expected mass_action")
        if len(r.reactants) != 1 or len(r.products) != 1:
            raise Unsupported("UnsupportedConstruct",
                              f"reaction {r.name!r} is not single-reactant/"
                              f"single-product")
        if r.reactants[0].coeff != 1 or r.products[0].coeff != 1:
            raise Unsupported("UnsupportedConstruct",
                              f"reaction {r.name!r} has non-unit stoichiometry")

    r1, r2 = model.reactions
    a1, b1 = r1.reactants[0].species, r1.products[0].species
    a2, b2 = r2.reactants[0].species, r2.products[0].species
    if not (a1 == b2 and b1 == a2 and a1 != b1):
        raise Unsupported("UnsupportedConstruct",
                          "reactions are not an inverse pair A ⇌ B")
    sp_a, sp_b = a1, b1
    kf, kr = r1.rate_args[0].name, r2.rate_args[0].name
    if kf is None or kr is None:
        raise Unsupported("UnsupportedKineticLaw",
                          "rate constants must be declared parameters")

    M = None
    for inv in model.invariants:
        terms = {t.species: t.coeff for t in inv.terms}
        if set(terms) == {sp_a, sp_b} and terms[sp_a] == 1 and terms[sp_b] == 1:
            M = _frac(inv.rhs)
            break
    if M is None:
        raise Unsupported("MissingConservationLaw",
                          f"need an invariant {sp_a} + {sp_b} = M")

    pmap = {p.name: p for p in model.params}
    if kf not in pmap or kr not in pmap:
        raise Unsupported("UnsupportedConstruct",
                          "rate parameters are not declared")
    pf, pr = pmap[kf], pmap[kr]
    if not (pf.lo > 0 and pr.lo > 0):
        raise Unsupported("CannotProvePositiveDenominator",
                          "rate-constant lower bounds must be strictly positive")

    return ReversiblePattern(
        sp_a=sp_a, sp_b=sp_b, kf=kf, kr=kr, M=M,
        kf_lo=_frac(pf.lo), kf_hi=_frac(pf.hi),
        kr_lo=_frac(pr.lo), kr_hi=_frac(pr.hi),
    )


def certified_bounds(p: ReversiblePattern):
    """Tight steady-state intervals. A* = M·kr/(kf+kr) is increasing in kr and
    decreasing in kf, so its extremes sit at opposite corners of the box."""
    a_lo = p.M * p.kr_lo / (p.kf_hi + p.kr_lo)
    a_hi = p.M * p.kr_hi / (p.kf_lo + p.kr_hi)
    b_lo = p.M - a_hi
    b_hi = p.M - a_lo
    return a_lo, a_hi, b_lo, b_hi


def _lit(x: Fraction) -> str:
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"({x.numerator} / {x.denominator} : ℝ)"


def emit_lean_instance(model: Model, p: ReversiblePattern | None = None) -> str:
    p = p or classify(model)
    a_lo, a_hi, b_lo, b_hi = certified_bounds(p)
    A, B = p.sp_a, p.sp_b
    M = _lit(p.M)
    L = [
        "import Mathlib",
        "",
        f"/- Auto-generated from {model.source.name} by `bsl certify`. -/",
        "/- Instance of the verified reversible two-species mass-action schema",
        "   (see BslLean.ReversibleTwoSpecies). Kernel-checked in CI. -/",
        f"namespace BSL.Generated.{model.name}",
        "",
        f"theorem steady_state_bounds (kf kr {A} {B} : ℝ)",
        f"    (hkf_lo : {_lit(p.kf_lo)} ≤ kf) (hkf_hi : kf ≤ {_lit(p.kf_hi)})",
        f"    (hkr_lo : {_lit(p.kr_lo)} ≤ kr) (hkr_hi : kr ≤ {_lit(p.kr_hi)})",
        f"    (hmass : {A} + {B} = {M})",
        f"    (hss : kf * {A} = kr * {B}) :",
        f"    {_lit(a_lo)} ≤ {A} ∧ {A} ≤ {_lit(a_hi)} ∧ "
        f"{_lit(b_lo)} ≤ {B} ∧ {B} ≤ {_lit(b_hi)} := by",
        "  have hpos : 0 < kf + kr := by linarith",
        f"  have hsum : (kf + kr) * {A} = {M} * kr := by "
        f"linear_combination hss + kr * hmass",
        f"  have hAlo : {_lit(a_lo)} ≤ {A} := by "
        f"nlinarith [hsum, hpos, hkf_lo, hkf_hi, hkr_lo, hkr_hi]",
        f"  have hAhi : {A} ≤ {_lit(a_hi)} := by "
        f"nlinarith [hsum, hpos, hkf_lo, hkf_hi, hkr_lo, hkr_hi]",
        "  refine ⟨hAlo, hAhi, ?_, ?_⟩ <;> linarith",
        "",
        f"end BSL.Generated.{model.name}",
        "",
    ]
    return "\n".join(L)
