# Evaluation Rubric

Used at three checkpoints: **D** (concept screening, provisional), **F** (independent review), and
**H** (final quality gate). Scores support judgment. They are **never summed**: a candidate is judged by its profile
and by the gates below.

---

## 1. Hard rejection criteria (any one means reject or send back; no score can compensate)

| Code | Criterion | Typical evidence |
|---|---|---|
| H1 | **Incorrect or ill-posed.** The intended algorithm is wrong, the statement is ambiguous in a way that changes answers, or the constraints make the problem infeasible or trivial. | Counterexample, brute-force mismatch, two readings giving different outputs |
| H2 | **Effective duplicate.** The formal problem is equivalent to a known problem, or it uses the same key insight with only surface, constraint, or wording changes. | A *found* reference (link or name) plus a mapping between the two problems |
| H3 | **Out-of-syllabus core.** An essential step needs knowledge listed under "What is forbidden" in `syllabus.md` (e.g., modular inverse, SCC, flows, KMP/hashing, lazy segment tree, Sprague-Grundy) and the insight does not overwhelmingly justify it. | The step that needs it |
| H4 | **No insight.** Once the statement is read, the solution is a direct application of a standard technique (Insight depth ≤ 1). | A reviewer solved it in one step by naming a technique |
| H5 | **Glue problem.** The solution splits into independent standard components with no meaningful interaction (often one per keyword). | Component list in which removing any one leaves standard sub-problems |
| H6 | **Inconsistency.** Statement, editorial, proof, complexity claim, and code disagree. | Diff between documents or a failed test |

H6 and fixable H1 issues mean **revise**. H2, H3, H4, and H5 mean **reject or mutate** (see WORKFLOW §D).

---

## 2. Comparative dimensions (0-4 anchors)

### O: Originality (judge the formal problem *and* the key insight, not the story)
- **0** Known problem; a reference was found.
- **1** Known problem with modified constraints, surface, or wording. The key insight is unchanged.
- **2** Familiar insight in a new setting. A contestant who remembers a specific problem or pattern gets it quickly.
- **3** New setting, and the key step is not a recognizable standard pattern, although it is related to known ideas
  (e.g., invariants of a similar type exist elsewhere). The searches found nothing close.
- **4** No close relative after a documented search, and an experienced reviewer finds the insight fresh.

**Always attach:** confidence (Low/Med/High), the searches performed, the closest problems found, and the precise
difference between the candidate and each of them. **Never** award 3+ on the basis of "I don't remember seeing it".

**Key step vs finisher.** Judge O mainly on the *key step*, meaning the step that unlocks the problem.
- A new key step that unlocks a **standard syllabus algorithm** (LIS, BFS, sorting plus greedy, prefix sums, a
  textbook DP) can earn O = 3 or 4. "A new central insight that unlocks a familiar algorithm" is the preferred kind
  of originality.
