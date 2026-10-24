#!/usr/bin/env python3
"""Dashboard announcements -> config/crises.json, read by the LLM.

    .venv/bin/python -I code/announcements.py ingest [--file path]   # process new announcements once
    .venv/bin/python -I code/announcements.py watch                  # wait for a new crisis, ingest, rerun experiments, rebuild dashboard, exit

Sources: the newest of ~/Downloads/*announcements*.json and ./team-01_announcements.json
(the dashboard's "Download released updates JSON"). Every reading call is logged to
config/crisis_readings.jsonl for TEAM_DOC. Our reading is a proposal: edit config/crises.json to override it.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Literal

from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm import LLM  # noqa: E402
import world as W  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CRISES = ROOT / "config" / "crises.json"
SEEN = ROOT / "config" / "announcements_seen.json"
LOG = ROOT / "config" / "crisis_readings.jsonl"
IST = timezone(timedelta(hours=3))
WEEK1_START = datetime(2026, 10, 24, 13, 0, tzinfo=IST)   # real clock: every 30 minutes is one company week
MENU_NAMES = sorted(W.MENU)
SEVERE_SET = "nodecision,W7_kalkan,W7_yalin,W7_yalniz_yedek"


class Effect(BaseModel):
    dates: List[str]
    airports: List[str]
    cancel_rate: float
    delay_hours: float
    bags: bool
    assistance: bool
    cause: str
    mitigating_actions: List[Literal[tuple(MENU_NAMES)]]


class Reading(BaseModel):
    is_crisis: bool
    update_of: str
    id: str
    title: str
    reading: str
    effects: List[Effect]


def effect_to_world(e):
    return {"dates": e["dates"], "bases": "all" if "ALL" in e["airports"] else e["airports"],
            "cancel_rate": max(0.0, min(1.0, e["cancel_rate"])), "delay_hours": max(0.0, min(24.0, e["delay_hours"])),
            "bags": e["bags"], "assistance": e["assistance"], "cause": e["cause"],
            "mitigated_by": {m: (0.3 if m.startswith("backup ground") else 0.6) for m in e["mitigating_actions"]}}


def sync_locked():
    """Copy the dashboard's decisions download (~/Downloads/*decisions*.json, field run_decisions) to config/locked.json."""
    files = sorted(glob.glob(os.path.expanduser("~/Downloads/*decisions*.json")), key=os.path.getmtime, reverse=True)
    if not files:
        return False
    try:
        raw = json.load(open(files[0], encoding="utf-8"))
    except Exception as e:
        print(f"skip {files[0]}: {e}")
        return False
    decs = raw.get("run_decisions", raw.get("decisions", [])) if isinstance(raw, dict) else raw
    known = {}
    for f in (ROOT / "config" / "experiments").glob("*.json"):
        for d in json.loads(f.read_text()).get("decisions", []):
            known[d["message"].strip()] = d.get("target_rule")
    out = []
    for d in decs:
        d = dict(d)
        rule = known.get(str(d.get("message", "")).strip())
        tgt = str(d.get("target", "")).lower()
        d["target_rule"] = rule or ("all" if tgt in ("everyone", "all", "") or "everyone" in tgt else "upcoming_travelers")
        out.append(d)
    path = ROOT / "config" / "locked.json"
    old = json.loads(path.read_text()) if path.exists() else {"decisions": []}
    if old.get("decisions") != out:
        path.write_text(json.dumps({"source": files[0], "decisions": out}, indent=2, ensure_ascii=False))
        print(f"locked decisions updated from {files[0]}: {len(out)} decision(s)", flush=True)
        return True
    return False


def sources():
    files = glob.glob(os.path.expanduser("~/Downloads/*announcements*.json")) + [str(ROOT / "team-01_announcements.json")]
    return sorted((f for f in files if os.path.exists(f)), key=os.path.getmtime, reverse=True)


def load_announcements():
    out = {}
    for f in sources():
        try:
            for a in json.load(open(f, encoding="utf-8")).get("announcements", []):
                out.setdefault(a["id"], a)
        except Exception as e:
            print(f"skip {f}: {e}")
    return out


