#!/usr/bin/env python3
"""Decide how to answer a new crisis: three readings x crisis-specific candidates x 2 seeds, locked decisions held fixed.

    .venv/bin/python -I code/crisis_decide.py <crisis_id>            # readings + candidates + runs + summary
    .venv/bin/python -I code/crisis_decide.py <crisis_id> --report   # summary only, from saved runs

Output: runs_dev/crisis/<crisis_id>/{readings.json, candidates/*.json, <reading>__<cand>__s<seed>/, summary.json}
Locked decisions (already saved on the TALP dashboard) live in config/locked.json and are part of every run.
"""
import argparse
import copy
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import List, Literal

from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm import LLM  # noqa: E402
import world as W  # noqa: E402
from announcements import Effect, IST, WEEK1_START, effect_to_world  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LOCKED = ROOT / "config" / "locked.json"
READER = os.environ.get("TALP_READER_MODEL", "gemini-3.5-flash")
ACTIONS = {  # dossier wording -> levels
    "Lease an aircraft with crew for 2 weeks": ["1 aircraft", "2 aircraft"],
    "Backup ground handling contract at both bases for the strike days": ["on"],
    "Free changes and cancellations for bookings in a 2-week window": ["on"],
    "Goodwill for affected passengers, up to 10,000 passengers": ["a $75 travel credit", "$50 cash"],
    "Rebooking deal with a partner airline for 2 disrupted weeks": ["on"],
    "Hotel rooms held for stranded passengers, whatever the cause": ["on"],
    "Extra airport and call-center staff for 2 weeks": ["on"],
    "Fare cap on the busiest routes for 2 weeks": ["on"],
    "Fare sale on quiet routes for 2 weeks": ["on"],
    "Double loyalty points for affected passengers": ["on"],
    "Merge low-load flights, announced at least 7 days ahead": ["on"],
}
NOT_MODELED = ("fare cap", "fare sale", "merge low-load")
THRESHOLDS = {"goal_1": 98.0, "goal_4": 96.0, "goal_3": 12.0}


class Variant(BaseModel):
    reading: str
    effects: List[Effect]


class Three(BaseModel):
    mild: Variant
    medium: Variant
    severe: Variant


class Act(BaseModel):
    action: Literal[tuple(ACTIONS)]
    level: str


class Candidate(BaseModel):
    code: str
    label: str
    target: str
    target_rule: Literal["all", "upcoming_travelers", "crisis_exposed", "crisis_affected"]
    actions: List[Act]
    message: str
    channels: List[Literal["app", "email", "text message", "social media"]]
    why: str


class Candidates(BaseModel):
    candidates: List[Candidate]


def locked():
    return json.loads(LOCKED.read_text())["decisions"] if LOCKED.exists() else []