- If the finisher is a **specific known problem with its own non-trivial insight** (e.g., "Color a Tree", "Candy
  Piles", "Two Dishes"), O is capped at 2, even when the reduction to it is new. In that case the problem is a
  composition of known insights.
- If the key step itself matches a known problem, theorem, or modelling trick, O ≤ 2 regardless of the finisher.

Record the finisher and its provenance explicitly. This rule is stated explicitly because reviewers otherwise
improvise it inconsistently.

### I: Insight depth
- **0** None. Pure implementation or simulation.
- **1** One routine observation (e.g., "sort first", "answer is monotone so binary search").
- **2** One real observation that a mid-level contestant finds within minutes.
- **3** A non-obvious observation, characterization, or reduction that requires proof or experimentation to find.
- **4** Either two or more *interacting* non-obvious insights, or one surprising characterization that changes what the problem is.

### K: Knowledge requirement (lower is better)
- **0** Loops, sorting, arithmetic, prefix sums.
- **1** Core syllabus: BFS/DFS, simple DP, greedy, binary search, DSU, two pointers.
- **2** Upper syllabus: Fenwick/segment tree (no lazy), binary lifting, bitmask/digit/tree DP, Dijkstra.
- **3** Edge of syllabus, or items starred `*` in the forbidden list.
- **4** Outside the syllabus.

### B: Incidental implementation burden (lower is better; judge *after* the insight is known)
- **0** At most ~30 lines, no casework.
- **1** At most ~60 lines, minor care (indices, overflow).
- **2** At most ~120 lines, or two interacting components, or one tricky special case.
- **3** More than ~120 lines, substantial casework, or bookkeeping unrelated to the insight.
- **4** Heavy implementation with many special cases.

Also record **essential vs incidental**: list each implementation component and mark whether it *is* part of the
insight (essential) or only plumbing (incidental).

### N: Naturalness
- **0** Arbitrary rules exist only to force the intended technique.
- **1** Several artificial constraints or ad hoc parameters.
- **2** Coherent, but with one ad hoc rule or constant.
- **3** Clean. Every rule is motivated, and the problem is easy to state precisely.
- **4** Strikingly simple. It could be stated in two sentences as a puzzle.

### C: Correctness evidence
- **fail**: a counterexample is known.
- **sketch**: a proof idea only.
- **proved**: a complete proof is written.
- **proved + verified**: a complete proof, and the model code matches a brute force exhaustively on all small inputs
  (state the bounds) plus random larger tests.

### P: Presentation
- **0** The statement is ambiguous or the editorial is missing.
- **1** Understandable, but with gaps.
- **2** Precise statement. The editorial is correct but presents the trick without motivation.
- **3** Precise statement with examples. The editorial shows how to *discover* the insight, and the proof is complete.
- **4** As 3, and also pedagogically excellent (motivating small cases, clear lemma structure).

### Insight-to-load ratio (qualitative, the main summary judgment)
**High** if I ≥ 3 and K ≤ 2 and B ≤ 1. **Medium** if I ≥ 3 with B = 2, or if I = 2 with K ≤ 1 and B ≤ 1.
Otherwise **Low**.

---

## 3. Gates

| Checkpoint | Proceed if |
|---|---|
| D (screening, provisional) | No hard reject is apparent, O ≥ 2 (provisional), I ≥ 2, K ≤ 2, B ≤ 2, N ≥ 2. **[v2]** The key step is tagged DERIVED in the provenance table, and the D2 cold-solver did not reach it by naming a known problem or lemma |
| F (independent review) | No hard reject. A statement-only solver did **not** find the intended solution by naming a technique. No easier unintended solution passes the constraints |
| H (final) | No hard reject, O ≥ 3 (Med confidence) **or** O = 2 with I = 4, I ≥ 3, K ≤ 2, B ≤ 2, N ≥ 3, C = proved + verified, P ≥ 3 |

To rank candidates that pass a gate, compare in this order: I, then O, then the insight-to-load ratio, then N.
A candidate that passes D but fails H is **recorded as a failure**. It is not polished into an apparent success.

---

## 4. Known-pattern dependence checks (run all of them at F and H)

1. **Formal one-liner:** strip the story and write the problem in one sentence. Search the web for it and for
   the key-insight phrase (at least 3 queries with different wording). Record the queries.
2. **Closest relatives:** name the 3 closest known problems or patterns, and state exactly how the key insight differs.
3. **Memory test:** would remembering one specific problem make this one easy? If yes, which problem?
4. **Technique-name test:** can the solution be described as "<technique name> + trivial adaptation"?
5. **Decomposition test:** remove the claimed insight. Are the remaining parts standard and independent? Does the
   insight connect them, or is it just one more part?
6. **Sequence test:** if the answers for small parameters form an integer sequence, check it in OEIS
   (`https://oeis.org/search?q=<terms>&fmt=short`). A famous sequence means the problem may be known.
7. **Trick-type test:** name the key step's *type* at an intermediate level of detail. Examples:
   "an exact power-of-two potential that changes by one per move", "fold into one sequence and take the LIS". Do not
   stop at something as broad as "invariant". Search for that type. If a known problem uses the same trick type as
   *its* key step, then O ≤ 2. In the design experiments, every originality failure at gate F or gate H was of this
   kind, not a duplicate problem.

## 5. Knowledge and burden checks

- List every algorithm or data structure in the model solution. Check each against `syllabus.md`.
- Count model-code lines (excluding I/O boilerplate) and special cases. Mark each as essential or incidental.
- Ask: "Could a contestant who finds the insight still fail mainly because of implementation?" If yes, then B ≥ 2.
- Ask: "Does the statement need a long definition section?" If yes, lower N or P.

## 6. Uncertainty reporting

Every review must end with:
- **Verified facts**, such as brute-force agreement or a found duplicate with a link.
- **Judgments**, such as the depth and naturalness scores, with one-line reasons.
- **Unverified claims**, especially originality, labelled with confidence and the searches behind them.
- **Reviewer independence**: who reviewed (fresh context or same context), what they saw first, and whether the
  reviewer is the same model family as the generator. Same-model agreement is weak evidence.

## 7. Review template

```
Candidate: <id>          Reviewer context: <fresh / same>      Saw statement first: <yes/no>
F1 statement-only attempt: <ideas tried, whether the key insight was found, time/effort proxy, alternative solutions>
Hard criteria: H1 .. H6 -> <pass/fail + evidence>
O <0-4> (conf <L/M/H>; searches: ...; closest: ...)
I <0-4>  K <0-4>  B <0-4> (essential: ..., incidental: ...)  N <0-4>  C <level>  P <0-4>
Insight-to-load ratio: <High/Medium/Low>
Gate decision: <advance / revise / mutate / reject>  Reason: ...
Verified facts / Judgments / Unverified claims: ...
```
