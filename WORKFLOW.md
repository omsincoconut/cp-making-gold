# Problem-Generation Workflow — version 2.2

All paths in this document are relative to this folder (`workflow_v2/`), which is the working root of every run.
The markers **[v2]** and **[v2.1]** label steps that were added after design experiments showed they were needed.

## 0. Overview

One run is one **trial**, and one trial is one external keyword draw. A trial ends as `accepted`, `revised`,
`rejected` or `abandoned`, and every outcome is logged. Expect most trials to end in rejection, because that is the
screen working. **Measured yield in the design experiments:** 0 of 13 trials passed the final gate (H). The best
candidate was complete and verified but fell one originality level short. Plan for many trials per accepted problem.

```
A Prepare (no data banks)
B Draw keywords (script)  -- policy enforced by the script
C Explore: attractors -> readings -> >=5 divergent questions -> quick labels
           -> probe by brute force WITH PREDICTIONS -> insight + provenance audit            [v2]
D Screen: rubric gate D -> cold-solve by a fresh solver [v2] -> advance / lemma-break [v2] / mutate / drop
E Formalize: statement.md + solution.md (bolt-on and leak checks [v2])
F Independent review (fresh context; statement first, then solution)
G Editorial + model.cpp + brute force + stress test
H Final gate (may still reject) -> close the trial in the log
```

**Inputs and tools:** Python 3 (randomizer, brute force); a C++17 compiler (on this Windows machine, run `g++`
from **PowerShell**, because the bash environment cannot link); web search; optionally subagents for the
fresh-context cold-solve (D2) and review (F, H). Without subagents, see the fallbacks in D2 and F.

**Files per trial:** `experiments/<TRIAL>/process.md` (everything procedural), `statement.md`, `solution.md`,
`coldsolve_*.md`, `review.md`, plus probe scripts. Accepted problems go to `problems/<slug>/`.

---

## A. Preparation

Read the following, in this order, and nothing else:
1. `references/design_principles.md`: what a good problem is, and how keywords are used.
2. `syllabus.md`: the knowledge ceiling. Pay attention to "What is forbidden".
3. `references/solver_moves.md`: read only when *solving* candidates (C3-C4), never to seed ideas.

Earlier technique-first data banks (technique entries with "how to reskin" templates) are
deliberately not included. They encouraged reskinned technique combinations, and giving them to the generator
showed no benefit in the design experiments.

Create `experiments/<TRIAL>/process.md`. Trial ids are fresh and never reused.

## B. External keyword draw

```
python randomizer/draw.py draw --trial <TRIAL>        # world mode, vocabulary v2 (default)
```
Paste the JSON output (seed and keywords) into `process.md`. Do not edit, replace, or re-draw it.

A draw has 4 keywords: **OBJECT** (protected), **DYNAMICS** (discardable), **QUESTION** (protected), and **TWIST**
(discardable). The parameters are justified in `randomizer/README.md`.

| Rule | Policy |
|---|---|
| Reinterpretation | Allowed for every keyword. Log it with `draw.py reinterpret`. The keyword's core meaning must survive *in the formal problem*; using it only in the story does not count. |
| Discard | At most **1** keyword, and only DYNAMICS or TWIST. It is allowed only after C2 shows at least 2 serious readings that use the keyword. Log it with `draw.py discard --reason`. The script enforces this. |
| Incompatible pairs | The script resolves these and logs them as `internal_resamples`. |
| Mutation draw | At most **2** per trial, using `draw.py mutate --reason "<candidate id>: ..."`. **[v2]** A mutation is bound to the candidate named in the reason. If that candidate is dropped, the mutation is spent. A candidate that triggered a mutation because it was KNOWN or close to an attractor may **not** later advance unmutated. |
| New draw | Only through a **new trial**. The old trial must first be closed (`rejected`/`abandoned`) with a reason, and closing requires a complete Stage C-D record. |

## C. Idea exploration

