#!/usr/bin/env python3
"""External keyword randomizer for the problem-generation workflow.

Standard library only. All randomness comes from this script: the seed is taken
from OS entropy (secrets) unless given, and every selection is derived from the
seed by SHA-256, so draws are exactly replayable and inspectable.

Selection rule (version independent):
    h_c = SHA-256("<seed>|<mode>|<slot>|<c>") as a 256-bit integer, c = 0,1,2,...
    take the first c with (h_c mod 2^64) < floor(2^64 / n) * n  (rejection => unbiased)
    index = (h_c mod 2^64) mod n
"Slot" is the facet name plus position; incompatible pairs (vocab 'incompatible')
are resolved by re-drawing the LATER slot with the next counter value, and every
such internal re-draw is logged.

Policy enforced here (see WORKFLOW.md §B):
  * one draw per trial id; a new draw needs a new trial id (old trial stays logged)
  * protected facets cannot be discarded; at most `max_discards` discards per trial
  * at most 2 mutation draws per trial
  * every discard / reinterpretation / mutation / close is appended to the log

Usage examples:
  python randomizer/draw.py draw --trial T07
  python randomizer/draw.py draw --trial T08 --mode technique
  python randomizer/draw.py replay --trial T07
  python randomizer/draw.py replay --seed 123 --mode world
  python randomizer/draw.py reinterpret --trial T07 --keyword D03 --as "rotation of a tree edge"
  python randomizer/draw.py discard --trial T07 --keyword T22 --reason "..."
  python randomizer/draw.py mutate --trial T07 --reason "candidate equals known problem X"
  python randomizer/draw.py close --trial T07 --status rejected --reason "..."
  python randomizer/draw.py status --trial T07
  python randomizer/draw.py audit
  python randomizer/draw.py list --facet twist
"""
import argparse
import datetime
import hashlib
import json
import os
import secrets
import sys

SCRIPT_VERSION = "1.1"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_VOCAB = os.path.join(HERE, "vocab_v2.json")
DEFAULT_LOG = os.path.join(ROOT, "logs", "draws.jsonl")
MAX_MUTATIONS = 2
CLOSE_STATUSES = ("accepted", "rejected", "revised", "abandoned")


def fail(msg):
    print(json.dumps({"ok": False, "error": msg}, indent=2))
    sys.exit(1)


