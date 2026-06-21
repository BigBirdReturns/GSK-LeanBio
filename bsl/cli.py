"""Command-line interface for the BSL toolchain.

    python -m bsl parse   MODEL.bsl
    python -m bsl check    MODEL.bsl
    python -m bsl compile  MODEL.bsl [--out DIR] [--backend file|genesis]
    python -m bsl lean     MODEL.bsl [--out FILE]

Standalone and dependency-free. The `genesis` backend is optional and only
loaded on demand (the AXM growth surface).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .lexer import BSLError
from .parser import parse_file
from .typecheck import check, has_errors
from .candidates import to_list
from .lean import emit_lean
from .emit.port import SourceDoc
from .emit.file_sink import FileSink


def _load(path: str):
    model = parse_file(path)
    diags = check(model)
    return model, diags


def _print_diags(diags, source_name: str) -> None:
    for d in diags:
        stream = sys.stderr if d.severity == "error" else sys.stdout
        print(d.format(source_name), file=stream)


def cmd_parse(args) -> int:
    model, diags = _load(args.file)
    print(f"model {model.name}")
    print(f"  species    : {len(model.species)}  "
          f"({', '.join(s.name for s in model.species)})")
    print(f"  reactions  : {len(model.reactions)}  "
          f"({', '.join(r.name for r in model.reactions)})")
    print(f"  parameters : {len(model.params)}  "
          f"({', '.join(p.name for p in model.params)})")
    print(f"  invariants : {len(model.invariants)}  "
          f"({', '.join(i.name for i in model.invariants)})")
    _print_diags(diags, model.source.name)
    return 1 if has_errors(diags) else 0


def cmd_check(args) -> int:
    model, diags = _load(args.file)
    _print_diags(diags, model.source.name)
    n_err = sum(1 for d in diags if d.severity == "error")
    n_warn = sum(1 for d in diags if d.severity == "warning")
    if n_err == 0 and n_warn == 0:
        print(f"{model.source.name}: ok — no issues")
    else:
        print(f"{model.source.name}: {n_err} error(s), {n_warn} warning(s)")
    return 1 if n_err else 0


def cmd_compile(args) -> int:
    model, diags = _load(args.file)
    _print_diags(diags, model.source.name)
    if has_errors(diags) and not args.force:
        print("compile aborted: model has errors (use --force to override)",
              file=sys.stderr)
        return 1

    cands = to_list(model)
    out_dir = Path(args.out) if args.out else Path("out") / model.name
    source = SourceDoc(
        name=model.source.name, text=model.source.text, sha256=model.source.sha256
    )

    if args.backend == "genesis":
        from .emit.genesis_adapter import GenesisEmitter
        emitter = GenesisEmitter()
    else:
        emitter = FileSink()

    result = emitter.emit(cands, source, out_dir)

    n_entities = sum(1 for c in cands if c.get("kind") == "entity")
    n_claims = sum(1 for c in cands if c.get("kind") == "claim")
    print(f"compiled {model.name}: {n_entities} entities, {n_claims} claims")
    print(f"  -> {result.out_dir}")
    print(f"  signed: {result.signed}"
          + (f" (suite {result.suite})" if result.suite else ""))
    if not result.signed:
        print("  note: unsigned bundle; dock the genesis backend "
              "(--backend genesis) to seal a conformant shard")
    return 0


def cmd_lean(args) -> int:
    model, diags = _load(args.file)
    _print_diags(diags, model.source.name)
    if has_errors(diags) and not args.force:
        print("lean emission aborted: model has errors (use --force to override)",
              file=sys.stderr)
        return 1
    text = emit_lean(model)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="bsl", description="BSL toolchain")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("parse", help="parse and summarise a model")
    sp.add_argument("file")
    sp.set_defaults(func=cmd_parse)

    sp = sub.add_parser("check", help="typecheck physical invariants")
    sp.add_argument("file")
    sp.set_defaults(func=cmd_check)

    sp = sub.add_parser("compile", help="emit evidence-bound claim candidates")
    sp.add_argument("file")
    sp.add_argument("--out", help="output directory (default: out/<model>)")
    sp.add_argument("--backend", choices=["file", "genesis"], default="file",
                    help="emitter backend (default: file)")
    sp.add_argument("--force", action="store_true",
                    help="emit even if the model has errors")
    sp.set_defaults(func=cmd_compile)

    sp = sub.add_parser("lean", help="emit Lean 4 semantics")
    sp.add_argument("file")
    sp.add_argument("--out", help="output .lean file (default: stdout)")
    sp.add_argument("--force", action="store_true",
                    help="emit even if the model has errors")
    sp.set_defaults(func=cmd_lean)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except BSLError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except RuntimeError as e:
        # e.g. the optional genesis backend when AXM is not installed
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
