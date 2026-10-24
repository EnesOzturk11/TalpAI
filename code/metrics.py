"""Turn persona behavior into the board's goals.

Personas are a stratified sample (strike-day travelers are oversampled), so behavior is measured as rates
inside strata and scaled with each persona's 'represents_weekly_pax' weight and party size.
"""
import math

KEPT = {"flies as planned", "rebooked"}
BASELINE_COMPLAINTS_PER_MONTH = 2500   # dossier
BASELINE_NPS = 12                      # dossier
WEEKS_PER_MONTH = 4.35


def wilson(k, n, z=1.96):
    if n == 0:
        return [0.0, 0.0]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]


def compute(all_personas, personas, weekly, world, probe):
    by = {(r["persona"], r["week"]): r for r in weekly}
    pw = {p["id"]: p["represents_weekly_pax"] for p in personas}
    weeks = sorted({r["week"] for r in weekly})

    # goal 1: fleet-level, strike days left out
    planned = sum(s["planned_ex_strike"] for s in world.weekly_stats.values())
    canceled = sum(s["canceled_ex_strike"] for s in world.weekly_stats.values())
    g1 = 100 * (1 - canceled / planned) if planned else 0

    # goal 2: passengers whose flight was canceled, rebooked by Kestrel within 24h or refunded.
    # Read from weekly.jsonl so it can be recomputed from the saved run; legs are importance-weighted.
    aff = ok = 0.0
    n_aff = n_ok = 0
    for r in weekly:
        for o in r["flights"]:
            if not o["canceled"] or r["persona"] not in pw:
                continue
            good = r["status"] == "canceled the trip" or (r["status"] == "rebooked" and o.get("rebook_within_24h"))
            aff += pw[r["persona"]] * o["iw"]
            ok += pw[r["persona"]] * o["iw"] * good
            n_aff += 1
            n_ok += good
    g2 = 100 * ok / aff if aff else 100.0

    # goal 3: NPS. LLM personas compress 0-10 answers, so the raw level is not comparable with the dossier;
    # we anchor week 1 at the dossier's +12 and report the simulated change from there.
    def nps_at(week):
        rows = [by[(pid, week)] for pid in pw if (pid, week) in by]
        s = sum(pw[r["persona"]] for r in rows) or 1
        return 100 * (sum(pw[r["persona"]] for r in rows if r["recommend_0_to_10"] >= 9) -
                      sum(pw[r["persona"]] for r in rows if r["recommend_0_to_10"] <= 6)) / s
    last = [by[(pid, max(weeks))] for pid in pw if (pid, max(weeks)) in by]
    wsum = sum(pw[r["persona"]] for r in last) or 1
    nps_raw_start, nps_raw_end = nps_at(min(weeks)), nps_at(max(weeks))
    nps = BASELINE_NPS + (nps_raw_end - nps_raw_start)
    complaint_rows = [r for r in weekly if r["complaint"] != "none"]
    # complaint index: weighted share of persona-weeks with a complaint; read against the nodecision run
    complaint_pct = 100 * sum(pw[r["persona"]] for r in complaint_rows) / (sum(pw.values()) * len(weeks)) if weeks else 0
    dot = sum(pw[r["persona"]] for r in complaint_rows if r["complaint"] == "to the DOT")

    # goal 4: revenue weeks 5-10 as % of plan (flown legs on Kestrel x fare x party, weighted)
    plan_rev = act_rev = 0.0
    for p in personas:
        for k, t in enumerate(p["trips"]):
            if t["week"] and 5 <= t["week"] <= 10 and t.get("booked", True):
                o = world.leg_outcome.get((p["id"], k)) or {"iw": 1.0}
                v = pw[p["id"]] * t["fare_usd"] * o["iw"]
                plan_rev += v
                r = by.get((p["id"], t["week"]))
                act_rev += v * (r is not None and r["status"] in KEPT)
    price_actions = sum(0.5 for d in world.decisions for a in d["actions"] if a["action"].lower().startswith("fare cap"))
    g4 = 100 * act_rev / plan_rev if plan_rev else 100.0

    final = [by[(pid, max(weeks))] for pid in pw if (pid, max(weeks)) in by]
    status_mix = {s: round(100 * sum(pw[r["persona"]] for r in final if r["status"] == s) / wsum, 1)
                  for s in ("flies as planned", "rebooked", "moved to another airline", "canceled the trip")}
    book_again = {s: round(100 * sum(pw[r["persona"]] for r in final if r["book_again"] == s) / wsum, 1)
                  for s in ("yes", "maybe", "no")}
    say_do = None
    if probe:
        start2a = {r["persona"]: r["score"] for r in probe if r["when"] == "start" and r["question"] == "2a"}
        said_stay = [pid for pid, s in start2a.items() if s >= 4]
        left = [pid for pid in said_stay if any(by.get((pid, w), {}).get("status") in
                                                ("moved to another airline", "canceled the trip") for w in weeks)]
        say_do = {"said_likely_to_stay": len(said_stay), "then_left_or_canceled": len(left), "personas": left}

    return {
        "goal_1": round(g1, 2),
        "goal_2": round(g2, 1),
        "goal_3": round(nps, 1),
        "goal_3b": round(complaint_pct, 2),
        "goal_4": round(g4, 1),
        "units": {
            "goal_1": "% of planned flights operated over weeks 1-10, strike days Dec 22-23 left out (fleet model)",
            "goal_2": "% of passengers on canceled flights rebooked by Kestrel within 24h or refunded (persona-weighted, importance-weighted)",
            "goal_3": "net promoter score at week 10: dossier's +12 plus the simulated change from week 1 (weighted 0-10 answers)",
            "goal_3b": "complaint index: weighted % of persona-weeks with a complaint to Kestrel or DOT (compare with nodecision; last winter ~2,500/month)",
            "goal_4": "% of planned weeks 5-10 ticket revenue still flown on Kestrel (sample legs x fare x persona weight, importance-weighted)",
        },
        "detail": {
            "nps_raw_week1_week10": [round(nps_raw_start, 1), round(nps_raw_end, 1)],
            "goal_2_sample": {"disrupted_legs": n_aff, "ok": n_ok, "ci95_unweighted": wilson(n_ok, n_aff)},
            "dot_share_of_complaints_pct": round(100 * dot / max(1, sum(pw[r["persona"]] for r in complaint_rows)), 1),
            "final_status_mix_pct": status_mix,
            "final_book_again_pct": book_again,
            "say_do_gap": say_do,
            "fare_cap_lost_revenue_musd": price_actions,
            "n_personas": len(personas), "weeks": len(weeks),
            "fleet": {str(w): {k: round(v, 1) for k, v in s.items()} for w, s in sorted(world.weekly_stats.items())},
        },
    }
