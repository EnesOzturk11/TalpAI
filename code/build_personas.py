"""Build the frozen Kestrel Air persona set (generated once, copied into every run).

    python code/build_personas.py --dry-run            # skeletons + template narrative, no LLM
    export TALP_KEY=...; python code/build_personas.py # + narratives written by Gemini

Writes personas/personas.jsonl, personas/PERSONAS.md, personas/gen_calls.jsonl and
prints a diversity report. Structured fields are sampled in code from pools.py (seeded),
so diversity is by construction; the LLM only turns each skeleton into a backstory.
"""
import argparse
import json
import os
import random
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import pools as P

N = 300
SEED = 2026
GEN_MODEL = "gemini-3.5-flash"
OUT = Path(__file__).resolve().parent.parent / "personas"

STRIKE_DAYS = {date(2026, 12, 22), date(2026, 12, 23)}
ADJACENT_DAYS = [date(2026, 12, d) for d in (20, 21, 24, 25, 26)]
STRATA = {"strike": 0.35, "adjacent": 0.20, "other": 0.45}  # our oversampling choice (Q9)

# Passengers each stratum stands for over the 10 weeks, from dossier numbers only.
WEEKLY_PAX, BASE_SHARE = 210_000, 0.6
STRATUM_PAX = {"strike": WEEKLY_PAX * BASE_SHARE * 2 / 7, "adjacent": WEEKLY_PAX * BASE_SHARE * 5 / 7}
STRATUM_PAX["other"] = WEEKLY_PAX * 10 - sum(STRATUM_PAX.values())
# ponytail: week 8 treated as a normal 210k week and one persona = one passenger (party and
# repeat trips not double-counted); refine if the board asks for revenue per booking.

FIRST = ["Maria", "James", "Aaliyah", "Kevin", "Priya", "Tom", "Danielle", "Luis", "Grace", "Marcus", "Hannah", "DeShawn",
         "Sofia", "Brian", "Keisha", "Ethan", "Yesenia", "Patrick", "Mei", "Andre", "Brittany", "Omar", "Colleen", "Jamal",
         "Rosa", "Tyler", "Nicole", "Victor", "Ashley", "Raymond", "Jasmine", "Connor", "Lourdes", "Derek", "Tiffany", "Hector",
         "Megan", "Samuel", "Imani", "Frank", "Carmen", "Dylan", "Wendy", "Anthony", "Lauren", "Reggie", "Ana", "Joe", "Kayla",
         "Darnell", "Linh", "Greg", "Tasha", "Mateo", "Diane", "Chris", "Amber", "Ravi", "Shannon", "Eddie", "Fatima", "Bill",
         "Jordan", "Alex", "Taylor", "Sam", "Riley", "Casey"]
LAST = ["Rivera", "O'Brien", "Washington", "Nguyen", "Patel", "Kowalski", "Johnson", "Martinez", "Russo", "Brooks", "Kim",
        "Thompson", "Delgado", "Murphy", "Jackson", "Chen", "Sullivan", "Ortiz", "Williams", "Morales", "Fitzgerald", "Harris",
        "Ramos", "DiNardo", "Coleman", "Santiago", "Walsh", "Robinson", "Reyes", "Novak", "Greene", "Castillo", "Byrne",
        "Mitchell", "Lopez", "Schmidt", "Carter", "Gomez", "Brennan", "Ward", "Torres", "Lee", "Henderson", "Vargas", "Price",
        "Flores", "Kelly", "Hughes", "Medina", "Foster", "Cruz", "Simmons", "Diaz", "Russell", "Pham", "Bailey", "Herrera",
        "McCarthy", "Bryant", "Mendoza", "Stewart", "Alvarez", "Graham", "Romero", "Wallace", "Jimenez", "Hayes", "Ruiz"]


