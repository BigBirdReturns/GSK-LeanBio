"""BSL -> Lean 4 verification obligations (core-only, `omega`-checkable).

Conservation is a *structural* fact about stoichiometry. If an invariant's
covector c lies in the left null space of the stoichiometric matrix N, then for
ANY kinetics

    d/dt (c . x) = c . (N v) = (c . N) v = 0

because each reaction flux v_r enters every species' derivative with its net
stoichiometric coefficient. We emit exactly that statement with each flux as an
opaque integer, so the goal is linear and closes by `omega` in Lean core — no
Mathlib, no real analysis, no axioms.

The check is real: if the declared invariant is *not* a conservation law of the
network, `c . N != 0` for some reaction, the goal is false, and `omega` fails.
"""

from __future__ import annotations

from .emit import _net
from ..nodes import Model, Invariant


def _is_int(x: float) -> bool:
    return x == int(x)


def _term(coeff: int, var: str) -> str:
    if coeff == 1:
        return var
    if coeff == -1:
        return f"-{var}"
    if coeff < 0:
        return f"({coeff}) * {var}"
    return f"{coeff} * {var}"


def _join_plus(parts: list[str]) -> str:
    if not parts:
        return "0"
    out = parts[0]
    for p in parts[1:]:
        out += f" + ({p})" if p.startswith("-") else f" + {p}"
    return out


def _dexpr(model: Model, species: str, relevant: list) -> str:
    terms = []
    for r in relevant:
        c = int(_net(r, species))
        if c == 0:
            continue
        terms.append(_term(c, f"v_{r.name}"))
    return _join_plus(terms)


def _human(inv: Invariant) -> str:
    return " + ".join(
        (t.species if t.coeff == 1 else f"{_int_or_float(t.coeff)}*{t.species}")
        for t in inv.terms
    )


def _int_or_float(x: float):
    return int(x) if _is_int(x) else x


def obligation(model: Model, inv: Invariant) -> dict:
    expr = _human(inv)
    coeffs_ok = all(_is_int(t.coeff) for t in inv.terms) and all(
        _is_int(_net(r, t.species)) for r in model.reactions for t in inv.terms
    )
    if not coeffs_ok:
        return {
            "name": inv.name,
            "claim": f"d/dt({expr}) = 0",
            "integer_ok": False,
            "lean": f"-- {inv.name}: skipped (non-integer coefficients; the omega "
                    f"path requires integers)",
        }

    relevant = [
        r for r in model.reactions
        if any(_net(r, t.species) != 0 for t in inv.terms)
    ]
    parts = []
    for t in inv.terms:
        c = int(t.coeff)
        inner = f"({_dexpr(model, t.species, relevant)})"
        if c == 1:
            parts.append(inner)
        elif c == -1:
            parts.append(f"-{inner}")
        else:
            parts.append(f"{c} * {inner}")
    lhs = _join_plus(parts)

    flux_vars = " ".join(f"v_{r.name}" for r in relevant)
    sig = f" ({flux_vars} : Int)" if relevant else ""
    body = (
        f"theorem {inv.name}{sig} :\n"
        f"    {lhs} = 0 := by\n"
        f"  omega"
    )
    return {
        "name": inv.name,
        "claim": f"d/dt({expr}) = 0",
        "integer_ok": True,
        "lean": body,
    }


def emit_verification(model: Model) -> tuple[str, list[dict]]:
    """Return (lean_source, obligations). One theorem per declared invariant."""
    obligations = [obligation(model, inv) for inv in model.invariants]
    L: list[str] = []
    L.append(f"/- Auto-generated conservation obligations for {model.name} "
             f"by GSK-LeanBio. -/")
    L.append("/- Flux-abstract stoichiometric conservation, checked by `omega` "
             "(Lean core, no Mathlib). -/")
    L.append(f"namespace BSL.{model.name}.Verify")
    L.append("")
    for ob in obligations:
        L.append(ob["lean"])
        L.append("")
    L.append(f"end BSL.{model.name}.Verify")
    L.append("")
    return "\n".join(L), obligations
