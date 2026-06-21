"""Optional Genesis adapter — the growth/scale surface.

This is where (and only where) GSK-LeanBio touches AXM. It maps BSL candidates
onto AXM Forge's candidate schema and calls the Genesis kernel to compile and
sign a conformant shard. Per AXM INV-26/28, the spoke never reimplements
sealing, Merkle construction, or signing: those are the kernel's job. We hand
candidates across the seam and let the kernel produce the byte-exact result.

AXM is an *optional* dependency. If it isn't installed this adapter raises a
clear error pointing at the extra — the standalone FileSink remains the default
path and needs none of this.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .port import Emitter, SourceDoc, EmitResult

_INSTALL_HINT = (
    "AXM Genesis/Core are not importable. The Genesis backend is optional; "
    "install it to seal shards:  pip install 'gsk-leanbio[axm]'  (or add the "
    "axm-genesis / axm-core packages to your environment). The standalone "
    "FileSink backend requires none of this."
)


class GenesisEmitter:
    """Docks the AXM kernel. Stub until AXM is present in the environment."""

    def emit(
        self,
        candidates: list[dict[str, Any]],
        source: SourceDoc,
        out_dir: str | Path,
    ) -> EmitResult:
        try:
            # Stable surfaces per axm-core SPOKE_API.md.
            from axm_forge.emission.genesis_emission import emit_shard  # type: ignore
        except ImportError as exc:  # pragma: no cover - depends on env
            raise RuntimeError(_INSTALL_HINT) from exc

        # --- seam translation: BSL candidates -> Forge candidates -----------
        # Bio-specific fields (grade_meta, Lean terms, interval bounds) become
        # an `ext/bsl@1` extension rather than touching frozen core tables
        # (AXM INV-29). Mapping the exact column shapes is the remaining work
        # for this adapter; the call below is the intended shape.
        forge_candidates = _to_forge_candidates(candidates)

        result = emit_shard(  # pragma: no cover - requires AXM installed
            candidates=forge_candidates,
            source_text=source.text,
            source_name=source.name,
            out_dir=str(out_dir),
        )
        return EmitResult(
            out_dir=Path(out_dir),
            signed=True,
            suite=getattr(result, "suite", "axm-blake3-mldsa44"),
            note="Sealed AXM Genesis shard.",
        )


def _to_forge_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Translate BSL candidate records to Forge's candidate schema.

    Kept as an explicit, reviewable function so the seam is one place. Filled in
    against the Forge candidate schema when wiring AXM for real.
    """
    return candidates


_: Emitter = GenesisEmitter()