def company_week(published_at):
    t = datetime.fromisoformat(published_at.replace("Z", "+00:00")).astimezone(IST)
    return max(1, min(10, int((t - WEEK1_START).total_seconds() // 1800) + 1)) if t >= WEEK1_START else 1


def prompt_for(a, week, crises):
    s = W.week_start(week)
    known = "\n".join(f"- id={c['id']} (week {c['announced_week']}): {c['title']}. {c['text'][:300]}" for c in crises)
    return f"""You read crisis announcements for a simulation of Kestrel Air, a fictional US low-cost airline.
Facts: bases Orlando (MCO) and Philadelphia (PHL); 6 in 10 flights touch a base; 36 aircraft of one family;
210,000 passengers a week, 86% full (week 8, Dec 21-27, is 97% booked); 75% US, 25% Mexico and Caribbean.
Company calendar: week 1 = Nov 2-8, 2026 ... week 10 = Jan 4-10, 2027. This announcement was published at the
start of week {week} ({s:%b %d, %Y} to {(s + timedelta(days=6)):%b %d, %Y}); it is already happening in that week.
Crises already known:
{known}

ANNOUNCEMENT
Title: {a.get('title', '')}
Body: {a.get('body', '')}

Decide:
1. is_crisis: false for anything that is not about Kestrel Air's business or its customers (prizes, logistics, tests).
2. update_of: the id of a known crisis if this updates it, else "".
3. id: a short snake_case id; title: a short title.
4. reading: 2-4 sentences on how you read it: what is known, what is not, how big it plausibly is. Crises are serious
   but survivable; none sinks the company alone. Be calibrated, not dramatic.
5. effects: ONLY flight-operation effects the world model can apply (cancellations, delays, slow bags, slow
   wheelchair/escort help), each with the exact dates (YYYY-MM-DD, inside the ten weeks), airports (IATA codes, or
   ["ALL"] for the whole network), cancel_rate (0-1, share of those flights canceled), delay_hours, bags, assistance,
   a short cause, and which decision-menu actions would soften it (from: {', '.join(MENU_NAMES)}).
   A crisis that only changes what people hear (reputation, prices, a data issue, a rival's move) has effects [] —
   the announcement text itself reaches personas through the news. For an update, give the full new effects list
   for that crisis, or [] to keep the old one."""


def ingest(only_file=None):
    seen = set(json.loads(SEEN.read_text())) if SEEN.exists() else set()
    anns = load_announcements() if not only_file else {a["id"]: a for a in json.load(open(only_file))["announcements"]}
    new = [a for i, a in sorted(anns.items(), key=lambda x: x[1].get("published_at", "")) if i not in seen]
    if not new:
        return []
    doc = json.loads(CRISES.read_text())
    shutil.copy(CRISES, CRISES.with_suffix(".json.bak"))
    llm = LLM(seed=1, model=os.environ.get("TALP_READER_MODEL", "gemini-3.5-flash"), temperature=0.4)
    changed = []
    for a in new:
        week = company_week(a.get("published_at") or a.get("publish_at"))
        _, r = llm.json(prompt_for(a, week, doc["crises"]), Reading, week=week)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"announcement": a, "week": week, "reading": r, "call": llm.calls[-1]}, ensure_ascii=False) + "\n")
        seen.add(a["id"])
        if not r["is_crisis"]:
            print(f"not a crisis: {a.get('title')}")
            continue
        effects = [effect_to_world(e) for e in r["effects"]]
        text = f"{a.get('title', '').strip()}: {a.get('body', '').strip()}"
        target = next((c for c in doc["crises"] if c["id"] == r["update_of"]), None)
        if target:
            target.setdefault("updates", []).append({"week": week, "text": text, "reading": r["reading"]})
            if effects:
                target["effects"] = effects
            changed.append((f"update to {target['id']} (week {week})", target["id"]))
        else:
            cid = r["id"] if r["id"] not in {c["id"] for c in doc["crises"]} else f"{r['id']}_{week}"
            doc["crises"].append({"id": cid, "kind": "surprise", "announced_week": week, "title": r["title"],
                                  "text": text, "updates": [], "reading": r["reading"], "effects": effects,
                                  "source_announcement": a["id"]})
            changed.append((f"new crisis {cid} (week {week}, {len(effects)} effects)", cid))
    CRISES.write_text(json.dumps(doc, indent=2, ensure_ascii=False))
    SEEN.write_text(json.dumps(sorted(seen)))
    for c, _ in changed:
        print("  " + c)
    return changed


def rebuild():
    py = str(ROOT / ".venv" / "bin" / "python")
    env = dict(os.environ, SSL_CERT_FILE=os.environ.get("SSL_CERT_FILE", "/etc/ssl/cert.pem"))
    shutil.rmtree(ROOT / "runs_dev" / "exp", ignore_errors=True)
    for args in (["run", "--seeds", "1,2", "--scenario", "base"],
                 ["run", "--seeds", "1,2", "--scenario", "severe", "--only", SEVERE_SET]):
        subprocess.run([py, "-I", "code/experiments.py", *args], cwd=ROOT, env=env, check=True)
    subprocess.run([py, "-I", "code/export_dashboard.py"], cwd=ROOT, env=env, check=True)


def decide(crisis_ids):
    py = str(ROOT / ".venv" / "bin" / "python")
    env = dict(os.environ, SSL_CERT_FILE=os.environ.get("SSL_CERT_FILE", "/etc/ssl/cert.pem"))
    for cid in dict.fromkeys(crisis_ids):
        print(f"deciding how to answer {cid}...", flush=True)
        subprocess.run([py, "-I", "code/crisis_decide.py", cid], cwd=ROOT, env=env, check=False)
    subprocess.run([py, "-I", "code/export_dashboard.py"], cwd=ROOT, env=env, check=True)


def watch(interval):
    print(f"watching {', '.join(sources()) or '~/Downloads/*announcements*.json'} and ~/Downloads/*decisions*.json every {interval}s", flush=True)
    while True:
        sync_locked()
        changed = ingest()
        if changed:
            decide([cid for _, cid in changed])
            print("READY: dashboard/kestrel-karar-odasi.html rebuilt; " + "; ".join(c for c, _ in changed), flush=True)
            return
        time.sleep(interval)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["ingest", "watch", "rebuild", "sync-locked"])
    ap.add_argument("--file")
    ap.add_argument("--interval", type=int, default=20)
    a = ap.parse_args()
    if a.cmd == "ingest":
        print(ingest(a.file) or "no new announcements")
    elif a.cmd == "rebuild":
        rebuild()
    elif a.cmd == "sync-locked":
        print("updated" if sync_locked() else "no change")
    else:
        watch(a.interval)


if __name__ == "__main__":
    main()
