# Where is the framework?

The disciplined version of the argument this repo backs. The attack is on the
**structure of the claim**, conditional on whether the framework ships — not on
any individual's character or intent.

## The claim

Kim Branson (Chief AI Officer, GSK), on LinkedIn:

> "I've often thought we need a 'Lean for biology'. It didn't exist so we built
> it. Details to come."

Follow-up, in reply to the question of openness:

> "The data is where the competitive aspect lies, not the methods to verify and
> check for correctness over multiple scales and evidence strengths."

Good. If the method is not the moat, the method can be published — and if it
borrows the word *Lean*, it must be.

## Why the word "Lean" carries a burden

Lean's authority does not come from sounding rigorous. It comes from proof terms
that can be **inspected, replayed, and checked outside the institution that
produced them**, with zero dependency on the author. Anyone can run Lean against
their own theorem without trusting the mathematician who wrote it. Borrowing the
word imports that standard, whether or not the speaker intends it.

## The burden, itemized

A "Lean for biology" that means what "Lean" means must expose:

- a formal specification language
- a proof checker
- runnable examples
- explicit assumptions / axioms
- parameter bounds
- evidence grades
- machine-checkable proof artifacts
- **zero dependency on proprietary infrastructure**

## Lean standard vs. biology reality

| Lean standard | Biology reality |
|---|---|
| Open proof terms — anyone can inspect | Provisional axioms — incomplete, evolving mechanisms |
| Local checker — anyone can run | Parameter uncertainty — estimates, noise, variability |
| Reproducible build — anyone can reproduce | Evidence grades — data quality varies, confidence is graded |
| No private infrastructure — anyone can verify | Model-relative — proofs certify the *model*, not biological truth |

## What this repo establishes

1. **The technical concept is real.** A biochemical model can be compiled into a
   kernel-checked theorem that is open, local, and reproducible by anyone — the
   flagship CI run is the proof.
2. **The ceiling is real and unavoidable.** Formal certainty attaches to the
   model statement under stated assumptions, never to biological ground truth.
   The most a faithful "Lean for biology" can be is model-relative certification.

## The structural point

A claim of the form *"we built X,"* where X's legitimacy comes from external
verifiability, is **undischarged until the verifier is published**. Until then
the statement functions as a credibility bridge: it captures the epistemic
authority of an open-verification regime while keeping the verification surface
private. This is a property of the *claim*, independent of anyone's intent.

## The falsifiable test

Publish the framework — the formal language and proof checker, runnable against
any lab's own data with zero proprietary-infrastructure dependency, the same way
anyone runs Lean against their own theorem.

- If it ships, the claim is discharged and this repo is a footnote. Good outcome.
- If it does not, the claim was branding wearing Lean's authority.

Either way the test is external and public. That is the whole point of invoking
Lean.

**Where is the framework?**