**C0. Attractor declaration.** Before inventing anything, list at least 3 well-known problems or techniques that
the draw immediately brings to mind. These are the default modes. No final candidate may share their key insight.

**C1. Readings.** For each keyword, write one literal reading and at least one non-literal reading.

**C2. Divergent questions (no solutions yet).** Write at least 5 candidate *formal questions*, 1-3 sentences each,
precise enough to brute-force. Every candidate must use OBJECT and QUESTION, plus at least one of DYNAMICS or TWIST.
At least 2 candidates must use a non-literal reading. Candidates must differ in what is asked, not only in their
parameters. Do not name algorithms in this step.

**C3. Quick solve pass.** Spend at most 10 lines on each candidate. Give the naive solution, a first-guess
efficient idea, and **the known lemma or problem it would most likely rely on [v2]**. Label each candidate:
`KNOWN`, `ROUTINE`, `INTRACTABLE`, or `PROMISING`.

**C4. Probe by experiment, with predictions [v2].** For the 1-3 most promising candidates:
1. *Before* running anything, write a **prediction**: the formula, characterization, or pattern you expect.
2. Brute-force tiny instances, tabulate the results, and look for structure.
3. Record whether the data **surprised** you. If your prediction was right, the governing fact is probably one you
   already knew, and so it is probably known to others. Treat that as a flag, not as a success.
4. Turn the observed structure into conjectures, and prove or refute them with `references/solver_moves.md`.

Keep the scripts in `experiments/<TRIAL>/`.

**C5. Insight statement and provenance audit [v2].** For each surviving candidate:
- (1) State the key insight in one sentence. (2) Explain why it is not obvious. (3) Describe the naive approach
  and why it fails. (4) Describe what remains after the insight: algorithm, knowledge needed, and approximate code
  size. (5) Apply the decomposition test.
- **Provenance table:** list every step of the solution and tag it `DERIVED` (found here from data or proof) or
  `RECOGNIZED` (you knew it before). For each RECOGNIZED step, name its source (problem, theorem, or classic
  lemma) and search it on the web.
- **Rule:** if the **key** step is RECOGNIZED, the candidate cannot advance as it stands. Go to D3 (lemma-break),
  mutate it, or drop it. RECOGNIZED *finishing* steps (for example "then LIS", or "then a greedy with a heap") are
  acceptable only if the reduction to them is DERIVED and non-obvious, and only if they stay within the syllabus.
- **[v2.1] Trick-type search.** Name the *type* of the key step at an intermediate level of detail. Examples: "an exact
  power-of-two potential that changes by one per move", "a reflection that swaps adjacent gaps", "a pairing strategy on
  a bipartite state graph", "fold two sequences into one and take the LIS". Do not stop at a level as broad as
  "invariant". Run at least 2 web searches for that type. If a known problem, especially a recent one, uses the same
  trick type *as its key step*, treat the key step as RECOGNIZED. In the design experiments, every originality
  failure at the late review gates was a match of this kind, not a duplicated problem.

## D. Concept screening (gate D of `RUBRIC.md`)

**D1. Provisional scoring and search.** Score O, I, K, B and N, with one line of justification for each. Run at
least 2 web searches per candidate (the formal one-liner and the insight phrase).

**D2. Cold-solve [v2].** For each candidate that passes D1 (at most 2), write a draft statement
(`experiments/<TRIAL>/draft_<id>.md`) that contains only the task, with no solution and no hints. Give it to a
**fresh-context solver** using template CS below, with a budget of roughly 20-30 minutes. The solver reports
what it tried, what it recognized, and how far it got.
- If the solver reaches the intended key step **by naming** a known problem, lemma or technique, treat the
  key step as RECOGNIZED and go to D3, mutate, or drop.
