# Keyword Randomizer

`draw.py` is a single file that uses only the Python standard library. The vocabulary lives in `vocab_v2.json`, which
is the default; `vocab_v1.json` is kept so that older draws can still be replayed. The append-only log is
`../logs/draws.jsonl` (that is, `workflow_v2/logs/draws.jsonl`), and it is created on first use. Run all commands from
the `workflow_v2/` folder.

## Quick start

```bash
python randomizer/draw.py draw --trial T07                 # new world-mode draw (seed from OS entropy), logged
python randomizer/draw.py replay --trial T07               # recompute from the log; checks vocab hash + match
python randomizer/draw.py replay --seed 123 --mode world   # dry replay of any seed (not logged)
python randomizer/draw.py reinterpret --trial T07 --keyword D03 --as "rotation of a tree edge"
python randomizer/draw.py discard --trial T07 --keyword T22 --reason "<readings tried and why they failed>"
python randomizer/draw.py mutate  --trial T07 --reason "<candidate equals known problem X>"
python randomizer/draw.py close   --trial T07 --status rejected --reason "<why>"
python randomizer/draw.py status  --trial T07              # events + remaining discards/mutations
python randomizer/draw.py audit                            # whole-log summary + integrity check
python randomizer/draw.py list --facet twist               # inspect vocabulary
```
Every command prints JSON (`"ok": true/false`), so an agent can parse the output directly.

Demonstrated invocation (actual output of a design-experiment draw, made with vocabulary v1):
```
$ python randomizer/draw.py draw --trial E1-W2 --note "E1 arm W"
{"ok": true, "trial": "E1-W2", "mode": "world", "seed": 2052074123490671346,
 "seed_source": "os_entropy(secrets.randbits(63))", "vocab_sha256": "5600993a...",
 "keywords": [{"facet":"object","id":"O28","text":"staircase shape (monotone lattice path)","role":"protected"},
              {"facet":"dynamics","id":"D16","text":"take an element from either end","role":"discardable"},
              {"facet":"question","id":"Q17","text":"minimum number of groups in a partition","role":"protected"},
              {"facet":"twist","id":"T25","text":"simultaneous updates (all at once)","role":"discardable"}], ...}
```

## Sampling mechanism (inspectable and version-independent)

- Seed: `secrets.randbits(63)` (OS entropy), unless `--seed` is given (in that case `seed_source: user` is logged).
- Selection for slot *s* with *n* entries: `h_c = SHA-256("<seed>|<mode>|<s>|<c>")`, c = 0, 1, .... Take the low 64 bits.
  Accept the first c for which the value is below `floor(2^64/n)*n` (rejection keeps the selection unbiased). Index = value mod n.
  The rule can be reimplemented in a few lines in any language, and it does not depend on Python's `random` module.
- Incompatible pairs (listed in the vocabulary) cause the later slot to be re-drawn with the next counter. Each
  internal re-draw is logged in `internal_resamples`. The model never chooses.
- The record stores the seed, mode, vocabulary file, its SHA-256, the script version, the keywords with roles, the open trials at
  draw time, and a timestamp. `replay --trial` verifies both the hash and the keyword list.
- Uniformity check (20,000 simulated seeds): the per-entry frequency in every facet lies within ±2σ of uniform. 1.5% of draws
  needed an internal resample.

## Parameter decisions and rationale

