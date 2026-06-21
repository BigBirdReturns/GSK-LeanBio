"""Run Lean over a model's conservation obligations and record a journal.

This is the "validation is itself a theorem" layer: each declared invariant
becomes a proof obligation, Lean's kernel discharges it (or refutes it), and the
outcome is written to a journal record — the standalone analogue of an AXM
journal shard (a decision trace: what was checked, what passed, what failed).

Lean is located via, in order: an explicit path, `$BSL_LEAN`, `lean` on PATH,
then `~/.elan/bin/lean`. If none is found, the obligation file is still emitted
and the journal is marked `unchecked` — emission never requires a toolchain.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from .nodes import Model
from .lean.verify_emit import emit_verification


def find_lean(explicit: str | None = None) -> str | None:
    for cand in (explicit, os.environ.get("BSL_LEAN")):
        if cand and Path(cand).exists():
            return cand
    found = shutil.which("lean")
    if found:
        return found
    elan = Path.home() / ".elan" / "bin" / "lean"
    return str(elan) if elan.exists() else None


def _lean_version(lean: str) -> str | None:
    try:
        out = subprocess.run([lean, "--version"], capture_output=True, text=True,
                             timeout=30)
        return out.stdout.strip() or None
    except Exception:
        return None


def _public(ob: dict, status: str) -> dict:
    return {
        "name": ob["name"],
        "claim": ob["claim"],
        "integer_ok": ob["integer_ok"],
        "status": status,
    }


def run_verification(
    model: Model,
    out_dir: str | Path,
    lean_path: str | None = None,
    timeout: int = 120,
) -> tuple[dict, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    source, obligations = emit_verification(model)
    lean_file = out / f"{model.name}.lean"
    lean_file.write_text(source, encoding="utf-8")

    journal: dict = {
        "kind": "validation_journal",
        "model": model.name,
        "source_hash": model.source.sha256,
        "checker": "lean omega (core)",
        "lean_file": str(lean_file),
        "obligations": [],
    }

    lean = find_lean(lean_path)
    runnable = [o for o in obligations if o["integer_ok"]]

    if lean is None:
        journal["obligations"] = [_public(o, "unchecked") for o in obligations]
        journal["result"] = "unchecked"
        journal["note"] = (
            "Lean not found. Set --lean / $BSL_LEAN or install a Lean 4 "
            "toolchain. The obligation file was written regardless."
        )
    else:
        proc = subprocess.run([lean, str(lean_file)], capture_output=True,
                              text=True, timeout=timeout)
        ok = proc.returncode == 0
        for o in obligations:
            if not o["integer_ok"]:
                status = "skipped"
            else:
                status = "discharged" if ok else "failed"
            journal["obligations"].append(_public(o, status))
        journal["lean_version"] = _lean_version(lean)
        if not obligations:
            journal["result"] = "no_obligations"
        elif ok:
            journal["result"] = "verified" if runnable else "skipped"
        else:
            journal["result"] = "failed"
            journal["lean_output"] = (proc.stdout + proc.stderr).strip()

    (out / f"{model.name}.journal.json").write_text(
        json.dumps(journal, indent=2, sort_keys=True), encoding="utf-8"
    )
    return journal, lean_file