class Picker:
    """Least-used-first sampling: every pool item is used before any is used twice."""

    def __init__(self, rng):
        self.rng, self.used = rng, Counter()

    def one(self, pool):
        low = min(self.used[x] for x in pool)
        x = self.rng.choice([c for c in pool if self.used[c] == low])
        self.used[x] += 1
        return x

    def many(self, pool, k):
        out = []
        for _ in range(k):
            out.append(self.one([x for x in pool if x not in out]))
        return out


def w(rng, options):
    """Weighted choice from {value: weight}."""
    return rng.choices(list(options), weights=list(options.values()))[0]


def allocate(total, shares):
    """Integer counts proportional to shares that sum to total (largest remainder)."""
    raw = {k: total * v / sum(shares.values()) for k, v in shares.items()}
    counts = {k: int(r) for k, r in raw.items()}
    for k in sorted(raw, key=lambda k: raw[k] - counts[k], reverse=True)[: total - sum(counts.values())]:
        counts[k] += 1
    return counts


def days(a, b):
    return [a + timedelta(d) for d in range((b - a).days + 1)]


def leg(rng, d, frm, to):
    return {"date": d.isoformat(), "weekday": d.strftime("%a"), "from": frm, "to": to,
            "flight": f"KS{rng.randint(100, 999)}",
            "departs": rng.choice(["6:05am", "7:40am", "9:15am", "11:30am", "1:50pm", "4:20pm", "6:45pm", "9:10pm"]),
            "touches_base": frm in P.BASES or to in P.BASES}


def trip_dates(rng, stratum, group):
    """(outbound, return) dates for the stratum. Only the strike stratum flies Dec 22-23."""
    after = days(date(2026, 12, 27), date(2027, 1, 4))
    if stratum == "strike":
        sd = rng.choice(sorted(STRIKE_DAYS))
        if rng.random() < 0.7:
            return sd, rng.choice(after), "outbound"
        return rng.choice(days(date(2026, 12, 12), date(2026, 12, 19))), sd, "return"
    if stratum == "adjacent":
        ad = rng.choice(ADJACENT_DAYS)
        if ad.day <= 21:
            return ad, rng.choice(after), "outbound"
        return rng.choice(days(date(2026, 12, 12), date(2026, 12, 19))), ad, "return"
    if group == "students":
        return rng.choice(days(date(2026, 12, 12), date(2026, 12, 19))), rng.choice(days(date(2027, 1, 5), date(2027, 1, 10))), None
    window = rng.choice(["thanksgiving", "new year", "november", "early december", "january"])
    if window == "thanksgiving":
        return rng.choice(days(date(2026, 11, 23), date(2026, 11, 25))), rng.choice(days(date(2026, 11, 28), date(2026, 11, 30))), None
    if window == "new year":
        return rng.choice(days(date(2026, 12, 27), date(2026, 12, 30))), rng.choice(days(date(2027, 1, 1), date(2027, 1, 4))), None
    start = {"november": (date(2026, 11, 4), date(2026, 11, 18)), "early december": (date(2026, 12, 2), date(2026, 12, 12)),
             "january": (date(2027, 1, 4), date(2027, 1, 6))}[window]
    out = rng.choice(days(*start))
    back = out + timedelta(rng.randint(2, 6) if group != "business travelers" else rng.randint(1, 3))
    return out, min(back, date(2027, 1, 10)), None


def destination(rng, pick, group, home_ap, need_base):
    """(airport, why) for the trip; need_base forces MCO or PHL on one end."""
    def ok(ap):
        return ap != home_ap and (not need_base or home_ap in P.BASES or ap in P.BASES)
    if group == "families visiting relatives":
        who, ap = pick.one([r for r in P.RELATIVES if ok(r[1])])
        return ap, f"visiting {who}"
    if group == "business travelers":
        why, ap = pick.one([b for b in P.BUSINESS_PURPOSES if ok(b[1])])
        return ap, why
    if group == "travel agencies":
        why, ap = pick.one([g for g in P.AGENCY_GROUPS if ok(g[1])])
        return ap, f"booked {why}"
    ap = pick.one([d for d in P.LEISURE_DESTS if ok(d)])
    reason = "a theme-park week" if ap == "MCO" else f"a warm-weather getaway to {P.AIRPORTS[ap]}"
    return ap, reason


