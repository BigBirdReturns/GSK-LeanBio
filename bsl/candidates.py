"""Model -> claim candidates (the AXM-shaped seam).

Each candidate is one JSON object on one line of `candidates.jsonl`. The shape
mirrors what AXM's Forge ingests: typed entities and SPO claims, every record
bound to a byte range of evidence in the canonical source, tier- and
confidence-graded. The exact reconciliation to Forge's internal candidate
schema (and the `ext/bsl@1` extension carrying Lean terms / interval bounds)
happens in the Genesis adapter — it is deliberately *not* baked in here, so the
bio front-end stays free of AXM-format logic.

Tier semantics follow AXM's INV-13:
  tier 0 = lossless lift from the model (confidence 1.0)
  tier 2 = evidence-graded (literature / experiment)
  tier 3 = weaker / assumed
"""

from __future__ import annotations

from typing import Any, Iterator

from .nodes import (
    Model,
    Span,
    GRADE_EXPERIMENT,
    GRADE_LITERATURE,
    GRADE_ASSUMED,
)

# Placeholder confidence heuristics keyed by grade. Real derivation (turning
# replicate counts / p-values / citation counts into calibrated confidence) is
# the parameter-oracle layer; these are honest stand-ins until then.
_GRADE_TIER = {
    GRADE_EXPERIMENT: 2,
    GRADE_LITERATURE: 2,
    GRADE_ASSUMED: 3,
}
_GRADE_CONF = {
    GRADE_EXPERIMENT: 0.95,
    GRADE_LITERATURE: 0.80,
    GRADE_ASSUMED: 0.50,
}

NAMESPACE = "bsl"


def _evidence(model: Model, span: Span) -> dict[str, Any]:
    return {
        "source_hash": model.source.sha256,
        "byte_start": span.byte_start,
        "byte_end": span.byte_end,
        "text": span.text,
    }


def _locator(model: Model, span: Span) -> dict[str, Any]:
    return {"file": model.source.name, "line": span.line, "col": span.col}


def _entity(model: Model, label: str, etype: str, span: Span) -> dict[str, Any]:
    return {
        "kind": "entity",
        "namespace": NAMESPACE,
        "label": label,
        "etype": etype,
        "evidence": _evidence(model, span),
        "locator": _locator(model, span),
    }


def _claim(
    model: Model,
    subject: str,
    predicate: str,
    obj: str,
    object_type: str,
    span: Span,
    tier: int,
    confidence: float,
    **extra: Any,
) -> dict[str, Any]:
    rec = {
        "kind": "claim",
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "object_type": object_type,
        "tier": tier,
        "confidence": confidence,
        "evidence": _evidence(model, span),
        "locator": _locator(model, span),
    }
    rec.update(extra)
    return rec


def candidates(model: Model) -> Iterator[dict[str, Any]]:
    """Yield entity and claim candidates for the model, in source order."""

    # Species -> entity + initial-concentration claim.
    for s in model.species:
        label = f"species:{s.name}"
        yield _entity(model, label, "species", s.span)
        yield _claim(
            model, label, "has_initial_concentration", repr(s.initial),
            "literal:decimal", s.span, tier=0, confidence=1.0,
        )

    # Parameters -> entity + interval claim (confidence-graded).
    for p in model.params:
        label = f"param:{p.name}"
        yield _entity(model, label, "parameter", p.span)
        yield _claim(
            model, label, "in_interval", f"[{p.lo}, {p.hi}]",
            "literal:string", p.span,
            tier=_GRADE_TIER[p.grade], confidence=_GRADE_CONF[p.grade],
            grade=p.grade, grade_meta=p.grade_meta,
        )

    # Reactions -> entity + stoichiometry + rate-law claims (all tier 0).
    for r in model.reactions:
        label = f"reaction:{r.name}"
        yield _entity(model, label, "reaction", r.span)
        for ref in r.reactants:
            yield _claim(
                model, label, "consumes", f"species:{ref.species}",
                "entity", ref.span, tier=0, confidence=1.0,
                stoichiometry=ref.coeff,
            )
        for ref in r.products:
            yield _claim(
                model, label, "produces", f"species:{ref.species}",
                "entity", ref.span, tier=0, confidence=1.0,
                stoichiometry=ref.coeff,
            )
        yield _claim(
            model, label, "has_rate_law", r.rate_law,
            "literal:string", r.span, tier=0, confidence=1.0,
        )
        yield _claim(
            model, label, "has_rate_parameter", f"param:{r.rate_param}",
            "entity", r.span, tier=0, confidence=1.0,
        )

    # Invariants -> entity + conservation claim + per-species links.
    for inv in model.invariants:
        label = f"invariant:{inv.name}"
        yield _entity(model, label, "invariant", inv.span)
        expr = " + ".join(
            (f"{ref.coeff} {ref.species}" if ref.coeff != 1.0 else ref.species)
            for ref in inv.terms
        )
        yield _claim(
            model, label, "asserts_conservation", f"{expr} = {inv.rhs}",
            "literal:string", inv.span, tier=0, confidence=1.0,
            grade=GRADE_ASSUMED,
        )
        for ref in inv.terms:
            yield _claim(
                model, label, "constrains", f"species:{ref.species}",
                "entity", ref.span, tier=0, confidence=1.0,
            )


def to_list(model: Model) -> list[dict[str, Any]]:
    return list(candidates(model))
