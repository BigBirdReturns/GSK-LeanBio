"""Standalone, dependency-free emitter.

Writes an evidence bundle that a human (or the AXM Forge importer) can read:

    out_dir/
      content/source.bsl     # the canonical source, byte-for-byte
      candidates.jsonl       # the seam payload
      manifest.json          # counts + source hash + provenance note

This bundle is deliberately *unsigned*. It is not a conformant Genesis shard
and does not pretend to be — sealing is the Genesis adapter's job. The note in
the manifest says so explicitly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .port import Emitter, SourceDoc, EmitResult

_UNSIGNED_NOTE = (
    "Unsigned standalone bundle produced by GSK-LeanBio FileSink. This is NOT a "
    "conformant AXM Genesis shard: no Merkle root, no signature. To produce a "
    "sealed, verifiable shard, emit through the Genesis adapter "
    "(bsl.emit.genesis_adapter.GenesisEmitter)."
)


class FileSink:
    """Default emitter. Pure stdlib."""

    def emit(
        self,
        candidates: list[dict[str, Any]],
        source: SourceDoc,
        out_dir: str | Path,
    ) -> EmitResult:
        out = Path(out_dir)
        (out / "content").mkdir(parents=True, exist_ok=True)

        (out / "content" / "source.bsl").write_text(source.text, encoding="utf-8")

        with (out / "candidates.jsonl").open("w", encoding="utf-8") as f:
            for rec in candidates:
                f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False))
                f.write("\n")

        n_entities = sum(1 for c in candidates if c.get("kind") == "entity")
        n_claims = sum(1 for c in candidates if c.get("kind") == "claim")
        manifest = {
            "format": "gsk-leanbio/bundle@1",
            "source_name": source.name,
            "source_hash": source.sha256,
            "suite": None,
            "signed": False,
            "candidate_counts": {"entities": n_entities, "claims": n_claims},
            "note": _UNSIGNED_NOTE,
        }
        (out / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
        )

        return EmitResult(
            out_dir=out, signed=False, suite=None, note=_UNSIGNED_NOTE
        )


# Confirm the adapter satisfies the port at import time.
_: Emitter = FileSink()
