#!/usr/bin/env python3
"""Convert the team's catalog-style personas (data/personas_v2_source.jsonl, sections A-I + sector)
into the simulator's schema (data/personas_v2.jsonl). The source file is never modified.

    python3 code/personas_v2.py
"""
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAL_START = date(2026, 11, 2)
STRIKE_DAYS = {date(2026, 12, 22), date(2026, 12, 23)}
BASES = {"MCO", "PHL"}
MEXICO_CARIBBEAN = {"CUN", "PUJ", "SDQ", "MBJ", "GDL", "SJU"}
WEEKLY_PAX = 210_000


def scale(x, labels=("very low", "low", "medium", "high", "very high")):
    return labels[max(1, min(5, int(x))) - 1] if isinstance(x, (int, float)) else str(x)


def leg(t, fare):
    codes = re.findall(r"\b[A-Z]{3}\b", t["leg"])
    frm, to = (codes + ["???", "???"])[:2]
    d = date.fromisoformat(t["date"])
    w = (d - CAL_START).days // 7 + 1
    touches = bool({frm, to} & BASES)
    return {"date": t["date"], "week": w if 1 <= w <= 10 else None, "from": frm, "to": to, "party": t["party"],
            "fare_usd": fare, "market": "mexico_caribbean" if {frm, to} & MEXICO_CARIBBEAN else "us",
            "touches_base": touches, "strike_day_at_base": touches and d in STRIKE_DAYS,
            "booked": t.get("booked", True), "note": t["leg"] if t["leg"] != f"{frm}→{to}" else ""}


def convert(s):
    A, B, C, D, E, F, G = (s[k] for k in "ABCDEFG")
    sec = s["sector"]
    trips_raw = sec["trips"]
    seats = sum(t["party"] for t in trips_raw if t.get("booked", True)) or 1
    fare = round(sec["paid_usd"] / seats) if sec.get("paid_usd") else 120
    trips = [leg(t, fare) for t in trips_raw]
    kids = f", children aged {', '.join(map(str, A['children']))}" if A["children"] else ""
    trust = s["state0"]["trust"]
    sentiment = "promoter" if trust >= 4 else "detractor" if trust <= 2 else "passive"
    stakes = sec.get("other_nonrefundable") or s["narrative"]
    return {
        "id": s["id"], "group": s["group"], "name": re.sub(r"'s$", "", s["narrative"].split()[0]),
        "demographic": {"age": A["age"], "gender": A["gender"], "home": f"{A['city']}, {A['state']}", "area": A["area"],
                        "household": f"{A['marital']}, household of {A['household_size']}{kids}",
                        "occupation": A["occupation"], "employment": A["employment"], "income": A["income"],
                        "housing": A["home"], "owns_car": A["car"], "education": A["education"]},
        "kestrel": {"customer_since": 2026 - B["customer_years"], "sentiment": sentiment,
                    "why": B.get("bad_experience") or "no strong story either way"},
        "life_story": {k: v for k, v in B.items() if v not in (None, False, "")},
        "values": {"values_most": ", ".join(C["values"]), "attitude_to_risk": C["risk"],
                   "trust_in_institutions": scale(C["trust_institutions"]), "trusts": C["trusts"],
                   "price_consciousness": scale(C["price_conscious"]), "brand_loyalty": scale(C["loyalty"]),
                   "sense_of_fairness": scale(C["fairness"]), "need_for_control": scale(C["need_control"])},
        "behavior": {"preferred_channel": D["channel"], "complaint_history": D["complaint_history"],
                     "writes_reviews": D["writes_reviews"], "social_media": D["social_media"],
                     "also_uses": ", ".join(D["rivals"]) or "no other airline", "payment": D["payment"],
                     "plans_ahead": D["planning"], "likely_actions": s["H"]["likely"],
                     "unlikely_actions": s["H"]["unlikely"]},
        "emotions": {"baseline_anxiety": scale(E["anxiety"]), "how_fast_angry": scale(E["anger_speed"]),
                     "patience_when_waiting": scale(E["patience"]), "tendency_to_forgive": scale(E["forgiveness"]),
                     "embarrassed_to_complain": E["embarrassed_to_complain"],
                     "tolerance_for_uncertainty": scale(E["uncertainty_tolerance"]), "mood": E["mood"]},
        "social_info": {"hears_news_from": F["news"], "circle_size": F["circle"], "opinion_role": F["opinion_role"],
                        "swayed_by_others": scale(F["swayable"]), "rumors": F["rumors"],
                        "asks_before_deciding": F["asks_before_deciding"]},
        "money": {"savings": G["savings"], "debt": G["credit_card_debt"], "paycheck_to_paycheck": G["paycheck_to_paycheck"],
                  "worried_about_prices": scale(G["price_worry"]), "who_pays": G["who_pays"],
                  "money_buffer_usd": s["state0"]["money_buffer_usd"]},
        "sector": {"how_often_they_fly": f"{D['trips_per_year']} trips a year",
                   "spend_style": sec["spend_style"], "needs_help_at_airport": sec.get("assist") or "no",
                   "books_via": D["channel"], "checks_a_bag": "yes" if "bag" in sec["spend_style"] else "no",
                   "paid_usd": sec["paid_usd"], **({k: v for k, v in s["I"].items()})},
        "trips": trips,
        "stakes": stakes,
        "if_disrupted": f"other airlines they use: {', '.join(D['rivals']) or 'none'}; money buffer about ${s['state0']['money_buffer_usd']}",
        "narrative": s["narrative"],
        "voice": f"{D['social_media']}; mood: {E['mood']}",
        "circle": [],
        "represents_weekly_pax": round(s["weight_pct"] / 100 * WEEKLY_PAX),
        "source_weight_pct": s["weight_pct"],
    }


def main():
    src = [json.loads(l) for l in open(ROOT / "data" / "personas_v2_source.jsonl", encoding="utf-8")]
    out = [convert(s) for s in src]
    for p in out:
        exp = [t for t in p["trips"] if t["strike_day_at_base"]]
        p["strike_exposure"] = ("on a strike day at a base" if exp else
                                "week 8, not on a strike day" if any(t["week"] == 8 for t in p["trips"]) else
                                "not traveling in week 8")
    with open(ROOT / "data" / "personas_v2.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps(p, ensure_ascii=False) + "\n" for p in out)
    legs = [t for p in out for t in p["trips"]]
    print(f"{len(out)} personas, groups {dict(Counter(p['group'] for p in out))}")
    print(f"legs: {len(legs)} | touch MCO/PHL: {sum(t['touches_base'] for t in legs)} | "
          f"on strike days at a base: {sum(t['strike_day_at_base'] for t in legs)} | not booked: {sum(not t['booked'] for t in legs)}")
    print("exposure:", dict(Counter(p["strike_exposure"] for p in out)))
    print("week-8 base legs:", [(p["id"], t["date"], t["from"], t["to"]) for p in out for t in p["trips"]
                                if t["week"] == 8 and t["touches_base"]])


if __name__ == "__main__":
    main()
