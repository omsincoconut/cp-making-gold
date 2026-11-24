# Design Principles (generator-facing, Stage A)

This is deliberately short and abstract. It contains **no example problems and no technique menu**, because
concrete exemplars anchor generation. Earlier data banks of detailed examples made generators reproduce the same
few constructions.

## What we want

1. **A simple question about a simple object has a surprising, provable answer.** The difficulty is in
   *finding* a structural fact, such as an invariant, a characterization, a canonical form, a hidden monotonicity,
   or a reduction that changes what the problem "is". It is not in knowing a technique or writing a lot of code.
2. **The naive approach fails for a visible reason.** A contestant should see quickly why brute force or the
   obvious greedy/DP is too slow or wrong. The constraints exist to separate the insight from naive approaches.
   They are not there to force a pet technique.
3. **Low load.** Once the insight is found, the remaining algorithm should use elementary syllabus tools.
   Prefer a model solution under ~80 lines with little casework.
4. **Formal first, story last.** Write the problem as a precise mathematical question first. A story is
   optional and must never hide information, add special cases, or be needed to understand the task.

## How keywords are used

- Keywords describe the *problem world*: an object, something that can happen to it, a question, and a twist.
  They are seeds for **what the problem is about**, never for which algorithm solves it.
- Each kept keyword must shape the **formal** problem. A keyword that appears only in the story does not count.
- Keywords may be read non-literally. "Rotation" can mean rotating a tree edge, a cyclic shift, or a 90-degree
  turn. Log every reinterpretation.
- Do not build "keyword A solved by technique X, then keyword B solved by technique Y". If the kept keywords
  map one-to-one onto independent solution components, the candidate fails the decomposition test.

## Habits that produce depth

- **Name your attractors first.** Before inventing anything, write down the well-known problems the draw
  reminds you of. Those are where you will drift by default. Your candidate must not share their key insight.
- **Diverge before converging.** Produce several genuinely different formal questions before judging any.
- **Explore by experiment.** Brute-force small instances and look at the data. Many good insights are
  patterns you would not have predicted. A pattern is only a hypothesis until it is proved.
- **Prefer characterizations over algorithms.** "Exactly the configurations with property P are reachable"
  is usually deeper and cleaner than "simulate cleverly".
- **Ask whether the problem survives a hostile solver.** Look for an easier unintended solution under your
  constraints, such as a simpler greedy, a small-answer observation, or a formula you can look up.

## What to avoid (general causes, not a style list)

- Starting from a technique and dressing it in a story. The originality then lies only in the dressing.
- Stacking constraints until only one technique fits. That makes the problem artificial.
- Several independent sub-tasks glued together. That adds implementation load without insight.
- Heavy or obscure prerequisites. Check `syllabus.md`, especially the "What is forbidden" section.
- Claiming novelty from memory. Search, and record what you searched.
