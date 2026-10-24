#!/usr/bin/env python3
"""Build dashboard/sistem.html from runs_dev/v3 (84 personas, locked W7 A3, engine crisis + strike).

    python3 code/build_system_dashboard.py
"""
import glob
import json
import statistics as st
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs_dev" / "v3"
PLAN_M = 6 * 210_000 * 142.5 / 1e6
KEPT = {"flies as planned", "rebooked"}
OPTIONS = {
    "nodecision": ("Karar yok", "Hiçbir aksiyon yok; Kestrel olağan politikasıyla devam ediyor.", 0.0),
    "locked_only": ("Kilitli karar: W7 · A3", "Grev haftası yolcularına W7'de ücretsiz değişiklik/iptal. TALP'a kaydedildi.", 0.2),
    "D2_W8_A5_partner": ("+ W8 · A5 partner havayolu", "Kilitli karar + grev haftası için partner havayoluyla yeniden rezervasyon.", 0.45),
    "D2_W8_A2_backup": ("+ W8 · A2 yedek yer hizmetleri", "Kilitli karar + grev günleri için yedek yer hizmetleri ekibi.", 0.7),
    "D2_W8_A6_hotel": ("+ W8 · A6 otel", "Kilitli karar + mahsur kalanlara otel odası.", 0.4),
    "D2_W8_A7_staff": ("+ W8 · A7 ek personel", "Kilitli karar + 2 hafta ek havalimanı ve çağrı merkezi personeli.", 0.35),
    "D2_W9_A4_credit": ("+ W9 · A4 $75 kredi", "Kilitli karar + grevden etkilenenlere $75 seyahat kredisi.", 0.5),
}
QUESTIONS = {"1a": "Güven", "1b": "Güven (b)", "2a": "Kalma niyeti", "2b": "Ayrılmayı düşünme ⇅", "3a": "Tavsiye",
             "3b": "Arkadaşa ne derdin", "4a": "Adil davranılma", "4b": "Sömürülme hissi ⇅"}
GROUPS_TR = {"families visiting relatives": "Akraba ziyareti", "vacationers": "Tatilciler", "students": "Öğrenciler",
             "business travelers": "İş yolcuları", "travel agencies": "Acenteler"}
ENGINE_WORDS = ("engine", "inspection", "ground", "grounded", "parts", "tiktok", "faa", "mechanic")
STRIKE_WORDS = ("strike", "ground handling", "baggage", "picket")


def fare_of(people, pid, o):
    t = next((t for t in people[pid]["trips"] if t["from"] == o["from"] and t["to"] == o["to"]), None)
    return (t["fare_usd"], t["party"]) if t else (0, 1)


