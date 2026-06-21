import json
from pathlib import Path

from bsl.parser import parse_file
from bsl.candidates import to_list
from bsl.lean import emit_lean
from bsl.emit.file_sink import FileSink
from bsl.emit.port import SourceDoc

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "A-enzyme-kinetics" / "model.bsl"


def test_candidates_shape():
    model = parse_file(EXAMPLE)
    cands = to_list(model)
    kinds = {c["kind"] for c in cands}
    assert kinds == {"entity", "claim"}

    # object_type must be in the AXM-allowed enum.
    allowed = {"entity", "literal:string", "literal:integer",
               "literal:decimal", "literal:boolean"}
    for c in cands:
        if c["kind"] == "claim":
            assert c["object_type"] in allowed
            assert 0 <= c["tier"] <= 4
            assert 0.0 <= c["confidence"] <= 1.0
            assert "evidence" in c and "source_hash" in c["evidence"]


def test_confidence_grading_flows_through():
    model = parse_file(EXAMPLE)
    cands = to_list(model)
    kcat = next(
        c for c in cands
        if c["kind"] == "claim" and c["subject"] == "param:kcat"
        and c["predicate"] == "in_interval"
    )
    assert kcat["grade"] == "DERIVED_FROM_EXPERIMENT"
    assert kcat["tier"] == 2
    assert kcat["confidence"] == 0.95


def test_evidence_points_at_source_bytes():
    model = parse_file(EXAMPLE)
    data = model.source.data
    for c in to_list(model):
        ev = c["evidence"]
        assert data[ev["byte_start"]:ev["byte_end"]].decode("utf-8") == ev["text"]


def test_file_sink_roundtrip(tmp_path):
    model = parse_file(EXAMPLE)
    cands = to_list(model)
    source = SourceDoc(model.source.name, model.source.text, model.source.sha256)
    result = FileSink().emit(cands, source, tmp_path)

    assert result.signed is False
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["signed"] is False
    assert manifest["source_hash"] == model.source.sha256

    lines = (tmp_path / "candidates.jsonl").read_text().strip().splitlines()
    assert len(lines) == len(cands)
    for line in lines:
        json.loads(line)  # each line is valid JSON

    # the bundled source is byte-identical to the input
    assert (tmp_path / "content" / "source.bsl").read_bytes() == model.source.data


def test_lean_emission_has_conservation_theorem():
    model = parse_file(EXAMPLE)
    lean = emit_lean(model)
    assert "namespace BSL.EnzymeKinetics" in lean
    assert "def dXdt" in lean
    assert "theorem enzyme_conservation" in lean
    assert "ring" in lean