| # | Parameter | Decision | Intended effect / evidence |
|---|---|---|---|
| 1 | Vocabulary size / composition | 30 objects, 32 dynamics, 18 questions, 30 twists (110 world keywords, about 520k world combinations). There are also 40 technique keywords (baseline arm only) and 16 mutations. | The vocabulary is large enough that repeated draws rarely coincide, and small enough that each entry could be checked by hand for syllabus fit and for admitting several readings. **No solution techniques** appear in the world facets. This is the main design choice, because analysis of earlier data banks showed that technique-first seeding produces reskinned technique combinations. |
| 2 | Taxonomy | Facets by **role in the problem**: what the input is, what can happen to it, what is asked, and one structural twist. | Every draw then reads as a coherent problem sketch ("on a *permutation*, by *reversing segments*, ask the *lexicographically smallest result*, *cyclically*"), not as a bag of concepts that must be glued together. Abstraction is mixed on purpose: OBJECT entries are broad ("tree"), while DYNAMICS and TWIST entries are mid-level ("remove a leaf", "every prefix must satisfy"). This is the "one structural keyword plus several conceptual keywords" pattern. |
| 3 | Distribution | Uniform within each facet, and exactly one keyword per facet. | This is the simplest option that can be inspected. Facet balance comes from the taxonomy, not from weights. Weighting by "quality" would bring back the designer's own attractors. |
| 4 | Keywords per draw | 4. | Fewer than 3 lets the model fall back on its favourite problems. More than 4 forces artificial gluing. With 4 role-separated slots, all of them can live naturally in one formal statement. |
| 5 | Roles | OBJECT and QUESTION are **protected** (mandatory). DYNAMICS and TWIST are **discardable**. | OBJECT and QUESTION determine *what kind of problem* this is, which is where the diversity is. Left to choose, models drift to "array + minimum cost". DYNAMICS and TWIST are the slots most likely to clash. |
| 6 | Discarding allowed? | Yes, but only after Stage C2 shows at least 2 serious readings that use the keyword, with the reason logged (minimum 20 characters, enforced). | Forcing every keyword in produces artificial problems. A free discard would defeat the external randomness. |
| 7 | How many | At most **1** per trial (enforced). | At least 3 of 4 externally chosen keywords always survive. |
| 8 | Protected categories | OBJECT and QUESTION (enforced). | See row 5. |
| 9 | Incompatibility | *Hard* contradictions (e.g. "static structure" combined with "minimum number of operations") are listed in the vocabulary and **re-drawn by the script**. *Soft* tension is handled by **reinterpretation** (logged), and if that fails, by a discard. | Keeps every choice outside the model, or at least logged. |
| 10 | Additional draws | (a) **Mutation draw**: at most 2 per trial (enforced). It is allowed only when a screened candidate turns out to be a known problem or an attractor, and the drawn mutation must be applied. (b) **New trial**: only after closing the current one with a reason (one draw per trial id is enforced; abandoned trials remain visible in `audit`). | Mutation gives an *external* way out of attractors instead of a growing forbidden list. Making re-draws cost a documented failed trial keeps cherry-picking at the draw level visible and expensive. |

## Selection-bias controls
- One draw per trial id. Draws can be pre-registered before generation starts, as was done in the design
  experiments.
- `open_trials_at_draw_time` exposes trials that were opened and never closed.
- `audit` reports `integrity_violations` (any trial whose draw count is not exactly 1), along with discard and mutation counts.
- If a keyword is frequently discarded or reinterpreted, fix it **in the vocabulary**, as a new version file. Do not let
  individual draws work around it. Keep old vocabulary files so that old seeds can still be replayed (`replay` reads the vocabulary file recorded in the log).

## Vocabulary versions
- `vocab_v1.json`: used in the first design experiment (sha256 `5600993a...`).
- `vocab_v2.json` (current default; script 1.1) changes five entries, based on an experimental finding. Keywords that
  only set the output format tended to attach a standard data-structure layer to an insight that was already
  complete. Two candidates in the first experiment had this problem and were flagged H5-borderline. The
  replacements:
  - Q09 "answer many queries about parts of the input" → "decide whether two given objects are equivalent under the operations"
  - Q18 "for every k, report the optimum" → "smallest parameter value that makes the goal achievable"
  - T10 "answer required after every update" → "one special element behaves differently"
  - T11 "answer required for every starting point" → "identical items are indistinguishable"
  - M07 "require the answer for every prefix" → "allow one exceptional operation of a different kind"

  The incompatibility list was updated to match. Both files are kept, and `replay --trial` loads whichever
  vocabulary file the log records for that trial.

## Modes
- `world` (default): OBJECT + DYNAMICS + QUESTION + TWIST.
- `technique`: 3 technique names. This mode exists only to reproduce the legacy approach as an experimental baseline.
- `uniform`: 4 keywords drawn uniformly from the union of the world facets, with no taxonomy (an ablation; not used so far).