- If the solver finds a **different, easier** solution, the candidate is broken. Revise or drop it.
- If the solver gets partway by genuine reasoning, or gets stuck, that is the desired outcome. Advance.
- **[v2.1]** Not naming the key step is necessary but **not sufficient**. The solver must also report its time to
  the key step, and whether it guessed the key fact from tiny brute-force data. If it solved the whole problem in
  about 15-20 minutes or less, or guessed the key fact, re-score I strictly at D4. In the design experiments, every
  such case was later reviewed at I = 2. Advance only if the generator can name a second non-obvious step that the
  solver also had to derive.
- *Fallback when no subagent is available:* do a recall audit. Write the 3 problems a strong contestant would
  most likely recall, and search each of them plus the insight phrase. Record that this check is weaker.

**D3. Lemma-break revision [v2].** If the key step is a recognized lemma L, change the rules **minimally** so that L
becomes false while the kept keywords stay in force, then go back to C4 for that candidate. Log the change with
`draw.py note`. Allow at most 2 lemma-break cycles per candidate. Do not lemma-break merely by adding constraints
that force a different technique; the result must still pass N ≥ 2.

**D4. Decide** for each candidate: **advance** (at most 1 to Stage E), **mutate**, or **drop**. If nothing
advances, close the trial `rejected` with the reasons (`draw.py close`).

## E. Formalization

Write two files:
- `statement.md`: an optional legend; the precise task; input and output format; constraints; at least 2
  examples computed by the brute force, each with a short explanation; and subtasks only if a natural ladder
  exists.
- `solution.md`: the key insight, algorithm, proof (complete, or with gaps clearly marked), complexity, and the
  naive approaches that must fail, with the constraint that rules out each one.

Checks:
- (a) Spend 10 minutes trying to find an *easier* solution that still passes the constraints.
- (b) Check for ambiguity: ties, empty cases, indexing, and the output when the task is impossible.
- (c) Check every tool used against the syllabus.
- (d) **Bolt-on check [v2]:** if a component exists only to satisfy an output format (all prefixes, all k, many
  queries, updates) and is a standard technique, remove it. Use a multi-test format or a single answer instead,
  unless the format is part of the insight.
- (e) **Leak check [v2]:** examples and their explanations must not demonstrate the key lemma. For example, do not
  make every sample answer have the special structure that the lemma asserts.

## F. Independent review

Use a fresh-context reviewer (template R). It first reads **only `statement.md`** and records a solving attempt
(F1). It then reads `solution.md` and reviews it against `RUBRIC.md` (F2), including the known-pattern checks
and the web searches. If no subagent is available, write your own statement-only attempt *before* re-reading
`solution.md`, and state this limitation. Agreement from the same model is weak evidence.

The outcome follows gate F: **advance**, **revise** (back to E), or **reject** (close the trial).

## G. Editorial and model implementation

In `problems/<slug>/` create: `statement.md`, `editorial.md`, `model.cpp` (C++17), `brute.py` or `brute.cpp`,
`stress.py`, and `review.md`.

The editorial has these sections, in order:
1. Motivating observations (how to discover the solution: small cases, failed attempts)
2. Key insight
3. Why it helps
4. Algorithm
5. Correctness proof
6. Complexity
7. Implementation notes

Verification consists of three parts: an exhaustive comparison with the brute force on all inputs up to a stated
size, random tests at moderate size (including targeted structured cases), and a timing test at maximum size.

## H. Final quality gate

Re-score with the full editorial and code in view, using gate H (preferably a fresh context, template H). Answer
explicitly: did writing the editorial show that the problem is more routine, more widely known, or heavier than it
seemed? A candidate can be rejected at this stage; record it if so. Close the trial with
`draw.py close --trial <TRIAL> --status accepted|rejected --reason "..."`.

---

## Decision rules (summary)

| Situation | Action |
|---|---|
| Key step RECOGNIZED (C5 provenance or D2 cold-solve) | Lemma-break (at most 2 cycles), mutate, or drop |
| Cold-solver finds an easier solution | Revise the constraints or rules, or drop |
| A component only serves an output format | Remove it (E-d) |
| I ≤ 1, or the solution is glue (H4/H5) | Drop |
| Out-of-syllabus key step (H3) | Drop, or lemma-break toward elementary tools |
| No candidate passes D | Close the trial `rejected`, then open a new trial |
| Passes F but fails H | Record it as a failure; do not polish it into an apparent success |

