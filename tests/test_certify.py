from fractions import Fraction
from pathlib import Path

import pytest

from bsl.parser import parse, parse_file
from bsl.certify import classify, certified_bounds, emit_lean_instance, Unsupported

EX = Path(__file__).resolve().parents[1] / "examples"


def test_classify_reversible_example():
    p = classify(parse_file(EX / "E-reversible" / "model.bsl"))
    assert {p.sp_a, p.sp_b} == {"A", "B"}
    assert (p.kf, p.kr) == ("kf", "kr")
    assert p.M == 10
    assert (p.kf_lo, p.kf_hi) == (1, 2)
    assert (p.kr_lo, p.kr_hi) == (3, 4)


def test_certified_bounds_match_flagship():
    p = classify(parse_file(EX / "E-reversible" / "model.bsl"))
    a_lo, a_hi, b_lo, b_hi = certified_bounds(p)
    assert (a_lo, a_hi, b_lo, b_hi) == (6, 8, 2, 4)


def test_emitted_instance_is_flagship_shaped():
    m = parse_file(EX / "E-reversible" / "model.bsl")
    lean = emit_lean_instance(m)
    assert "theorem steady_state_bounds" in lean
    assert "linear_combination hss + kr * hmass" in lean
    assert "nlinarith" in lean
    assert "6 ≤ A ∧ A ≤ 8 ∧ 2 ≤ B ∧ B ≤ 4" in lean
    assert "sorry" not in lean


def test_fractional_bounds_emit_rationals():
    # kf∈[1,1], kr∈[1,2], M=1  ->  A* = kr/(1+kr) ∈ [1/2, 2/3]
    src = """model Frac {
      species A @init 0.5
      species B @init 0.5
      reaction f : A -> B @mass_action(kf)
      reaction r : B -> A @mass_action(kr)
      param kf in [1.0, 1.0] @assumed
      param kr in [1.0, 2.0] @assumed
      invariant tot : A + B = 1.0
    }"""
    p = classify(parse(src))
    a_lo, a_hi, _, _ = certified_bounds(p)
    assert a_lo == Fraction(1, 2) and a_hi == Fraction(2, 3)
    assert "(1 / 2 : ℝ)" in emit_lean_instance(parse(src), p)


def test_fail_closed_michaelis_menten():
    with pytest.raises(Unsupported) as e:
        classify(parse_file(EX / "B-michaelis-menten" / "model.bsl"))
    assert e.value.code in {"UnsupportedConstruct", "UnsupportedKineticLaw"}


def test_fail_closed_missing_conservation():
    src = """model NoCons {
      species A @init 1.0
      species B @init 0.0
      reaction f : A -> B @mass_action(kf)
      reaction r : B -> A @mass_action(kr)
      param kf in [1.0, 2.0] @assumed
      param kr in [1.0, 2.0] @assumed
    }"""
    with pytest.raises(Unsupported) as e:
        classify(parse(src))
    assert e.value.code == "MissingConservationLaw"


def test_fail_closed_nonpositive_rate():
    src = """model ZeroRate {
      species A @init 1.0
      species B @init 0.0
      reaction f : A -> B @mass_action(kf)
      reaction r : B -> A @mass_action(kr)
      param kf in [0.0, 2.0] @assumed
      param kr in [1.0, 2.0] @assumed
      invariant tot : A + B = 1.0
    }"""
    with pytest.raises(Unsupported) as e:
        classify(parse(src))
    assert e.value.code == "CannotProvePositiveDenominator"
