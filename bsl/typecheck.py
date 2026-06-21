"""Physical-invariant typechecking for BSL models.

These are compile-time checks that a model is physically well-formed before any
claim is emitted or any Lean is generated. They are intentionally conservative:
they catch structural and sign errors, not modelling-judgement errors.
"""

from __future__ import annotations

from dataclasses import dataclass

from .nodes import Model, Span


@dataclass
class Diagnostic:
    severity: str   # "error" | "warning"
    code: str
    message: str
    span: Span

    def format(self, source_name: str = "") -> str:
        loc = f"{source_name}:{self.span.line}:{self.span.col}" if source_name else (
            f"line {self.span.line}, col {self.span.col}"
        )
        return f"{self.severity.upper()} [{self.code}] {loc}: {self.message}"


def check(model: Model) -> list[Diagnostic]:
    diags: list[Diagnostic] = []
    species = model.species_names()
    params = model.param_names()

    # --- duplicate declarations ---------------------------------------------
    _check_dupes(model.species, "species", "E_DUP_SPECIES", diags)
    _check_dupes(model.reactions, "reaction", "E_DUP_REACTION", diags)
    _check_dupes(model.params, "parameter", "E_DUP_PARAM", diags)
    _check_dupes(model.invariants, "invariant", "E_DUP_INVARIANT", diags)

    # --- non-negative initial concentrations --------------------------------
    for s in model.species:
        if s.initial < 0:
            diags.append(Diagnostic(
                "error", "E_NEGATIVE_INITIAL",
                f"species {s.name!r} has negative initial concentration "
                f"{s.initial}", s.span,
            ))

    # --- reactions: referenced species + params must exist, coeffs > 0 ------
    for r in model.reactions:
        for ref in r.reactants + r.products:
            if ref.species not in species:
                diags.append(Diagnostic(
                    "error", "E_UNDECLARED_SPECIES",
                    f"reaction {r.name!r} references undeclared species "
                    f"{ref.species!r}", ref.span,
                ))
            if ref.coeff <= 0:
                diags.append(Diagnostic(
                    "error", "E_BAD_STOICH",
                    f"reaction {r.name!r} has non-positive stoichiometric "
                    f"coefficient {ref.coeff} on {ref.species!r}", ref.span,
                ))
        if r.rate_param not in params:
            diags.append(Diagnostic(
                "error", "E_UNDECLARED_PARAM",
                f"reaction {r.name!r} uses undeclared rate parameter "
                f"{r.rate_param!r}", r.span,
            ))

    # --- parameter intervals: lo <= hi, rate constants non-negative ---------
    for p in model.params:
        if p.lo > p.hi:
            diags.append(Diagnostic(
                "error", "E_BAD_INTERVAL",
                f"parameter {p.name!r} has empty interval [{p.lo}, {p.hi}] "
                f"(lower bound exceeds upper)", p.span,
            ))
        if p.lo < 0:
            diags.append(Diagnostic(
                "error", "E_NEGATIVE_RATE",
                f"parameter {p.name!r} admits negative values; mass-action rate "
                f"constants must be non-negative", p.span,
            ))

    # --- invariants reference declared species only -------------------------
    for inv in model.invariants:
        for ref in inv.terms:
            if ref.species not in species:
                diags.append(Diagnostic(
                    "error", "E_UNDECLARED_SPECIES",
                    f"invariant {inv.name!r} references undeclared species "
                    f"{ref.species!r}", ref.span,
                ))

    # --- unused parameters (warning) ----------------------------------------
    used = {r.rate_param for r in model.reactions}
    for p in model.params:
        if p.name not in used:
            diags.append(Diagnostic(
                "warning", "W_UNUSED_PARAM",
                f"parameter {p.name!r} is declared but never used by a reaction",
                p.span,
            ))

    return diags


def has_errors(diags: list[Diagnostic]) -> bool:
    return any(d.severity == "error" for d in diags)


def _check_dupes(items, kind: str, code: str, diags: list[Diagnostic]) -> None:
    seen: dict[str, object] = {}
    for it in items:
        if it.name in seen:
            diags.append(Diagnostic(
                "error", code,
                f"duplicate {kind} {it.name!r}", it.span,
            ))
        else:
            seen[it.name] = it
