from pathlib import Path

import pytest

from bsl.parser import parse, parse_file
from bsl.lean.verify_emit import emit_verification
from bsl.verify import run_verification, find_lean

EX = Path(__file__).resolve().parents[1] / "examples"
LEAN_MISSING = find_lean() is None
needs_lean = pytest.mark.skipif(LEAN_MISSING, reason="no Lean toolchain available")


def test_emit_obligation_needs_no_lean():
    m = parse_file(EX / "A-enzyme-kinetics" / "model.bsl")
    src, obs = emit_verification(m)
    assert "namespace BSL.EnzymeKinetics.Verify" in src
    assert "theorem enzyme_conservation" in src
    assert "omega" in src
    assert len(obs) == 1 and obs[0]["integer_ok"]


def test_unchecked_when_lean_forced_absent(tmp_path):
    m = parse_file(EX / "A-enzyme-kinetics" / "model.bsl")
    journal, lean_file = run_verification(m, tmp_path, lean_path="/nonexistent/lean")
    # falls through to PATH lookup; only assert the file is always written
    assert lean_file.exists()
    assert journal["result"] in {"verified", "unchecked"}


@needs_lean
@pytest.mark.parametrize("example,inv", [
    ("A-enzyme-kinetics", "enzyme_conservation"),
    ("B-michaelis-menten", "mass_conservation"),
    ("C-hill", "receptor_conservation"),
])
def test_verify_discharges_conservation(example, inv, tmp_path):
    m = parse_file(EX / example / "model.bsl")
    journal, _ = run_verification(m, tmp_path)
    assert journal["result"] == "verified", journal
    statuses = {o["name"]: o["status"] for o in journal["obligations"]}
    assert statuses[inv] == "discharged"


@needs_lean
def test_verify_refutes_false_invariant(tmp_path):
    src = """model Bogus {
      species A @init 1.0
      species B @init 0.0
      reaction r : A -> B @mass_action(k)
      param k in [0.0, 1.0] @assumed
      invariant fake : A = 1.0
    }"""
    journal, _ = run_verification(parse(src), tmp_path)
    assert journal["result"] == "failed"
    assert journal["obligations"][0]["status"] == "failed"
