"""BSL — the Biological Specification Language front-end for GSK-LeanBio.

A standalone, dependency-free toolchain that turns a `.bsl` biochemical model
into (a) a type-checked AST, (b) evidence-bound, confidence-graded claim
candidates, and (c) Lean 4 semantics. Shaped to dock into the AXM provenance
ecosystem via the `candidates.jsonl` seam, but requiring none of it to run.
"""

from .nodes import (
    Model,
    Species,
    Reaction,
    SpeciesRef,
    Param,
    Invariant,
    Span,
    Source,
)
from .lexer import tokenize, BSLError
from .parser import parse, parse_file
from .typecheck import check, Diagnostic

__all__ = [
    "Model",
    "Species",
    "Reaction",
    "SpeciesRef",
    "Param",
    "Invariant",
    "Span",
    "Source",
    "tokenize",
    "parse",
    "parse_file",
    "check",
    "Diagnostic",
    "BSLError",
]

__version__ = "0.1.0"