def make_trips(rng, pick, p, stratum):
    g, home_ap = p["group"], p["home"]["airport"]
    out_d, ret_d, strike_leg = trip_dates(rng, stratum, g)
    if g == "students":  # college -> home for winter break, then back
        col_ap = p["student"]["college_airport"]
        legs, why = [leg(rng, out_d, col_ap, home_ap), leg(rng, ret_d, home_ap, col_ap)], "winter break at home"
        if strike_leg == "return":  # flying back to campus on Dec 22-23 makes no sense; flip it
            legs = [leg(rng, ret_d, col_ap, home_ap), leg(rng, ret_d + timedelta(14), home_ap, col_ap)]
        dest = home_ap
    else:
        dest, why = destination(rng, pick, g, home_ap, need_base=stratum != "other")
        legs = [leg(rng, out_d, home_ap, dest), leg(rng, ret_d, dest, home_ap)]
    intl = dest in P.INTERNATIONAL or (g == "students" and home_ap in P.INTERNATIONAL)
    peak = any(date.fromisoformat(l["date"]) >= date(2026, 12, 19) and date.fromisoformat(l["date"]) <= date(2027, 1, 3) for l in legs)
    party = {"families visiting relatives": rng.randint(2, 6), "vacationers": rng.randint(1, 4), "students": 1,
             "business travelers": rng.choice([1, 1, 2]), "travel agencies": rng.randint(10, 30)}[g]
    trips = [{
        "trip_id": f"{p['id']}-T1", "purpose": why, "exposure": stratum, "international": intl, "party_size": party,
        "fare_type": w(rng, {"basic (non-refundable, no free changes)": 0.6, "bundle (bag + seat, no free changes)": 0.3,
                             "flex (free changes, credit on cancel)": 0.1}),
        "fare_per_person_usd": round((210 if intl else 120) * rng.uniform(0.6, 1.6) * (1.3 if peak else 1.0)),
        "checked_bags": party if g == "families visiting relatives" else rng.choice([0, 1, 1, 2]),
        "legs": legs,
    }]
    return trips


def sector(rng, g, stratum):
    biz = g == "business travelers"
    return {
        "flights_per_year": {"students": rng.choice(["2 (fall and winter break)", "4"]), "business travelers": rng.choice(["8-10", "12-15", "20+"]),
                             "travel agencies": "books 15-40 group trips a year"}.get(g, rng.choice(["1", "2", "2-3", "4-5"])),
        "flies_kestrel": rng.choice(["twice a year, someone else otherwise", "only when Kestrel is cheapest", "mostly Kestrel from this airport",
                                     "first time on Kestrel"]),
        "rivals_also_used": rng.sample(["Frontier", "Southwest", "JetBlue", "Allegiant", "Breeze", "American", "Delta", "United", "Avelo"], 2),
        "date_flexibility": w(rng, {"fixed: cannot move": 0.45, "can move a day or two": 0.35, "fully flexible": 0.2})
        if g not in ("travel agencies", "business travelers") else "fixed: cannot move",
        "travels_with": {"families visiting relatives": rng.choice(["two kids under 10", "a spouse and a toddler", "an elderly parent who uses a cane",
                                                                    "a teenager and a spouse", "a partner and a newborn", "three kids, 4 to 15"]),
                         "students": "alone", "business travelers": rng.choice(["alone", "a coworker"]),
                         "travel agencies": "the group (the agent flies with about half of their groups)"}.get(g, rng.choice(["a partner", "two friends", "alone", "a spouse and an adult child"])),
        "needs_airport_help": w(rng, {"none": 0.85, "wheelchair assistance for a parent": 0.08, "wheelchair assistance for themselves": 0.04,
                                      "a child flying alone part of the way": 0.03}),
        "loyalty_tier": w(rng, {"not a member": 0.5, "Kestrel Rewards basic": 0.35, "Kestrel Rewards Silver": 0.12, "Kestrel Rewards Gold": 0.03}),
        "afraid_of_flying": w(rng, {"no": 0.75, "a little, needs an aisle and headphones": 0.2, "yes, takes medication to fly": 0.05}),
        "knows_refund_rights": w(rng, {"has heard of the 2024 DOT automatic-refund rule and would cite it": 0.25 + 0.3 * (biz or g == "travel agencies"),
                                       "vaguely knows you can get money back": 0.45, "assumes a voucher is all they can get": 0.3}),
        "tsa_precheck": rng.random() < (0.7 if biz else 0.3),
        "booking_channel": {"travel agencies": "books group fares by phone/email with Kestrel's group desk"}.get(g, w(rng, {"Kestrel app": 0.4, "kestrelair.com": 0.3, "Expedia": 0.15, "Google Flights then Kestrel site": 0.15})),
        "how_to_airport": rng.choice(["drives and parks in economy", "spouse drops them off", "Uber", "SEPTA Airport Line" , "LYNX bus", "a friend's ride at 4am"]),
        "connection_tolerance": rng.choice(["none: nonstop only", "one short connection is fine", "will connect anywhere to save $80"]),
        "seat": rng.choice(["window", "aisle", "whatever is free (won't pay for seats)"]),
        "buys_snacks_on_board": rng.random() < 0.3,
        "employer_pays": biz and rng.random() < 0.5,
    }