## Re-running the workflow (checklist)

1. `python randomizer/draw.py draw --trial <NEW_ID>`, then create `experiments/<NEW_ID>/process.md`.
2. C0-C5. Use the brute force with predictions, then the provenance table.
3. D1. Then D2 cold-solve (template CS). Then D3 or D4.
4. E: write the statement and solution. F: review with template R.
5. G: write the editorial, model, and stress test. H: final gate (template H). Then `draw.py close`.
6. Periodically run `python randomizer/draw.py audit`. Revise the vocabulary (as a new version file) if some
   keywords are discarded or reinterpreted far more often than others.

## Prompt templates

**G0. Generator (Stages A-D1, then E after the cold-solve; fresh agent):**
```
You are generating one original competitive-programming problem by following WORKFLOW.md (v2.2) exactly.
Trial id: <TRIAL>. Read references/design_principles.md and syllabus.md first. Get the draw with `python randomizer/draw.py draw --trial
<TRIAL>` (or `replay --trial <TRIAL>` if it was pre-registered). Work through C0-C5 (predictions before
every probe; provenance table) and D1. Then write draft_<id>.md for at most 2 candidates and STOP for D2.
Be skeptical: most candidates should be dropped, and rejecting the whole trial is an acceptable outcome.
Return: the draw, attractors, all candidates with labels, predictions vs. observations, provenance tables,
provisional scores, randomizer actions, and file paths.
```

**CS. Cold-solver (D2; fresh context; sees only the draft):**
```
Read ONLY experiments/<TRIAL>/draft_<id>.md. Try to solve it as a strong olympiad contestant would, spending
roughly 20-30 minutes of effort (small brute-force scripts are allowed). Report: (1) every idea you tried;
(2) whether it reminded you of a known problem, lemma, theorem or technique, naming it precisely and saying
whether that recognition gave you the key step; (3) your best solution and its complexity, and whether you
believe it is correct; (4) whether you suspect the intended solution is easier or harder than yours;
(5) [v2.1] the approximate time to your key step, and whether you guessed the key fact from small data
before proving it. Do not read any other file in the experiments/ folder. Write your report to
experiments/<TRIAL>/coldsolve_<id>.md.
```
Infrastructure note: during the design experiments, two subagent calls were refused once by the provider's
content filter. A rerun with neutral wording ("review a draft algorithm-contest problem") succeeded.

**R. Reviewer (Stage F; fresh context; never sees process.md or the keywords):**
```
Part 1: read ONLY experiments/<TRIAL>/statement.md. Try seriously to solve it. Write down every idea you try,
whether you reach a correct efficient solution, and any solution simpler than you would expect.
Part 2: now read solution.md. Using RUBRIC.md: check hard criteria H1-H6; try to break the proof (look for
counterexamples, and brute-force small cases if useful); run the known-pattern checks (at least 3 web searches
with different phrasings, recording queries and the closest results); and score O/I/K/B/N/C/P with one-line
reasons. Write review.md using the template in RUBRIC.md §7. Separate verified facts from judgments.
```

**H. Final gate (fresh context if possible):** the same as R, but with editorial.md and model.cpp, plus this
question: "Does the full editorial show the problem to be more routine, more widely known, or heavier to implement
than solution.md suggested?"

## Optional secondary features
- **Difficulty target:** state the target (for example "EJOI medium") in Stage E and choose constraints and
  subtasks to match. Never add knowledge requirements just to raise the difficulty.
- **Partial scoring:** use subtasks only when they correspond to natural milestones (brute force, a key special
  case, the full problem).
- **Interactive or output-only:** use these only when the QUESTION keyword is Q13 or the formal problem
  naturally requires it.