def load_vocab(path):
    with open(path, "rb") as f:
        raw = f.read()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def pick_index(seed, mode, slot, n, start=0):
    """Return (index, counter_used) using unbiased hash-based selection."""
    limit = (2 ** 64 // n) * n
    c = start
    while True:
        h = int.from_bytes(hashlib.sha256(f"{seed}|{mode}|{slot}|{c}".encode()).digest(), "big")
        v = h % (2 ** 64)
        if v < limit:
            return v % n, c
        c += 1


def conflicts(vocab, chosen_ids, new_id):
    for rule in vocab.get("incompatible", []):
        for cid in chosen_ids:
            if (rule["a"] == cid and new_id in rule["b"]) or (rule["a"] == new_id and cid in rule["b"]):
                return rule
    return None


def compute_draw(vocab, seed, mode):
    if mode not in vocab["modes"]:
        fail(f"unknown mode {mode}; available: {list(vocab['modes'])}")
    spec = vocab["modes"][mode]
    if "pool_from" in spec:
        pool = [(f, e) for f in spec["pool_from"] for e in vocab["facets"][f]]
        slots = [("pool", i) for i in range(spec["count"])]
    else:
        slots = [(f, i) for i, f in enumerate(spec["facets"])]
    roles = spec["roles"]
    chosen, resamples = [], []
    for facet, pos in slots:
        entries = pool if facet == "pool" else [(facet, e) for e in vocab["facets"][facet]]
        slot = f"{facet}#{pos}"
        counter = 0
        while True:
            idx, used = pick_index(seed, mode, slot, len(entries), counter)
            src_facet, entry = entries[idx]
            ids = [k["id"] for k in chosen]
            rule = None if entry["id"] not in ids else {"reason": "duplicate keyword"}
            rule = rule or conflicts(vocab, ids, entry["id"])
            if rule is None:
                break
            resamples.append({"slot": slot, "rejected": entry["id"], "reason": rule["reason"]})
            counter = used + 1
        role = roles.get(src_facet, roles.get("*", "discardable"))
        chosen.append({"facet": src_facet, "id": entry["id"], "text": entry["text"], "role": role})
    return chosen, resamples, spec.get("max_discards", 0)


def read_log(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def append_log(path, record):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    record["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def trial_events(log, trial):
    return [r for r in log if r.get("trial") == trial]


def trial_draw(log, trial):
    for r in trial_events(log, trial):
        if r["event"] == "draw":
            return r
    fail(f"no draw recorded for trial {trial}")


def is_closed(log, trial):
    return any(r["event"] == "close" for r in trial_events(log, trial))


def cmd_draw(a):
    vocab, vhash = load_vocab(a.vocab)
    log = read_log(a.log)
    if not a.no_log and trial_events(log, a.trial):
        fail(f"trial {a.trial} already exists; one draw per trial. Close it and use a new trial id.")
    seed = a.seed if a.seed is not None else secrets.randbits(63)
    kws, resamples, max_discards = compute_draw(vocab, seed, a.mode)
    open_trials = sorted({r["trial"] for r in log if r["event"] == "draw" and not is_closed(log, r["trial"])})
    rec = {
        "event": "draw", "trial": a.trial, "mode": a.mode, "seed": seed,
        "seed_source": "user" if a.seed is not None else "os_entropy(secrets.randbits(63))",
        "vocab_file": os.path.relpath(a.vocab, ROOT).replace("\\", "/"), "vocab_version": vocab["version"],
        "vocab_sha256": vhash, "script_version": SCRIPT_VERSION, "keywords": kws,
        "internal_resamples": resamples, "max_discards": max_discards,
        "open_trials_at_draw_time": open_trials, "note": a.note,
    }
    if not a.no_log:
        append_log(a.log, rec)
    print(json.dumps({"ok": True, "logged": not a.no_log, **rec}, indent=2, ensure_ascii=False))


def cmd_replay(a):
    if a.trial:
        rec = trial_draw(read_log(a.log), a.trial)
        vocab_path = os.path.join(ROOT, rec["vocab_file"])
        vocab, vhash = load_vocab(vocab_path)
        kws, resamples, _ = compute_draw(vocab, rec["seed"], rec["mode"])
        print(json.dumps({
            "ok": True, "trial": a.trial, "seed": rec["seed"], "mode": rec["mode"],
            "vocab_hash_matches": vhash == rec["vocab_sha256"],
            "replay_matches_log": [k["id"] for k in kws] == [k["id"] for k in rec["keywords"]],
            "keywords": kws, "internal_resamples": resamples}, indent=2, ensure_ascii=False))
    else:
        if a.seed is None:
            fail("replay needs --trial or --seed")
        vocab, vhash = load_vocab(a.vocab)
        kws, resamples, _ = compute_draw(vocab, a.seed, a.mode)
        print(json.dumps({"ok": True, "seed": a.seed, "mode": a.mode, "vocab_sha256": vhash,
                          "keywords": kws, "internal_resamples": resamples}, indent=2, ensure_ascii=False))


def keyword_of(rec, kid):
    for k in rec["keywords"]:
        if k["id"] == kid:
            return k
    fail(f"keyword {kid} is not part of the draw for trial {rec['trial']}")


def require_open(log, trial):
    if is_closed(log, trial):
        fail(f"trial {trial} is closed")


def cmd_discard(a):
    log = read_log(a.log)
    rec = trial_draw(log, a.trial)
    require_open(log, a.trial)
    k = keyword_of(rec, a.keyword)
    if k["role"] == "protected":
        fail(f"{a.keyword} ({k['facet']}) is protected and cannot be discarded; reinterpret it instead")
    done = [r for r in trial_events(log, a.trial) if r["event"] == "discard"]
    if any(r["keyword"] == a.keyword for r in done):
        fail(f"{a.keyword} already discarded")
    if len(done) >= rec["max_discards"]:
        fail(f"discard limit reached ({rec['max_discards']}) for trial {a.trial}")
    if len(a.reason.strip()) < 20:
        fail("reason must explain which readings were tried and why they failed (>= 20 chars)")
    out = {"event": "discard", "trial": a.trial, "keyword": a.keyword, "text": k["text"],
           "facet": k["facet"], "reason": a.reason}
    append_log(a.log, out)
    print(json.dumps({"ok": True, **out}, indent=2, ensure_ascii=False))


def cmd_reinterpret(a):
    log = read_log(a.log)
    rec = trial_draw(log, a.trial)
    require_open(log, a.trial)
    k = keyword_of(rec, a.keyword)
    out = {"event": "reinterpret", "trial": a.trial, "keyword": a.keyword, "text": k["text"], "as": a.as_}
    append_log(a.log, out)
    print(json.dumps({"ok": True, **out}, indent=2, ensure_ascii=False))


def cmd_mutate(a):
    log = read_log(a.log)
    rec = trial_draw(log, a.trial)
    require_open(log, a.trial)
    done = [r for r in trial_events(log, a.trial) if r["event"] == "mutate"]
    if len(done) >= MAX_MUTATIONS:
        fail(f"mutation limit reached ({MAX_MUTATIONS}) for trial {a.trial}")
    vocab, vhash = load_vocab(os.path.join(ROOT, rec["vocab_file"]))
    entries = vocab["facets"]["mutation"]
    taken = {r["keyword"] for r in done}
    counter = 0
    while True:
        idx, used = pick_index(rec["seed"], "mutation", f"mutation#{len(done)}", len(entries), counter)
        if entries[idx]["id"] not in taken:
            break
        counter = used + 1
    e = entries[idx]
    out = {"event": "mutate", "trial": a.trial, "keyword": e["id"], "text": e["text"],
           "derived_from_seed": rec["seed"], "index": len(done), "reason": a.reason}
    append_log(a.log, out)
    print(json.dumps({"ok": True, **out}, indent=2, ensure_ascii=False))


def cmd_close(a):
    log = read_log(a.log)
    trial_draw(log, a.trial)
    require_open(log, a.trial)
    out = {"event": "close", "trial": a.trial, "status": a.status, "reason": a.reason}
    append_log(a.log, out)
    print(json.dumps({"ok": True, **out}, indent=2, ensure_ascii=False))


def cmd_note(a):
    log = read_log(a.log)
    trial_draw(log, a.trial)
    out = {"event": "note", "trial": a.trial, "text": a.text}
    append_log(a.log, out)
    print(json.dumps({"ok": True, **out}, indent=2, ensure_ascii=False))


def cmd_status(a):
    log = read_log(a.log)
    rec = trial_draw(log, a.trial)
    ev = trial_events(log, a.trial)
    nd = sum(r["event"] == "discard" for r in ev)
    nm = sum(r["event"] == "mutate" for r in ev)
    print(json.dumps({"ok": True, "trial": a.trial, "closed": is_closed(log, a.trial),
                      "discards_left": rec["max_discards"] - nd, "mutations_left": MAX_MUTATIONS - nm,
                      "events": ev}, indent=2, ensure_ascii=False))


def cmd_audit(a):
    log = read_log(a.log)
    trials = {}
    for r in log:
        t = trials.setdefault(r["trial"], {"draws": 0, "discards": [], "reinterpretations": 0,
                                           "mutations": [], "status": "open"})
        if r["event"] == "draw":
            t["draws"] += 1
            t["mode"] = r["mode"]
            t["keywords"] = [f"{k['id']}:{k['text']}" for k in r["keywords"]]
        elif r["event"] == "discard":
            t["discards"].append(r["keyword"])
        elif r["event"] == "reinterpret":
            t["reinterpretations"] += 1
        elif r["event"] == "mutate":
            t["mutations"].append(r["keyword"])
        elif r["event"] == "close":
            t["status"] = r["status"]
    summary = {
        "trials": len(trials),
        "by_status": {s: sum(t["status"] == s for t in trials.values()) for s in CLOSE_STATUSES + ("open",)},
        "total_discards": sum(len(t["discards"]) for t in trials.values()),
        "total_mutations": sum(len(t["mutations"]) for t in trials.values()),
        "integrity_violations": [k for k, t in trials.items() if t["draws"] != 1],
    }
    print(json.dumps({"ok": True, "summary": summary, "trials": trials}, indent=2, ensure_ascii=False))


def cmd_list(a):
    vocab, vhash = load_vocab(a.vocab)
    facets = [a.facet] if a.facet else list(vocab["facets"])
    print(json.dumps({"ok": True, "version": vocab["version"], "vocab_sha256": vhash,
                      "facets": {f: vocab["facets"][f] for f in facets}}, indent=2, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="External keyword randomizer (see module docstring).")
    p.add_argument("--log", default=DEFAULT_LOG)
    p.add_argument("--vocab", default=DEFAULT_VOCAB)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("draw"); s.add_argument("--trial", required=True)
    s.add_argument("--mode", default="world"); s.add_argument("--seed", type=int)
    s.add_argument("--note", default=""); s.add_argument("--no-log", action="store_true")
    s.set_defaults(f=cmd_draw)
    s = sub.add_parser("replay"); s.add_argument("--trial"); s.add_argument("--seed", type=int)
    s.add_argument("--mode", default="world"); s.set_defaults(f=cmd_replay)
    s = sub.add_parser("discard"); s.add_argument("--trial", required=True)
    s.add_argument("--keyword", required=True); s.add_argument("--reason", required=True)
    s.set_defaults(f=cmd_discard)
    s = sub.add_parser("reinterpret"); s.add_argument("--trial", required=True)
    s.add_argument("--keyword", required=True); s.add_argument("--as", dest="as_", required=True)
    s.set_defaults(f=cmd_reinterpret)
    s = sub.add_parser("mutate"); s.add_argument("--trial", required=True)
    s.add_argument("--reason", required=True); s.set_defaults(f=cmd_mutate)
    s = sub.add_parser("close"); s.add_argument("--trial", required=True)
    s.add_argument("--status", required=True, choices=CLOSE_STATUSES)
    s.add_argument("--reason", required=True); s.set_defaults(f=cmd_close)
    s = sub.add_parser("note"); s.add_argument("--trial", required=True)
    s.add_argument("--text", required=True); s.set_defaults(f=cmd_note)
    s = sub.add_parser("status"); s.add_argument("--trial", required=True); s.set_defaults(f=cmd_status)
    s = sub.add_parser("audit"); s.set_defaults(f=cmd_audit)
    s = sub.add_parser("list"); s.add_argument("--facet"); s.set_defaults(f=cmd_list)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
