# Solver-side Moves (used to SOLVE candidates in Stage C2-C4, never to seed them)

These are the generic reasoning moves abstracted from an earlier data bank; the source-specific moves were dropped.
Use this list as a checklist when a candidate seems hard or easy, to find hidden structure or an unintended
shortcut.

1. **Representation shift:** which representation makes each operation local (boundaries, differences,
   prefix values, positions of special elements, gaps)?
2. **Future-equivalence state:** which two partial situations behave identically for every continuation?
3. **Net effect:** what is the minimal observable effect of one operation? Do operations commute?
4. **Reverse time / reverse the process:** is the inverse process simpler or more monotone?
5. **Monotone key:** do facts only switch on (or off) as some parameter grows?
6. **Optimization to feasibility:** is "can we achieve at least X?" easier than "maximize"?
7. **Auxiliary graph:** are configurations or positions vertices of a graph with a simple structure?
8. **Exchange / local-to-global:** does a local improvement argument pin down an optimal order or shape?
9. **Global to local:** can a global condition be checked by local summaries (per element, per pair, per gap)?
10. **Complement:** is the complement easier to count or characterize?
11. **Swap viewpoint:** construct versus verify, by element versus by value, by operation versus by position.
12. **Small cases:** brute-force tiny instances, tabulate, guess, then prove.
13. **Free variables:** where can the problem be cut because one quantity can be adjusted freely?
14. **Lower bound first:** find a simple lower bound, then try to show it is always achievable.
15. **Invariants and monovariants:** what never changes, or changes in one direction only?
16. **Extremal element:** what happens to the largest, smallest, first, or last element?
17. **Counting by contribution:** count how much each element, pair, or position contributes to the total.