def build(seed=SEED):
    rng = random.Random(seed)
    pick = Picker(rng)
    groups = allocate(N, P.GROUPS)
    metro_names, metro_w = list(P.METROS), [m["weight"] for m in P.METROS.values()]
    names, personas = set(), []
    for g, n in groups.items():
        strata = [s for s, c in allocate(n, STRATA).items() for _ in range(c)]
        rng.shuffle(strata)
        for stratum in strata:
            pid = f"P{len(personas) + 1:03d}"
            while (name := f"{rng.choice(FIRST)} {rng.choice(LAST)}") in names:
                pass
            names.add(name)
            metro_name = rng.choices(metro_names, weights=metro_w)[0]
            metro = P.METROS[metro_name]
            place, state, area = rng.choice(metro["places"])
            age = {"students": rng.randint(18, 24), "business travelers": rng.randint(27, 62),
                   "travel agencies": rng.randint(30, 68)}.get(g, rng.randint(24, 78))
            occ, emp, employer = rng.choice(P.OCCUPATIONS[g])
            if age >= 66 and g in ("vacationers", "families visiting relatives") and rng.random() < 0.7:
                occ, emp, employer = f"retired {occ.split(' at ')[0].replace('retired ', '')}", "retired", employer
            p = {"id": pid, "group": g, "name": name, "stratum": stratum}
            p["home"] = {"metro": metro_name, "place": place, "state": state, "area": area, "airport": metro["airport"]}
            if g == "students":
                college, col_ap = pick.one([c for c in P.COLLEGES if c[1] != metro["airport"]])
                p["student"] = {"college": college, "college_airport": col_ap, "major": pick.one(P.STUDENT_MAJORS),
                                "year": rng.choice(["freshman", "sophomore", "junior", "senior"])}
            kids = rng.choice(["none", "one, age 4", "two, ages 7 and 11", "three, ages 2, 9 and 15", "two adult children"]) \
                if g != "students" else "none"
            p["demographic"] = {
                "age": age, "gender": w(rng, {"woman": 0.5, "man": 0.47, "nonbinary": 0.03}),
                "household_size": 1 if g == "students" and rng.random() < 0.6 else rng.randint(1, 5),
                "marital_status": "single" if g == "students" else rng.choice(["married", "single", "divorced", "living with a partner", "widowed" if age > 60 else "married"]),
                "children": kids, "education": "in college" if g == "students" else rng.choice(
                    ["high school diploma", "some college", "associate degree", "bachelor's degree", "master's degree", "trade certificate"]),
                "occupation": occ, "employment_status": emp, "employer_type": employer,
                "household_income": "parents' household " + rng.choice(["$35-60k", "$60-100k", "$100-150k"]) if g == "students"
                else w(rng, {"under $35k": 0.12, "$35-60k": 0.28, "$60-100k": 0.35, "$100-150k": 0.18, "$150k+": 0.07}),
                "home": rng.choice(["rents", "owns", "rents", "owns", "lives with parents" if age < 30 else "owns"]),
                "owns_car": rng.random() < 0.8,
            }
            p["life_story"] = {
                "kestrel_customer_since": rng.choice(["2014", "2018", "2021", "2023", "2025", "this is their first booking"]),
                "past_bad_experience": pick.one(P.PAST_BAD_EXPERIENCES),
                "recent_life_event": pick.one(P.LIFE_EVENTS),
                "first_in_family_to_college": rng.random() < 0.25, "served_in_military": rng.random() < 0.07,
            }
            p["values"] = {
                "values_most": pick.one(P.VALUES_MOST),
                "price_consciousness": w(rng, {"extreme: compares fares to the dollar": 0.4, "high": 0.4, "moderate": 0.2}),
                "brand_loyalty": w(rng, {"none: books whoever is cheapest": 0.55, "some": 0.35, "loyal": 0.1}),
                "trust_in_institutions": rng.choice(["low", "medium", "high"]),
                "sense_of_fairness": rng.choice(["keeps score of every fee", "average", "gives companies the benefit of the doubt"]),
                "need_for_control": rng.choice(["plans everything to the hour", "medium", "goes with the flow"]),
            }
            p["behavior"] = {
                "preferred_channel": rng.choice(["app", "website", "phone (wants a human)", "chat", "X/Twitter DM to the airline"]),
                "complaint_history": rng.choice(["never complained", "complained once by email", "has filed a DOT complaint before", "complains often"]),
                "writes_reviews": rng.choice(["never", "Google reviews sometimes", "Tripadvisor regular", "Yelp Elite"]),
                "social_media_use": rng.choice(["posts daily", "posts a few times a month", "lurks only", "barely online"]),
                "payment_method": w(rng, {"credit card": 0.55, "debit card": 0.3, "buy now pay later (Affirm)": 0.1, "Kestrel credit + card": 0.05}),
                "plans_ahead": rng.choice(["books 4+ months ahead", "books 1-2 months ahead", "books last-minute"]),
            }
            p["emotions"] = {
                "baseline_anxiety": rng.choice(["low", "medium", "high: checks the flight status every hour the day before"]),
                "anger_speed": rng.choice(["slow to anger", "medium", "fast: snaps at the first bad news"]),
                "patience_when_waiting": rng.choice(["will wait hours calmly", "about 30 minutes", "very little"]),
                "tendency_to_forgive": rng.choice(["forgives if treated decently", "holds grudges for years", "forgets quickly"]),
                "embarrassed_to_complain": rng.random() < 0.3,
                "tolerance_for_uncertainty": rng.choice(["low: needs a plan B", "medium", "high"]),
            }
            p["social_info"] = {
                "news_sources": rng.sample(metro["news"], 2) + pick.many(P.ONLINE_COMMUNITIES, 2),
                "circle_size": rng.choice(["small: a few close people", "medium", "large: knows everyone"]),
                "opinion_role": rng.choice(["leads: friends ask them first", "follows", "neither"]),
                "swayed_by_others": rng.choice(["easily", "somewhat", "rarely"]),
                "rumors": rng.choice(["believes and shares quickly", "checks before sharing", "ignores them"]),
                "asks_before_deciding": rng.choice(["spouse/partner", "their mother", "nobody", "a group chat", "a coworker who travels a lot"]),
            }
            p["money"] = {
                "savings": rng.choice(["under $500", "about one month of expenses", "3-6 months", "comfortable"]),
                "credit_card_debt": rng.choice(["none", "a few hundred dollars", "around $4,000", "over $10,000"]),
                "paycheck_to_paycheck": rng.random() < 0.4,
                "worried_about_prices": rng.choice(["very", "somewhat", "not really"]),
                "who_pays": {"students": rng.choice(["parents", "themselves (savings from a campus job)", "split with parents"]),
                             "business travelers": "their business or employer", "travel agencies": "the group members pay; agency earns a fee"}.get(g, "themselves"),
            }
            team = rng.choice(metro["teams"])
            p["lifestyle"] = {
                "tv": pick.one(P.TV_SHOWS), "film": pick.one(P.FILMS), "music": pick.one(P.MUSIC), "podcast": pick.one(P.PODCASTS),
                "hobby": pick.one(P.HOBBIES), "sports_team": team, "pet": pick.one(P.PETS), "coffee": pick.one(P.COFFEE),
                "phone": rng.choice(P.PHONES), "morning_or_night": rng.choice(["morning person", "night owl"]),
            }
            p["sector"] = sector(rng, g, stratum)
            p["trips"] = make_trips(rng, pick, p, stratum)
            personas.append(p)
    n_in = Counter(p["stratum"] for p in personas)
    for p in personas:
        p["weight_passengers"] = round(STRATUM_PAX[p["stratum"]] / n_in[p["stratum"]], 1)
        p["initial_state"] = initial_state(p)
    return personas


