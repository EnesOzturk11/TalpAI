#!/usr/bin/env python3
"""Export experiment runs (runs_dev/exp) into dashboard/data.json and build dashboard/kestrel-karar-odasi.html.

    python3 code/export_dashboard.py
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP = ROOT / "runs_dev" / "exp"
OUT = ROOT / "dashboard"

QUESTIONS = {
    "1a": ("Güven", "How much do you trust Kestrel Air?", False),
    "1b": ("Güven (b)", "I can count on Kestrel Air to treat me right.", False),
    "2a": ("Kalma", "How likely to keep using Kestrel Air (3 months)?", False),
    "2b": ("Ayrılmayı düşünme", "I am thinking about leaving Kestrel Air.", True),
    "3a": ("Tavsiye", "How likely to recommend Kestrel Air?", False),
    "3b": ("Arkadaşa ne derdin", "Stay away (1) ... go for it (5)", False),
    "4a": ("Adalet", "How fairly has Kestrel Air treated you?", False),
    "4b": ("Sömürülme hissi", "Kestrel Air takes advantage of people like me.", True),
}


def wilson(k, n, z=1.96):
    if n == 0:
        return [0, 0]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h)), round(100 * (c + h))]


def main():
    personas = {p["id"]: p for p in (json.loads(l) for l in open(ROOT / "data" / "personas.jsonl", encoding="utf-8"))}
    people = {pid: {"name": p["name"], "group": p["group"], "age": p["demographic"]["age"], "home": p["demographic"]["home"],
                    "stakes": p["stakes"], "exposure": p["strike_exposure"], "circle": p["circle"],
                    "w": p["represents_weekly_pax"]} for pid, p in personas.items()}
    runs = {}
    for d in sorted(EXP.iterdir()):
        if not (d / "metrics.json").exists():
            continue
        scen, pkg, seed = d.name.split("__")
        m = json.loads((d / "metrics.json").read_text())
        W = [json.loads(l) for l in open(d / "weekly.jsonl", encoding="utf-8")]
        wsum = sum(people[p]["w"] for p in people)
        weeks = []
        for w in range(1, 11):
            rows = [r for r in W if r["week"] == w]
            def share(pred):
                return round(100 * sum(people[r["persona"]]["w"] for r in rows if pred(r)) / wsum, 1)
            weeks.append({"week": w,
                          "rec": round(sum(people[r["persona"]]["w"] * r["recommend_0_to_10"] for r in rows) / wsum, 2),
                          "kept": share(lambda r: r["status"] in ("flies as planned", "rebooked")),
                          "other": share(lambda r: r["status"] == "moved to another airline"),
                          "complaint": share(lambda r: r["complaint"] != "none")})
        talk = [{"p": r["persona"], "w": r["week"], "t": r["what_you_said_or_posted"][:320], "where": r.get("said_where", ""), "pub": r["posted_publicly"],
                 "st": r["status"], "rec": r["recommend_0_to_10"], "feel": r["how_you_feel"][:200],
                 "fl": [("İPTAL" if o["canceled"] else f"{o['delay_hours']:.0f}s rötar" if o["delay_hours"] else "zamanında")
                        + f" {o['from']}→{o['to']}" for o in r["flights"]]}
                for r in W if r["what_you_said_or_posted"].strip()]
        moved = sorted({r["persona"] for r in W if "change to a different date" in r["actions"]})
        flights = []
        for r in W:
            for o in r["flights"]:
                trip = next((t for t in personas[r["persona"]]["trips"] if t["from"] == o["from"] and t["to"] == o["to"]), None)
                fare, party = (trip["fare_usd"], trip["party"]) if trip else (0, 1)
                kept = r["status"] in ("flies as planned", "rebooked")
                flights.append({"w": r["week"], "d": o["date"], "fr": o["from"], "to": o["to"], "p": r["persona"], "n": party,
                                "orig": trip["date"] if trip and trip["date"] != o["date"] else "",
                                "out": "cancel" if o["canceled"] else ("delay" if o["delay_hours"] else "ok"),
                                "dh": o["delay_hours"], "st": r["status"], "plan": fare * party, "rev": fare * party if kept else 0,
                                "r24": bool(o.get("rebook_within_24h"))})
        flights.sort(key=lambda f: (f["w"], f["d"], f["p"]))
        seq = {}
        for f in flights:
            seq[f["w"]] = seq.get(f["w"], 0) + 1
            f["code"] = f"W{f['w']}.{seq[f['w']]}"
        probe = {}
        if (d / "probe.jsonl").exists():
            rows = [json.loads(l) for l in open(d / "probe.jsonl", encoding="utf-8")]
            for q in QUESTIONS:
                s = [r["score"] for r in rows if r["question"] == q and r["when"] == "start"]
                e = [r["score"] for r in rows if r["question"] == q and r["when"] == "end"]
                if s and e:
                    probe[q] = [round(sum(s) / len(s), 2), round(sum(e) / len(e), 2)]
        runs.setdefault(scen, {}).setdefault(pkg, []).append({
            "seed": int(seed[1:]), "goals": {k: m[k] for k in ("goal_1", "goal_2", "goal_3", "goal_3b", "goal_4")},
            "g2n": m["detail"]["goal_2_sample"], "mix": m["detail"]["final_status_mix_pct"], "weeks": weeks,
            "moved": moved, "talk": talk, "probe": probe, "flights": flights, "cost": json.loads((d / "run.json").read_text()).get("cost_musd", 0)})
    packages = {"nodecision": {"label": "Karar yok", "blurb": "Business as usual: Kestrel olağan politikasıyla devam ediyor.",
                               "decisions": [], "cost": 0}}
    for f in sorted((ROOT / "config" / "experiments").glob("*.json")):
        if f.stem.startswith("crises"):
            continue
        j = json.loads(f.read_text())
        decs = [{k: v for k, v in d.items() if k != "target_rule"} for d in j["decisions"]]
        packages[f.stem] = {"label": j.get("_label", f.stem), "blurb": j.get("_blurb", ""), "decisions": decs}
    for scen in runs.values():
        for pkg, rs in scen.items():
            k = sum(r["g2n"]["ok"] for r in rs)
            n = sum(r["g2n"]["disrupted_legs"] for r in rs)
            for r in rs:
                r["g2pool"] = {"k": k, "n": n, "ci": wilson(k, n)}
    from datetime import datetime, timedelta, timezone
    crises = json.loads((ROOT / "config" / "crises.json").read_text())["crises"]
    crisis_dec = []
    for f in sorted((ROOT / "runs_dev" / "crisis").glob("*/summary.json")):
        crisis_dec.append(json.loads(f.read_text()))
    crisis_dec.sort(key=lambda s: -s["week"])
    data = {"people": people, "packages": packages, "runs": runs, "crisis_decisions": crisis_dec,
            "locked": json.loads((ROOT / "config" / "locked.json").read_text()).get("decisions", [])
                      if (ROOT / "config" / "locked.json").exists() else [],
            "questions": {k: {"label": v[0], "text": v[1], "reversed": v[2]} for k, v in QUESTIONS.items()},
            "updated": datetime.now(timezone(timedelta(hours=3))).strftime("%H:%M"),
            "crises": [{"id": c["id"], "kind": c["kind"], "week": c["announced_week"], "title": c["title"],
                        "text": c["text"], "reading": c["reading"], "updates": c.get("updates", []),
                        "effects": [f"{', '.join(e['dates'])} · {'tüm ağ' if e['bases'] == 'all' else '/'.join(e['bases'])}"
                                    f" · iptal %{round(100 * e['cancel_rate'])}, rötar {e['delay_hours']:g} sa"
                                    for e in c["effects"]]} for c in crises],
            "scenarios": {"base": "Temel: grev günlerinde üs uçuşlarının ~%25'i iptal",
                          "severe": "Ağır: ~%50 iptal, 5 saat rötar, grev 24 Aralık'a uzuyor"}}
    OUT.mkdir(exist_ok=True)
    (OUT / "data.json").write_text(json.dumps(data, ensure_ascii=False))
    tpl = (OUT / "template.html").read_text(encoding="utf-8")
    html = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (OUT / "kestrel-karar-odasi.html").write_text(html, encoding="utf-8")
    talk = sum(len(r["talk"]) for s in runs.values() for rs in s.values() for r in rs)
    print(f"runs: {sum(len(rs) for s in runs.values() for rs in s.values())}, messages: {talk}, "
          f"html: {len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
