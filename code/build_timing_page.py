#!/usr/bin/env python3
"""Build dashboard/zamanlama.html: the same decision (A3+A5) taken now (W4/W5) vs in W7 vs not at all.

    python3 code/build_timing_page.py      (reads runs_dev/timing)
"""
import glob
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs_dev" / "timing"
PLAN_M = 6 * 210_000 * 142.5 / 1e6
OPTS = {
    "nodecision": ("Karar yok", "Kestrel olağan politikasıyla devam ediyor.", None),
    "W4_A3A5": ("W4 · A3+A5", "Bu hafta kilitleseydik: 23 Kasım haftasından itibaren grev uyarısı, ücretsiz değişiklik 23 Kas–6 Ara uçuşları için.", 4),
    "W5_A3A5": ("W5 · A3+A5", "Şimdi kilitlersek (W4 kilidi 14:30'da kaçtı): 30 Kasım haftası, ücretsiz değişiklik 30 Kas–13 Ara uçuşları için.", 5),
    "W7_A3A5": ("W7 · A3+A5", "Kilitlediğimiz karar: 14 Aralık haftası, ücretsiz değişiklik 14–27 Ara uçuşları için (grev günleri dahil).", 7),
}


def main():
    people = {p["id"]: p for p in (json.loads(l) for l in open(ROOT / "data" / "personas.jsonl", encoding="utf-8"))}
    wt = {k: v["represents_weekly_pax"] for k, v in people.items()}
    tot = sum(wt.values())
    data = {"opts": {}, "people": {k: {"name": v["name"], "group": v["group"]} for k, v in people.items()}}
    for k, (label, blurb, week) in OPTS.items():
        runs = []
        for d in sorted(glob.glob(str(RUNS / f"{k}__s*"))):
            m = json.loads(Path(d, "metrics.json").read_text())
            W = [json.loads(l) for l in open(Path(d, "weekly.jsonl"), encoding="utf-8")]
            talk = [r for r in W if r["what_you_said_or_posted"]]
            flights = []
            for r in W:
                if r["week"] != 8:
                    continue
                for o in r["flights"]:
                    trip = next((t for t in people[r["persona"]]["trips"] if t["from"] == o["from"] and t["to"] == o["to"]), None)
                    fare, party = (trip["fare_usd"], trip["party"]) if trip else (0, 1)
                    flights.append({"d": o["date"], "fr": o["from"], "to": o["to"], "p": r["persona"], "n": party,
                                    "orig": trip["date"] if trip and trip["date"] != o["date"] else "",
                                    "out": "cancel" if o["canceled"] else ("delay" if o["delay_hours"] else "ok"),
                                    "dh": o["delay_hours"], "st": r["status"], "plan": fare * party,
                                    "rev": fare * party if r["status"] in ("flies as planned", "rebooked") else 0})
            flights.sort(key=lambda f: (f["d"], f["p"]))
            for i, f in enumerate(flights, 1):
                f["code"] = f"W8.{i}"
            runs.append({
                "seed": int(d.rsplit("__s", 1)[1]), "g4": m["goal_4"], "g3": m["goal_3"], "cmp": m["goal_3b"],
                "other": m["detail"]["final_status_mix_pct"]["moved to another airline"],
                "rec": [round(sum(wt[r["persona"]] * r["recommend_0_to_10"] for r in W if r["week"] == w) / tot, 3) for w in range(1, 11)],
                "moved": sorted({r["persona"] for r in W if "change to a different date" in r["actions"]}),
                "angry": round(100 * sum(r["recommend_0_to_10"] <= 4 for r in talk) / max(1, len(talk)), 1),
                "quotes": [{"p": r["persona"], "w": r["week"], "where": r.get("said_where", ""), "t": r["what_you_said_or_posted"][:300],
                            "rec": r["recommend_0_to_10"]} for r in talk if r["messages_seen"] and (week is None or r["week"] >= week)][:40],
                "flights": flights})
        data["opts"][k] = {"label": label, "blurb": blurb, "week": week, "runs": runs}
    nd = sum(r["g4"] for r in data["opts"]["nodecision"]["runs"]) / len(data["opts"]["nodecision"]["runs"])
    for k, o in data["opts"].items():
        g4 = sum(r["g4"] for r in o["runs"]) / len(o["runs"])
        o["net"] = round((g4 - nd) / 100 * PLAN_M - (0 if k == "nodecision" else 0.45), 1)
    data["updated"] = datetime.now(timezone(timedelta(hours=3))).strftime("%H:%M")
    tpl = (ROOT / "dashboard" / "zamanlama_template.html").read_text(encoding="utf-8")
    out = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (ROOT / "dashboard" / "zamanlama.html").write_text(out, encoding="utf-8")
    print(f"wrote dashboard/zamanlama.html ({len(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