def initial_state(p):
    """Starting attitude before week 1; the weekly simulation evolves it from here."""
    # TODO(human): derive these from the persona's attributes instead of one neutral baseline.
    return {"would_book_again": "yes", "trust": 3, "mood": "neutral", "blame_if_disrupted": "Kestrel"}


def template_narrative(p):
    d, h, t, l = p["demographic"], p["home"], p["trips"][0], p["lifestyle"]
    out, ret = t["legs"]
    return (f"{p['name']} is {d['age']}, a {d['occupation']} in {h['place']}, {h['state']} ({d['household_income']} household, {d['home']}). "
            f"Trip: {t['purpose']}, {out['from']}->{out['to']} on {out['weekday']} {out['date']}, back {ret['date']}, "
            f"party of {t['party_size']}, {t['fare_type']} fare at ${t['fare_per_person_usd']} per person. "
            f"Past experience: {p['life_story']['past_bad_experience']}. Gets news from {', '.join(p['social_info']['news_sources'])}. "
            f"{l['tv'].capitalize()}; film: {l['film']}; listens to {l['music']} and {l['podcast']}; {l['hobby']}; roots for the {l['sports_team']}.")


PROMPT = """You are writing the background of one US airline customer for a behavior simulation.
Here is the person as JSON. Every fact in it is fixed: keep names, places, dates, numbers and named
titles exactly as given, and do not contradict any field.

{persona}

Write a 170-230 word third-person backstory that weaves in the trip, their money situation, their
past experience with airlines, where they get news, and at least four of the named lifestyle details
(shows, films, music, podcast, hobby, team, pet, coffee) as concrete everyday habits. You may add at
most two small concrete details that fit the facts. Then one final sentence on how they typically
react when travel goes wrong, consistent with the emotions fields.
Rules: no stereotypes tied to their name, place, age or gender; do not mention race, religion,
politics, health conditions or immigration status; do not mention any strike or future event.
Return only the backstory text."""