def company_week_now():
    t = datetime.now(IST)
    return int((t - WEEK1_START).total_seconds() // 1800) + 1 if t >= WEEK1_START else 0


def full_text(crisis):
    ups = " ".join(f"UPDATE (week {u['week']}): {u['text']}" for u in crisis.get("updates", []))
    return (crisis["text"] + " " + ups).strip()


def three_readings(llm, crisis):
    prompt = f"""A crisis was announced to Kestrel Air, a fictional US low-cost airline (bases MCO and PHL, 6 in 10 flights
touch a base, 210,000 passengers a week; week {crisis['announced_week']} of a ten-week calendar that runs Nov 2, 2026 to Jan 10, 2027).
Announcement: {full_text(crisis)}
Our current reading: {crisis['reading']}
Current effects: {json.dumps(crisis['effects'])}

The text is vague on purpose. Give three readings of the SAME announcement that a careful analyst would find plausible:
mild (it turns out smaller than feared), medium (most likely), severe (a bad but survivable case; nothing sinks the company).
For each: a 1-2 sentence reading and the flight-operation effects (exact dates, airports or ["ALL"], cancel_rate 0-1,
delay_hours, bags, assistance, cause, mitigating_actions). Effects [] if the crisis does not touch flight operations.
Menu actions for mitigating_actions: {', '.join(sorted(W.MENU))}."""
    _, r = llm.json(prompt, Three, week=crisis["announced_week"])
    return {k: {"reading": v["reading"], "effects": [effect_to_world(e) for e in v["effects"]]} for k, v in r.items()}


def candidates(llm, crisis, week, budget):
    lock = locked()
    prompt = f"""You advise Kestrel Air's board. A new crisis: {full_text(crisis)}
Our reading: {crisis['reading']} {' '.join(u.get('reading', '') for u in crisis.get('updates', []))}
Already locked decisions (fixed, do not repeat): {json.dumps([{k: d[k] for k in ('week', 'actions', 'message')} for d in lock]) or 'none'}
Propose 4 DIFFERENT single decisions to answer this crisis, taking effect in week {week} ({W.week_label(week)}).
Each uses 1 to 3 actions from this menu (exact names, with one listed level): {json.dumps(ACTIONS)}.
Total cost of one decision must be at most ${budget:.2f}M (CFO costs: {json.dumps({k: v['levels'] for k, v in W.MENU.items()})}).
target_rule: "crisis_exposed" (people booked on the crisis's dates and airports), "crisis_affected" (people whose flights it
actually disrupted, only sensible after it happened), "upcoming_travelers" or "all". target: one plain sentence.
message: the exact words passengers will read, at most 600 characters, honest (no promise the company cannot keep, no
false or misleading statement), naming only what the actions really provide. channels: from app, email, text message,
social media. why: exactly three short lines separated by newlines. Red lines: safety is never traded; refunds required
by DOT rules are always paid and are not a decision; never cancel all flights at a base.
Make the four meaningfully different (e.g. protect before it hits / help on the day / recover after / message-light cheap
option). code: short snake_case; label: 2-5 words."""
    _, r = llm.json(prompt, Candidates, week=week)
    out, seen = [], set()
    for c in r["candidates"]:
        d = {"week": week, "target": c["target"],
             "target_rule": c["target_rule"] if c["target_rule"] in ("all", "upcoming_travelers") else f"{c['target_rule']}:{crisis['id']}",
             "actions": [{"action": a["action"], "level": a["level"] if a["level"] in ACTIONS[a["action"]] else ACTIONS[a["action"]][0]}
                         for a in c["actions"]][:3],
             "message": c["message"][:600], "channels": c["channels"] or ["app"], "why": c["why"]}
        try:
            cost = sum(W.MENU[W.norm_action(a["action"])]["levels"][a["level"]] for a in d["actions"])
            assert d["actions"] and cost <= budget + 1e-9 and c["code"] not in seen
        except Exception:
            continue
        seen.add(c["code"])
        out.append({"code": c["code"], "label": c["label"], "cost": round(cost, 2), "decision": d,
                    "not_modeled": [a["action"] for a in d["actions"] if a["action"].lower().startswith(NOT_MODELED)]})
    return out


def run_one(base, reading, cand, seed, crises_file, dec_file):
    name = f"{reading}__{cand}__s{seed}"
    cmd = [str(ROOT / ".venv/bin/python"), "-I", "code/sim.py", "--name", name, "--seed", str(seed),
           "--out", str(base.relative_to(ROOT)), "--type", "plan", "--workers", "16", "--probe",
           "--decisions", str(dec_file), "--crises", str(crises_file)]
    env = dict(os.environ, SSL_CERT_FILE=os.environ.get("SSL_CERT_FILE", "/etc/ssl/cert.pem"))
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)
    print(("ok   " if r.returncode == 0 else "FAIL ") + name + ("" if r.returncode == 0 else "\n" + r.stderr[-600:]), flush=True)


