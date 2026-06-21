from pathlib import Path

import pytest

from bsl.parser import parse, parse_file
from bsl.lexer import BSLError

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "A-enzyme-kinetics" / "model.bsl"


def test_parse_example():
    model = parse_file(EXAMPLE)
    assert model.name == "EnzymeKinetics"
    assert [s.name for s in model.species] == ["E", "S", "ES", "P"]
    assert [r.name for r in model.reactions] == ["binding", "unbinding", "catalysis"]
    assert {p.name for p in model.params} == {"kf", "kr", "kcat"}
    assert [i.name for i in model.invariants] == ["enzyme_conservation"]


def test_species_initial():
    model = parse_file(EXAMPLE)
    init = {s.name: s.initial for s in model.species}
    assert init == {"E": 1.0, "S": 10.0, "ES": 0.0, "P": 0.0}


def test_reaction_stoichiometry():
    model = parse_file(EXAMPLE)
    binding = next(r for r in model.reactions if r.name == "binding")
    assert {ref.species for ref in binding.reactants} == {"E", "S"}
    assert [ref.species for ref in binding.products] == ["ES"]
    assert binding.rate_law == "mass_action"
    assert binding.rate_param == "kf"


def test_param_grades():
    model = parse_file(EXAMPLE)
    by_name = {p.name: p for p in model.params}
    assert by_name["kcat"].grade == "DERIVED_FROM_EXPERIMENT"
    assert by_name["kcat"].grade_meta == {"replicates": 3, "p": 0.01}
    assert by_name["kf"].grade == "LITERATURE_CONSENSUS"
    assert by_name["kf"].grade_meta == {"citations": 12}
    assert by_name["kr"].grade == "ASSUMED_FOR_MODELING"


def test_evidence_byte_ranges_roundtrip():
    """Every span must point at the exact bytes it claims to."""
    model = parse_file(EXAMPLE)
    data = model.source.data
    for s in model.species:
        sub = data[s.span.byte_start:s.span.byte_end].decode("utf-8")
        assert sub == s.span.text
        assert s.name in sub


def test_scientific_notation():
    model = parse("model M { param k in [9.0e5, 1.1e6] @assumed\n"
                  " reaction r : A -> B @mass_action(k)\n species A\n species B }")
    p = model.params[0]
    assert p.lo == 9.0e5
    assert p.hi == 1.1e6


def test_syntax_error_has_position():
    with pytest.raises(BSLError) as exc:
        parse("model M { species }")  # missing species name
    assert exc.value.line == 1