def write_narratives(personas, seed):
    from google import genai
    from google.genai import types

    client = genai.Client(vertexai=True, api_key=os.environ["TALP_KEY"],
                          http_options=types.HttpOptions(retry_options=types.HttpRetryOptions(attempts=5)))

    def one(i_p):
        i, p = i_p
        prompt = PROMPT.format(persona=json.dumps({k: v for k, v in p.items() if k not in ("initial_state", "weight_passengers", "stratum")}, indent=1))
        reply = client.models.generate_content(model=GEN_MODEL, contents=prompt,
                                               config=types.GenerateContentConfig(temperature=1.0, seed=seed + i))
        return {"id": f"gen-{p['id']}", "persona": p["id"], "week": 0, "prompt": prompt, "response": reply.text, "model": GEN_MODEL}

    with ThreadPoolExecutor(max_workers=16) as ex:
        calls = list(ex.map(one, enumerate(personas)))
    for p, c in zip(personas, calls):
        p["narrative"] = c["response"].strip()
    return calls


def check(personas):
    """Fails loudly if the set breaks the challenge minimums or our own design."""
    groups = Counter(p["group"] for p in personas)
    assert len(personas) >= 24 and len(groups) >= 3 and min(groups.values()) >= 4, groups
    assert set(groups) <= set(P.GROUPS), groups
    assert len({p["id"] for p in personas}) == len(personas)
    for p in personas:
        legs = [l for t in p["trips"] for l in t["legs"]]
        hit = any(date.fromisoformat(l["date"]) in STRIKE_DAYS and l["touches_base"] for l in legs)
        assert hit == (p["stratum"] == "strike"), (p["id"], p["stratum"], legs)
        assert all(date(2026, 11, 2) <= date.fromisoformat(l["date"]) <= date(2027, 1, 10) for l in legs), p["id"]
    total = sum(p["weight_passengers"] for p in personas)
    assert abs(total - WEEKLY_PAX * 10) < len(personas), total