def one_run(d, people):
    m = json.loads((d / "metrics.json").read_text())
    W = [json.loads(l) for l in open(d / "weekly.jsonl", encoding="utf-8")]
    wt = {p: people[p]["represents_weekly_pax"] for p in people}
    tot = sum(wt.values())
    weeks = []
    for w in range(1, 11):
        rows = [r for r in W if r["week"] == w]
        plan = act = 0.0
        for r in rows:
            for o in r["flights"]:
                fare, _ = fare_of(people, r["persona"], o)
                v = wt[r["persona"]] * fare * o.get("iw", 1.0)
                plan += v
                act += v * (r["status"] in KEPT)
        fl = m["detail"]["fleet"].get(str(w), {})
        weeks.append({
            "rec": round(sum(wt[r["persona"]] * r["recommend_0_to_10"] for r in rows) / tot, 3),
            "other": round(100 * sum(wt[r["persona"]] for r in rows if r["status"] == "moved to another airline") / tot, 2),
            "complaint": round(100 * sum(wt[r["persona"]] for r in rows if r["complaint"] != "none") / tot, 2),
            "rev_pct": round(100 * act / plan, 1) if plan else None,
            "cancel_pct": round(100 * fl["canceled_ex_strike"] / fl["planned_ex_strike"], 2) if fl.get("planned_ex_strike") else None,
            "worst_day_pct": fl.get("canceled_pct")})
    seg = {}
    for g in GROUPS_TR:
        ids = [p for p in people if people[p]["group"] == g]
        plan = act = 0.0
        for r in W:
            if r["persona"] in ids and 5 <= r["week"] <= 10:
                for o in r["flights"]:
                    fare, _ = fare_of(people, r["persona"], o)
                    v = wt[r["persona"]] * fare * o.get("iw", 1.0)
                    plan += v
                    act += v * (r["status"] in KEPT)
        last = [r for r in W if r["persona"] in ids and r["week"] == 10]
        first = [r for r in W if r["persona"] in ids and r["week"] == 1]
        seg[g] = {"rev": round(100 * act / plan, 1) if plan else None,
                  "other": round(100 * sum(r["status"] == "moved to another airline" for r in last) / max(1, len(last)), 1),
                  "rec_delta": round(st.mean(r["recommend_0_to_10"] for r in last) - st.mean(r["recommend_0_to_10"] for r in first), 2),
                  "n": len(ids)}
    talk = [r for r in W if r["what_you_said_or_posted"]]
    probe = {}
    if (d / "probe.jsonl").exists():
        rows = [json.loads(l) for l in open(d / "probe.jsonl", encoding="utf-8")]
        for q in QUESTIONS:
            s = [r["score"] for r in rows if r["question"] == q and r["when"] == "start"]
            e = [r["score"] for r in rows if r["question"] == q and r["when"] == "end"]
            if s and e:
                probe[q] = [round(st.mean(s), 2), round(st.mean(e), 2)]
    quotes = []
    for r in talk:
        t = r["what_you_said_or_posted"].lower()
        topic = "engine" if any(x in t for x in ENGINE_WORDS) else "strike" if any(x in t for x in STRIKE_WORDS) else "other"
        quotes.append({"p": r["persona"], "w": r["week"], "where": r.get("said_where", ""), "t": r["what_you_said_or_posted"][:300],
                       "rec": r["recommend_0_to_10"], "topic": topic, "st": r["status"],
                       "fl": ["İPTAL" if o["canceled"] else f"{o['delay_hours']:.0f} sa rötar" if o["delay_hours"] else "zamanında" for o in r["flights"]]})
    return {"g1": m["goal_1"], "g2": m["goal_2"], "g3": m["goal_3"], "g3b": m["goal_3b"], "g4": m["goal_4"],
            "other": m["detail"]["final_status_mix_pct"]["moved to another airline"],
            "moved": len({r["persona"] for r in W if "change to a different date" in r["actions"]}),
            "angry": round(100 * sum(r["recommend_0_to_10"] <= 4 for r in talk) / max(1, len(talk)), 1),
            "happy": round(100 * sum(r["recommend_0_to_10"] >= 7 for r in talk) / max(1, len(talk)), 1),
            "weeks": weeks, "seg": seg, "probe": probe, "quotes": quotes}


def main():
    people = {p["id"]: p for p in (json.loads(l) for l in open(ROOT / "data" / "personas_84.jsonl", encoding="utf-8"))}
    data = {"options": {k: {"label": v[0], "blurb": v[1], "cost": v[2]} for k, v in OPTIONS.items()}, "runs": {},
            "groups": GROUPS_TR, "questions": QUESTIONS,
            "people": {k: {"name": v["name"], "group": GROUPS_TR[v["group"]], "home": v["demographic"]["home"]} for k, v in people.items()},
            "crises": json.loads((ROOT / "config" / "crises.json").read_text())["crises"],
            "locked": json.loads((ROOT / "config" / "locked.json").read_text())["decisions"]}
    for d in sorted(RUNS.iterdir()):
        if d.is_dir() and (d / "metrics.json").exists():
            scen, opt, seed = d.name.split("__")
            data["runs"].setdefault(scen, {}).setdefault(opt, []).append(one_run(d, people))
    data["plan_m"] = PLAN_M
    data["updated"] = datetime.now(timezone(timedelta(hours=3))).strftime("%H:%M")
    tpl = (ROOT / "dashboard" / "sistem_template.html").read_text(encoding="utf-8")
    out = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (ROOT / "dashboard" / "sistem.html").write_text(out, encoding="utf-8")
    n = sum(len(v) for s in data["runs"].values() for v in s.values())
    print(f"wrote dashboard/sistem.html: {n} runs, {len(out) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
