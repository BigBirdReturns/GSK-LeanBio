"""AST node definitions and source-position bookkeeping.

Every construct carries a `Span` — a byte range into the canonical `.bsl`
source — so that downstream claims can be bound to exact source bytes (the
same content-addressed evidence model AXM uses).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Span:
    """A byte range in the source document, plus 1-based line/column."""

    byte_start: int
    byte_end: int
    line: int
    col: int
    text: str


@dataclass
class Source:
    """The canonical source document. Byte offsets are authoritative."""

    name: str
    text: str
    data: bytes
    sha256: str
    # char-index -> byte-offset map (len == len(text) + 1)
    _byte_at: list[int] = field(repr=False, default_factory=list)

    @classmethod
    def from_text(cls, name: str, text: str) -> "Source":
        data = text.encode("utf-8")
        byte_at = [0] * (len(text) + 1)
        b = 0
        for i, ch in enumerate(text):
            byte_at[i] = b
            b += len(ch.encode("utf-8"))
        byte_at[len(text)] = b
        return cls(
            name=name,
            text=text,
            data=data,
            sha256=hashlib.sha256(data).hexdigest(),
            _byte_at=byte_at,
        )

    def span(self, char_start: int, char_end: int, line: int, col: int) -> Span:
        return Span(
            byte_start=self._byte_at[char_start],
            byte_end=self._byte_at[char_end],
            line=line,
            col=col,
            text=self.text[char_start:char_end],
        )


@dataclass
class Species:
    name: str
    initial: float
    span: Span


@dataclass
class SpeciesRef:
    """A stoichiometric term `coeff * species` inside a reaction or invariant."""

    coeff: float
    species: str
    span: Span


@dataclass
class Reaction:
    name: str
    reactants: list[SpeciesRef]
    products: list[SpeciesRef]
    rate_law: str          # currently always "mass_action"
    rate_param: str        # name of the rate constant, e.g. "kf"
    span: Span


# Confidence grades, mirroring the report's grading system.
GRADE_EXPERIMENT = "DERIVED_FROM_EXPERIMENT"
GRADE_LITERATURE = "LITERATURE_CONSENSUS"
GRADE_ASSUMED = "ASSUMED_FOR_MODELING"


@dataclass
class Param:
    name: str
    lo: float
    hi: float
    grade: str
    grade_meta: dict
    span: Span


@dataclass
class Invariant:
    name: str
    terms: list[SpeciesRef]
    rhs: float
    span: Span


@dataclass
class Model:
    name: str
    species: list[Species]
    reactions: list[Reaction]
    params: list[Param]
    invariants: list[Invariant]
    span: Span
    source: Source

    def species_names(self) -> set[str]:
        return {s.name for s in self.species}

    def param_names(self) -> set[str]:
        return {p.name for p in self.params}