def report(personas):
    print(f"{len(personas)} personas")
    print("group x stratum:", dict(Counter((p["group"], p["stratum"]) for p in personas)))
    for field in ("tv", "film", "music", "podcast", "hobby", "pet", "coffee", "sports_team"):
        c = Counter(p["lifestyle"][field] for p in personas)
        print(f"  {field:12s} {len(c):3d} distinct, most repeated x{c.most_common(1)[0][1]}")
    combos = Counter(tuple(p["lifestyle"][f] for f in ("tv", "film", "music", "hobby")) for p in personas)
    print(f"  identical tv+film+music+hobby combos: {sum(v for v in combos.values() if v > 1)}")


def write_md(personas, path):
    lines = ["# Kestrel Air personas", "", f"{len(personas)} personas, generated by `code/build_personas.py` (seed {SEED}). "
             "Source of truth is `personas.jsonl`; this file is a readable view for the team and the board Q&A.", "",
             "| id | name | group | home | stratum | trip | weight (pax) |", "|---|---|---|---|---|---|---|"]
    for p in personas:
        t = p["trips"][0]
        o, r = t["legs"]
        lines.append(f"| {p['id']} | {p['name']} | {p['group']} | {p['home']['place']}, {p['home']['state']} | {p['stratum']} | "
                     f"{o['from']}->{o['to']} {o['date']}, back {r['date']} | {p['weight_passengers']} |")
    for p in personas:
        lines += ["", f"## {p['id']} {p['name']} ({p['group']})", "", p["narrative"], "",
                  "<details><summary>All fields</summary>", "", "```json",
                  json.dumps({k: v for k, v in p.items() if k != "narrative"}, indent=1, ensure_ascii=False), "```", "</details>"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="template narratives, no LLM calls")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()
    personas = build(args.seed)
    check(personas)
    OUT.mkdir(exist_ok=True)
    if args.dry_run:
        for p in personas:
            p["narrative"] = template_narrative(p)
    else:
        calls = write_narratives(personas, args.seed)
        with open(OUT / "gen_calls.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(c, ensure_ascii=False) + "\n" for c in calls)
    with open(OUT / "personas.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps(p, ensure_ascii=False) + "\n" for p in personas)
    write_md(personas, OUT / "PERSONAS.md")
    report(personas)


if __name__ == "__main__":
    main()
