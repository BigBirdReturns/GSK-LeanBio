from pathlib import Path

import pytest

from bsl.parser import parse, parse_file
from bsl.typecheck import check, has_errors
from bsl.lean import emit_lean
from bsl.lexer import BSLError

EX = Path(__file__).resolve().parents[1] / "examples"


def test_mm_example_parses_and_checks():
    m = parse_file(EX / "B-michaelis-menten" / "model.bsl")
    assert m.name == "SubstrateConversion"
    convert = m.reactions[0]
    assert convert.rate_law == "michaelis_menten"
    assert convert.rate_param_names() == ["vmax", "km"]
    assert not has_errors(check(m)), [d.format() for d in check(m)]


def test_hill_example_parses_and_checks():
    m = parse_file(EX / "C-hill" / "model.bsl")
    bind = next(r for r in m.reactions if r.name == "bind")
    assert bind.rate_law == "hill"
    assert bind.rate_param_names() == ["kon", "kd"]
    # the Hill exponent is a literal, not a parameter
    literals = [a.value for a in bind.rate_args if a.value is not None]
    assert literals == [2.0]
    assert not has_errors(check(m)), [d.format() for d in check(m)]


def test_mm_requires_single_substrate():
    src = """model M {
      species A
      species B
      species C
      reaction r : A + B -> C @michaelis_menten(v, k)
      param v in [0.0, 1.0] @assumed
      param k in [0.0, 1.0] @assumed
    }"""
    codes = {d.code for d in check(parse(src))}
    assert "E_KINETICS_SUBSTRATE" in codes


def test_unknown_rate_law_rejected():
    with pytest.raises(BSLError):
        parse("model M { species A\n species B\n"
              " reaction r : A -> B @bogus(k)\n param k in [0,1] @assumed }")


def test_rate_law_arity_checked():
    with pytest.raises(BSLError):
        parse("model M { species A\n species B\n"
              " reaction r : A -> B @mass_action(a, b)\n"
              " param a in [0,1] @assumed\n param b in [0,1] @assumed }")


def test_mm_lean_flux():
    m = parse_file(EX / "B-michaelis-menten" / "model.bsl")
    lean = emit_lean(m)
    assert "p.vmax * x S / (p.km + x S)" in lean


def test_hill_lean_flux():
    m = parse_file(EX / "C-hill" / "model.bsl")
    lean = emit_lean(m)
    assert "x R ^ 2" in lean
