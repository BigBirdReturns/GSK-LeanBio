"""The emitter port — the AXM-shaped mating surface.

Everything upstream (parse -> typecheck -> candidates) is pure biology and
knows nothing about how candidates get sealed. An `Emitter` takes candidates
plus the canonical source and produces an artifact. The standalone `FileSink`
writes a plain bundle; the `GenesisEmitter` docks the AXM kernel to produce a
signed shard. New backends are new `Emitter`s — the bio code never changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@dataclass
class SourceDoc:
    """The canonical source handed across the seam alongside candidates."""

    name: str
    text: str
    sha256: str


@dataclass
class EmitResult:
    out_dir: Path
    signed: bool
    suite: str | None
    note: str


@runtime_checkable
class Emitter(Protocol):
    def emit(
        self,
        candidates: list[dict[str, Any]],
        source: SourceDoc,
        out_dir: str | Path,
    ) -> EmitResult:
        ...
