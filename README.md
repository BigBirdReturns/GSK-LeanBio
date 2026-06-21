# GSK-LeanBio — BSL

**A formal-methods front-end for biochemical models.** Write a model in BSL
(the Biological Specification Language), get back three things:

1. a **type-checked** model (physical invariants enforced at compile time),
2. a set of **evidence-bound claims** — every fact traced to exact bytes in your
   `.bsl` source, confidence-graded by how you justified it, and
3. **Lean 4** definitions of the model's semantics (ODE vector field +
   conservation theorems), ready to prove.

It runs locally with **zero dependencies** — just Python 3.10+. Nothing leaves
your machine, nothing is fetched, no account.

## What this is — and isn't

This proves **model consistency under explicitly stated, confidence-graded
assumptions**. It does **not** claim biological ground truth. A green check means
"given these axioms and parameter bounds, the conclusion follows" — not "nature
agrees." See [`docs/limitations.md`](docs/limitations.md).

## Quick start

```bash
git clone https://github.com/BigBirdReturns/gsk-leanbio
cd gsk-leanbio

python -m bsl check   examples/A-enzyme-kinetics/model.bsl
python -m bsl compile examples/A-enzyme-kinetics/model.bsl --out out/enzyme
python -m bsl lean    examples/A-enzyme-kinetics/model.bsl
```

`compile` writes a standalone evidence bundle (`candidates.jsonl` + source +
manifest). `lean` emits the model's semantics as Lean 4.

## The AXM mating surface

GSK-LeanBio stands on its own, but it is shaped to dock into the
[AXM](https://github.com/BigBirdReturns) provenance ecosystem without being
welded to it. The seam is exactly two interfaces:

- **in:** `candidates.jsonl` — entities/claims/evidence + tier + confidence, the
  format AXM's Forge already ingests.
- **out:** a sealed, signed Genesis shard.

The bio code carries **zero AXM-format logic**. It hands candidates to an
[`Emitter`](bsl/emit/port.py) (a one-method port). The default
[`FileSink`](bsl/emit/file_sink.py) writes a plain unsigned bundle — no
dependency. The optional [`GenesisEmitter`](bsl/emit/genesis_adapter.py) docks
the AXM kernel to produce a cryptographically sealed shard; that is the
*growth/scale surface*, not a build-time requirement. The tool doesn't *become*
AXM — it exposes a socket AXM clicks into.

## Status

| Capability | State |
|---|---|
| BSL parser (mass-action reactions, params, invariants) | working |
| Typechecker (non-negative conc/rates, mass-balance refs, intervals) | working |
| Candidate emission (evidence-bound, confidence-graded) | working |
| Standalone `FileSink` bundle | working |
| Lean 4 semantics emission (ODE field + conservation theorem) | working (emit only) |
| Genesis adapter (signed shards) | optional, stub — docks when AXM is installed |
| Running Lean to *discharge* proofs | next |
| Michaelis–Menten / Hill sugar, PK/PD, CTMC | not yet |

## License

Apache-2.0
