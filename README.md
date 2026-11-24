# Problem-generation workflow — start here

This folder is self-contained, and it is the working root for every run. Run all commands from here.

| File / folder | Purpose | When to read |
|---|---|---|
| `WORKFLOW.md` | The complete procedure, stage by stage, with prompt templates | First |
| `references/design_principles.md` | What a good problem is, and how keywords are used | Stage A |
| `syllabus.md` | Knowledge ceiling (allowed and forbidden topics) | Stage A |
| `references/solver_moves.md` | Checklist for *solving* candidates, never for seeding them | Stages C3-C4 |
| `randomizer/` | External keyword randomizer (`draw.py`, vocabularies, `README.md`) | Stage B onwards |
| `RUBRIC.md` | Scoring anchors, hard rejection criteria, and gates D/F/H | Stages D, F, H |

Runs create `logs/draws.jsonl` (the randomizer log), `experiments/<TRIAL>/` (per-trial work), and
`problems/<slug>/` (accepted problems) inside this folder.