def summarize(base, crisis_id):
    meta = json.loads((base / "meta.json").read_text())
    rows = {}
    for d in base.iterdir():
        if (d / "metrics.json").exists():
            reading, cand, _ = d.name.split("__")
            m = json.loads((d / "metrics.json").read_text())
            W_ = [json.loads(l) for l in open(d / "weekly.jsonl", encoding="utf-8")]
            moved = len({r["persona"] for r in W_ if "change to a different date" in r["actions"]})
            rows.setdefault(cand, {}).setdefault(reading, []).append(
                {**{k: m[k] for k in ("goal_1", "goal_2", "goal_3", "goal_3b", "goal_4")},
                 "other": m["detail"]["final_status_mix_pct"]["moved to another airline"], "moved": moved})
    def avg(xs, k):
        return round(sum(x[k] for x in xs) / len(xs), 2)
    table = {}
    for cand, by_r in rows.items():
        table[cand] = {}
        for reading, xs in by_r.items():
            cell = {k: avg(xs, k) for k in ("goal_1", "goal_2", "goal_3", "goal_3b", "goal_4", "other", "moved")}
            table[cand][reading] = cell
    base_cells = table.get("baseline", {})
    for cand, by_r in table.items():
        for reading, cell in by_r.items():
            b = base_cells.get(reading)
            cell["pass"] = {"goal_1": cell["goal_1"] >= THRESHOLDS["goal_1"], "goal_4": cell["goal_4"] >= THRESHOLDS["goal_4"],
                            "goal_3": cell["goal_3"] >= THRESHOLDS["goal_3"],
                            "goal_3b": b is None or cell["goal_3b"] <= b["goal_3b"] + 0.25}
            if b:
                cell["vs_baseline"] = {k: round(cell[k] - b[k], 2) for k in ("goal_2", "goal_3", "goal_3b", "goal_4", "other")}
    def rank(cand):
        cells = list(table[cand].values())
        info = next((x for x in meta["candidates"] if x["code"] == cand), {"cost": 0, "not_modeled": []})
        return (not info["not_modeled"], min(sum(c["pass"].values()) for c in cells), min(c["goal_4"] for c in cells),
                -info["cost"])
    order = sorted(table, key=rank, reverse=True)
    best = next((c for c in order if c != "baseline"), None)
    summary = {"crisis_id": crisis_id, "title": meta["title"], "week": meta["week"], "readings": meta["readings"],
               "locked": meta["locked"], "candidates": meta["candidates"], "table": table, "order": order,
               "recommended": best, "rule": "only candidates whose actions the model simulates; then most board goals passed in the WORST reading, then higher worst-case revenue, then lower cost",
               "thresholds": THRESHOLDS}
    (base / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"recommended: {best}  (order: {order})")
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("crisis_id")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--seeds", default="1,2")
    ap.add_argument("--parallel", type=int, default=8)
    ap.add_argument("--crises-file", default="config/crises.json", help="for tests: a copy of crises.json")
    a = ap.parse_args()
    base = ROOT / "runs_dev" / "crisis" / a.crisis_id
    if a.report:
        return summarize(base, a.crisis_id)
    crises = json.loads((ROOT / a.crises_file).read_text())
    crisis = next(c for c in crises["crises"] if c["id"] == a.crisis_id)
    base.mkdir(parents=True, exist_ok=True)
    lock = locked()
    spent = round(sum(W.MENU[W.norm_action(x["action"])]["levels"][x["level"]] for d in lock for x in d["actions"]), 2)
    if len(lock) >= 2:
        print("both decisions are locked; nothing left to decide")
        return
    week = min(10, max(crisis["announced_week"] + 1, company_week_now() + 1))
    llm = LLM(seed=1, model=READER, temperature=0.4)
    readings = three_readings(llm, crisis)
    if not any(v["effects"] for v in readings.values()):   # reputation-only crisis: the three readings run identically
        readings = {"medium": readings["medium"]}
    cands = candidates(llm, crisis, week, W.BUDGET_M - spent)
    (base / "llm_calls.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in llm.calls))
    files = {}
    for r, v in readings.items():
        doc = copy.deepcopy(crises)
        next(c for c in doc["crises"] if c["id"] == a.crisis_id)["effects"] = v["effects"]
        f = base / f"crises_{r}.json"
        f.write_text(json.dumps(doc, indent=2, ensure_ascii=False))
        files[r] = f
    (base / "candidates").mkdir(exist_ok=True)
    decs = {"baseline": lock}
    for c in cands:
        decs[c["code"]] = lock + [c["decision"]]
    for code, d in decs.items():
        (base / "candidates" / f"{code}.json").write_text(json.dumps({"decisions": d}, indent=2, ensure_ascii=False))
    meta = {"title": crisis["title"], "week": week, "readings": readings, "locked": lock, "spent_musd": spent,
            "candidates": cands}
    (base / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"{len(readings)} readings x {len(decs)} options (baseline + {len(cands)} candidates) x seeds {a.seeds}")
    jobs = [(r, code, int(s)) for r in readings for code in decs for s in a.seeds.split(",")]
    with ThreadPoolExecutor(a.parallel) as ex:
        list(ex.map(lambda j: run_one(base, j[0], j[1], j[2], files[j[0]], base / "candidates" / f"{j[1]}.json"), jobs))
    summarize(base, a.crisis_id)


if __name__ == "__main__":
    main()
