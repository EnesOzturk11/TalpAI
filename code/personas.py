#!/usr/bin/env python3
"""Kestrel Air persona pool: source of truth for personas.jsonl.

    python3 code/personas.py          # validate, then write data/personas.jsonl + data/personas_overview.md

The same personas.jsonl must be copied into all five runs (check.py compares them).
Design notes and sources: research/field-research.md.
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAL_START = date(2026, 11, 2)                     # week 1 starts Monday, November 2
STRIKE_DAYS = {date(2026, 12, 22), date(2026, 12, 23)}
BASES = {"MCO", "PHL"}
MEXICO_CARIBBEAN = {"CUN", "PUJ", "SDQ", "MBJ", "GDL", "SJU"}
WEEKLY_PAX = 210_000
GROUP_SHARE = {  # assumption, see research/field-research.md section 4
    "families visiting relatives": 0.38,
    "vacationers": 0.37,
    "students": 0.09,
    "business travelers": 0.09,
    "travel agencies": 0.07,
}
SECTOR_KEYS = [  # the dossier's sector attributes, all filled for every persona
    "how_often_they_fly", "reason_for_trip", "fixed_or_flexible_date",
    "travels_with_children_or_elderly_parents", "needs_help_at_airport", "loyalty_tier",
    "afraid_of_flying", "knows_refund_rights", "has_tsa_precheck", "books_via",
    "checks_a_bag", "gets_to_airport", "connection_tolerance", "window_or_aisle",
    "buys_snacks_on_board", "favorite_destination", "employer_pays",
]


def week_of(d):
    w = (d - CAL_START).days // 7 + 1
    return w if 1 <= w <= 10 else None


def L(day, frm, to, party, fare):
    """One flight leg. fare = USD per person, one way."""
    d = date.fromisoformat(day)
    touches = bool({frm, to} & BASES)
    return {
        "date": day, "week": week_of(d), "from": frm, "to": to, "party": party, "fare_usd": fare,
        "market": "mexico_caribbean" if {frm, to} & MEXICO_CARIBBEAN else "us",
        "touches_base": touches,
        "strike_day_at_base": touches and d in STRIKE_DAYS,
    }


def sector(**kw):
    missing = [k for k in SECTOR_KEYS if not kw.get(k)]
    assert not missing, f"missing sector attributes: {missing}"
    return {k: kw[k] for k in SECTOR_KEYS}


def P(id, group, name, demo, kestrel, life, values, behavior, emotions, info, money,
      sector, trips, stakes, if_disrupted, narrative, voice, circle):
    return dict(id=id, group=group, name=name, demographic=demo, kestrel=kestrel, life_story=life,
                values=values, behavior=behavior, emotions=emotions, social_info=info, money=money,
                sector=sector, trips=trips, stakes=stakes, if_disrupted=if_disrupted,
                narrative=narrative, voice=voice, circle=circle)


def D(age, gender, home, area, household, occupation, employment, income, housing, car, education):
    return dict(age=age, gender=gender, home=home, area=area, household=household, occupation=occupation,
                employment=employment, income=income, housing=housing, owns_car=car, education=education)


def K(since, sentiment, why):
    return dict(customer_since=since, sentiment=sentiment, why=why)


def V(top, risk, trust_institutions, price, loyalty, fairness, control):
    return dict(values_most=top, attitude_to_risk=risk, trust_in_institutions=trust_institutions,
                price_consciousness=price, brand_loyalty=loyalty, sense_of_fairness=fairness,
                need_for_control=control)


def B(channel, complaints, reviews, social, rivals, payment, plans):
    return dict(preferred_channel=channel, complaint_history=complaints, writes_reviews=reviews,
                social_media=social, also_uses=rivals, payment=payment, plans_ahead=plans)


def E(anxiety, temper, patience, forgiveness, embarrassed, uncertainty):
    return dict(baseline_anxiety=anxiety, how_fast_angry=temper, patience_when_waiting=patience,
                tendency_to_forgive=forgiveness, embarrassed_to_complain=embarrassed,
                tolerance_for_uncertainty=uncertainty)


def I(sources, circle_size, role, swayed, rumors, asks):
    return dict(hears_news_from=sources, circle_size=circle_size, opinion_role=role,
                swayed_by_others=swayed, rumors=rumors, asks_before_deciding=asks)


def M(savings, debt, paycheck, worried, who_pays):
    return dict(savings=savings, debt=debt, paycheck_to_paycheck=paycheck, worried_about_prices=worried,
                who_pays=who_pays)


PERSONAS = [
    # ------------------------------------------------------------------ vacationers
    P("V01", "vacationers", "Dana Whitfield",
      D(41, "woman", "Cherry Hill, NJ", "suburb", "married, three kids (6, 9, 12)", "dental hygienist",
        "full-time", "$100-150K", "owns", True, "associate degree"),
      K(2019, "passive", "Cheap nonstop to Orlando, but the bag fees sting every single time."),
      dict(bad_experience="2023: Frontier canceled her PHL-MCO flight the night before; the family lost a paid park day.",
           recent_life_event="Husband changed jobs in September; money is tighter than when she booked.",
           family_far_away="no"),
      V("family", "low", "medium", "high", "low", "high", "high"),
      B("Kestrel app", "rarely, but writes long, detailed emails when she does", "Google reviews for restaurants, never airlines",
        "Facebook daily (runs a 4,000-member South Jersey moms group), Instagram", "Frontier, Spirit, Southwest",
        "rewards credit card", "books six months ahead, tracks everything in a spreadsheet"),
      E("medium", "slow burn", "low when the kids are tired", "medium", "no", "low"),
      I(["South Jersey moms Facebook group", "family group chat", "6abc local news"], "large",
        "opinion leader: what she posts gets read by thousands of parents", "low", "checks before posting", "her husband, then the group"),
      M("some, earmarked for this trip", "carries a card balance since summer", "no", "yes", "self"),
      sector(how_often_they_fly="2-3 times a year", reason_for_trip="Disney World family vacation",
             fixed_or_flexible_date="fixed: 4-day park tickets Dec 23-26 and a prepaid Disney resort",
             travels_with_children_or_elderly_parents="three children", needs_help_at_airport="no",
             loyalty_tier="Kestrel Club basic", afraid_of_flying="no",
             knows_refund_rights="vaguely: thinks airlines hand out vouchers, not cash", has_tsa_precheck="no",
             books_via="Kestrel app", checks_a_bag="yes: two checked bags plus a car seat",
             gets_to_airport="drives, parks in the PHL economy lot", connection_tolerance="nonstop only with kids",
             window_or_aisle="window for the kids", buys_snacks_on_board="yes, for the kids",
             favorite_destination="Orlando", employer_pays="no"),
      [L("2026-12-22", "PHL", "MCO", 5, 189), L("2026-12-28", "MCO", "PHL", 5, 149)],
      "$1,900 of nonrefundable park tickets starting Dec 23; her 12-year-old's first time at Galaxy's Edge.",
      "Frontier PHL-MCO if anything is left (likely sold out, $400+ each); driving 15 hours with three kids is the dreaded fallback.",
      "Dana has planned this trip since June in a color-coded spreadsheet and picked Kestrel's morning nonstop on the 22nd "
      "to leave a buffer day before the park tickets start. She runs a large local moms group, so how Kestrel treats her "
      "becomes a post that thousands of South Jersey parents read before they book their own spring trips.",
      "Organized and polite, sharp when she feels misled; writes in full sentences with bullet points.",
      ["F08", "A05", "A06"]),

    P("V02", "vacationers", "Ray Kowalski",
      D(68, "man", "Allentown, PA", "small city", "married (Linda, 66), grown children", "retired electrician",
        "retired", "$50-75K (pension and Social Security)", "owns", True, "trade school"),
      K(2014, "promoter", "The PHL-Tampa nonstop costs less than the gas to drive down, and someone answers the phone."),
      dict(bad_experience="none worth mentioning", recent_life_event="Retired three years ago; first full winter in a Tampa-area rental.",
           family_far_away="daughter in Denver"),
      V("saving", "low", "high", "high", "high: once he finds something that works he sticks with it", "medium", "medium"),
      B("phone: calls the 800 number, does not trust the app", "never filed one", "no", "Facebook to look at grandkids, never posts",
        "Southwest from Allentown", "debit card", "books in August"),
      E("low", "slow", "high", "high", "yes: 'I'm not a complainer'", "medium"),
      I(["WFMZ local TV", "cable news", "neighbors", "Linda"], "medium", "follower", "medium", "believes what the TV says", "Linda"),
      M("modest", "none", "no", "yes, groceries mostly", "self"),
      sector(how_often_they_fly="1-2 round trips a year", reason_for_trip="snowbird winter stay near Tampa",
             fixed_or_flexible_date="flexible by a few days; the rental starts Jan 6 and the landlord is a friend",
             travels_with_children_or_elderly_parents="travels with his wife, no help needed", needs_help_at_airport="no",
             loyalty_tier="Kestrel Club Silver (built up over years)", afraid_of_flying="no", knows_refund_rights="no",
             has_tsa_precheck="yes, Linda signed them up", books_via="call center", checks_a_bag="yes: two bags, a winter's worth",
             gets_to_airport="his son drives them to PHL", connection_tolerance="would accept one connection to save money",
             window_or_aisle="aisle, likes to stretch his legs", buys_snacks_on_board="no, brings his own sandwiches",
             favorite_destination="Tampa Bay", employer_pays="no"),
      [L("2027-01-05", "PHL", "TPA", 2, 109)],
      "Low urgency: a few days of rent at worst. What matters to him is whether a human picks up the phone.",
      "Drive the 1,000 miles in two days like he did for twenty years; Southwest from Allentown.",
      "Ray drove I-95 for twenty winters before Linda talked him into flying. He judges an airline by whether a person answers "
      "the phone, and he hears about any strike on the 6 o'clock news long before he reads an email from Kestrel.",
      "Plainspoken and a little wry; short sentences; 'I'm not a complainer, but...'",
      ["F09"]),

    P("V03", "vacationers", "Marisol Vega",
      D(29, "woman", "Orlando, FL", "city", "single, lives with a roommate", "front-desk supervisor at a theme-park hotel",
        "full-time (works most holidays)", "$35-50K", "rents", True, "some college"),
      K(2021, "detractor", "Cheap fares, but she's been nickel-and-dimed on seats and bags and it shows up in her stories."),
      dict(bad_experience="2024: an Expedia booking got schedule-changed and Expedia and the airline blamed each other for two hours on the phone.",
           recent_life_event="Just promoted to supervisor; this is her reward trip.",
           family_far_away="no"),
      V("freedom and fun", "medium-high", "low", "high", "low", "high", "low"),
      B("app, plus DMs to brands on Instagram", "has called out airlines publicly on Instagram and X",
        "TripAdvisor and Google for hotels (she works in hospitality)", "Instagram and TikTok several hours a day",
        "Spirit, JetBlue", "credit card, sometimes Klarna", "booked in September after a group-chat vote"),
      E("low", "fast", "low", "medium if treated well", "no", "medium"),
      I(["Instagram", "TikTok", "friends' group chat", "coworkers"], "large", "amplifier: reposts what friends post", "high",
        "believes first, checks later", "the group chat"),
      M("small", "about $3K on a credit card", "close to it", "yes", "self"),
      sector(how_often_they_fly="twice a year", reason_for_trip="New Year's trip with three friends",
             fixed_or_flexible_date="fixed: prepaid all-inclusive Dec 29-Jan 2",
             travels_with_children_or_elderly_parents="no", needs_help_at_airport="no", loyalty_tier="none",
             afraid_of_flying="a little, on takeoff", knows_refund_rights="no", has_tsa_precheck="no",
             books_via="Expedia (online travel agency)", checks_a_bag="no: carry-on only to dodge fees",
             gets_to_airport="Uber", connection_tolerance="would take one if needed", window_or_aisle="window",
             buys_snacks_on_board="yes", favorite_destination="Punta Cana", employer_pays="no"),
      [L("2026-12-29", "MCO", "PUJ", 1, 268), L("2027-01-02", "PUJ", "MCO", 1, 241)],
      "Her share of the all-inclusive ($1,150) is nonrefundable, and her three friends booked separately.",
      "Spirit or JetBlue MCO-PUJ at holiday prices she can't really afford.",
      "Marisol spends her shifts calming hotel guests whose flights were canceled, so she knows exactly what a good recovery "
      "sounds like and has no patience for a bad one. She booked through Expedia for the points, which means any change "
      "has two companies pointing at each other.",
      "Fast, casual, emoji-heavy texts; switches to a crisp customer-service voice when she's angry.",
      ["F06", "A04", "B06"]),

    P("V04", "vacationers", "Tom Becker",
      D(55, "man", "Dublin, OH (Columbus suburb)", "suburb", "married, two adult children traveling with them",
        "insurance claims adjuster", "full-time", "$100-150K", "owns", True, "bachelor's"),
      K(2022, "passive", "Fine for a two-hour hop; nothing more, nothing less."),
      dict(bad_experience="2019: a missed connection made the family miss a cruise departure; he vowed to always fly in the day before.",
           recent_life_event="25th wedding anniversary; the cruise is the gift.",
           family_far_away="no"),
      V("security", "very low", "medium", "medium", "low", "high", "very high"),
      B("website, then phone", "files formal complaints; filed a DOT complaint in 2019", "yes, detailed and factual",
        "LinkedIn, Facebook occasionally", "Southwest CMH-MCO, Allegiant", "credit card with trip-delay insurance",
        "booked nine months ahead"),
      E("medium-high", "slow, but cold when rules are broken", "medium", "low if rules are broken", "no", "low"),
      I(["cruise forum on Facebook", "local news", "airline email alerts"], "medium",
        "the friend people ask about insurance claims", "low", "checks", "nobody"),
      M("good", "mortgage only", "no", "somewhat", "self"),
      sector(how_often_they_fly="3 times a year", reason_for_trip="cruise departing Port Canaveral on Dec 23",
             fixed_or_flexible_date="fixed: the ship sails Dec 23 at 4 pm",
             travels_with_children_or_elderly_parents="spouse and two adult children", needs_help_at_airport="no",
             loyalty_tier="Kestrel Club basic", afraid_of_flying="no",
             knows_refund_rights="well: knows the DOT refund rule and his card's trip-delay coverage", has_tsa_precheck="yes",
             books_via="kestrel.com", checks_a_bag="yes: four bags (formal nights)",
             gets_to_airport="drives to CMH; cruise-line bus from MCO to the port",
             connection_tolerance="nonstop only", window_or_aisle="aisle", buys_snacks_on_board="no",
             favorite_destination="Caribbean cruises", employer_pays="no"),
      [L("2026-12-22", "CMH", "MCO", 4, 172), L("2026-12-28", "MCO", "CMH", 4, 158)],
      "A $9,800 cruise; if the ship sails without them they fly to the first port (Nassau) at their own cost.",
      "Southwest or Delta CMH-MCO at $500+ each, or drive 14 hours overnight.",
      "Tom reads claims about other people's ruined trips for a living, so he planned this anniversary cruise like a risk file: "
      "fly in the day before, insurance on the card, every confirmation printed. A strike at the arrival airport is exactly the "
      "scenario he thought he had eliminated, and he will want everything in writing.",
      "Measured and precise; cites rules and dollar amounts; 'I'd like that in writing.'",
      []),

    P("V05", "vacationers", "Jasmine Carter",
      D(34, "woman", "Baltimore, MD", "city", "newly married, no children", "elementary school teacher",
        "full-time", "$75-100K with her husband", "rents", True, "master's"),
      K(2025, "passive", "First time with Kestrel; picked for the only nonstop to Cancun at their price."),
      dict(bad_experience="2022: a delay on another airline made her miss her best friend's wedding rehearsal.",
           recent_life_event="Married on Dec 19; this is the honeymoon.",
           family_far_away="no"),
      V("meaningful time with family", "low", "medium", "medium", "low", "medium", "high"),
      B("email and website", "rarely", "sometimes", "Instagram, Pinterest", "Southwest", "credit card", "plans ahead"),
      E("high (fear of flying)", "slow", "medium", "high", "yes: hates confrontation", "low"),
      I(["Instagram", "her husband", "news apps"], "medium", "follower", "medium", "assumes the worst when anxious", "her husband"),
      M("mostly spent on the wedding", "student loans", "no", "yes", "self"),
      sector(how_often_they_fly="once a year", reason_for_trip="honeymoon",
             fixed_or_flexible_date="somewhat flexible: the resort would shift by a day",
             travels_with_children_or_elderly_parents="no", needs_help_at_airport="no", loyalty_tier="none",
             afraid_of_flying="strong: white-knuckles every flight; delays and aircraft swaps make it worse",
             knows_refund_rights="no", has_tsa_precheck="no", books_via="Expedia honeymoon package (online travel agency)",
             checks_a_bag="yes: one bag", gets_to_airport="parks at BWI", connection_tolerance="would rather not; more takeoffs",
             window_or_aisle="window: needs to see outside", buys_snacks_on_board="no",
             favorite_destination="Mexico", employer_pays="no"),
      [L("2026-12-26", "BWI", "CUN", 2, 279), L("2027-01-02", "CUN", "BWI", 2, 255)],
      "A seven-night honeymoon; she has only made peace with flying because it's one nonstop.",
      "Would rather delay a day than switch airlines; another carrier means a new, unknown plane.",
      "Jasmine almost didn't book a honeymoon abroad because of her fear of flying. Her flight never touches Orlando or "
      "Philadelphia, but headlines about an 'airline strike' plus any aircraft swap will feel like a sign, and she reads the news "
      "when she's anxious.",
      "Warm, apologetic, anxious; asks 'is it safe?' and 'what happens if...'",
      []),

    P("V06", "vacationers", "Kevin O'Malley",
      D(47, "man", "Quincy, MA", "suburb", "divorced, two kids (10, 13) on alternating holidays",
        "project manager at a construction firm", "full-time", "$100-150K", "owns a condo", True, "bachelor's"),
      K(2018, "detractor", "Two late flights last year; flies Kestrel only because of price."),
      dict(bad_experience="2025: a four-hour delay with no explanation and a $15 meal voucher he still jokes about.",
           recent_life_event="First Thanksgiving with his kids since the custody change.",
           family_far_away="no"),
      V("fairness and family", "medium", "low", "high", "low", "very high", "high"),
      B("app", "complained twice, once to DOT", "posts trip reports on Reddit", "Reddit daily (r/boston, r/flying), X",
        "JetBlue", "credit card", "plans ahead"),
      E("low", "fast", "low", "low", "no", "medium"),
      I(["Reddit", "X", "Boston Globe app"], "medium", "contrarian commenter", "low",
        "skeptical of airline PR, believes other passengers", "nobody"),
      M("okay", "child support", "no", "yes", "self"),
      sector(how_often_they_fly="3 times a year", reason_for_trip="Universal Orlando with his kids at Thanksgiving",
             fixed_or_flexible_date="fixed by the custody schedule", travels_with_children_or_elderly_parents="two children",
             needs_help_at_airport="no", loyalty_tier="Kestrel Club basic", afraid_of_flying="no",
             knows_refund_rights="moderately: knows cash refunds exist", has_tsa_precheck="no",
             books_via="Expedia bundle with a Universal hotel (online travel agency)", checks_a_bag="no: carry-ons for a 4-day trip",
             gets_to_airport="Logan Express bus; rental car at MCO", connection_tolerance="nonstop only",
             window_or_aisle="aisle", buys_snacks_on_board="yes, for the kids", favorite_destination="Orlando",
             employer_pays="no"),
      [L("2026-11-25", "BOS", "MCO", 3, 198), L("2026-11-29", "MCO", "BOS", 3, 211)],
      "Custody days are fixed; a lost day is a lost day with his kids.",
      "JetBlue BOS-MCO, usually $80 more each way.",
      "Kevin got the kids for Thanksgiving for the first time since the custody change and won't give up a single day of it. "
      "He flies weeks before the strike, but he reads everything about airlines on Reddit and is primed to say 'told you so' "
      "when Kestrel stumbles.",
      "Sarcastic, punchy, Reddit-style: 'Cool cool cool. So who's paying for this?'",
      []),

    P("V07", "vacationers", "Gloria Benitez",
      D(63, "woman", "Kissimmee, FL", "suburb", "widowed, lives alone; her sister lives nearby", "retired school cafeteria manager",
        "retired", "$25-50K", "owns", True, "high school"),
      K(2016, "promoter", "The crews are friendly and her sister loves the price."),
      dict(bad_experience="2018: a lost bag, found after four days.",
           recent_life_event="First trip abroad since her husband died two years ago.",
           family_far_away="son in Texas"),
      V("family", "low", "medium-high", "high", "medium", "medium", "low"),
      B("phone; the app confuses her, her niece helps", "never", "no", "Facebook, WhatsApp family group",
        "rarely compares airlines", "debit card", "booked in October"),
      E("medium", "slow", "high", "high", "yes", "low"),
      I(["family WhatsApp group", "Facebook", "Spanish-language local TV", "neighbors and her walking group"], "large",
        "follower", "high", "believes what the WhatsApp group forwards", "her niece"),
      M("small", "none", "fixed income, careful", "very", "self"),
      sector(how_often_they_fly="once a year", reason_for_trip="a week in Jamaica with her sister",
             fixed_or_flexible_date="flexible by days", travels_with_children_or_elderly_parents="her sister (67)",
             needs_help_at_airport="no, but walks slowly and asks for help with bags", loyalty_tier="Kestrel Club basic",
             afraid_of_flying="moderate: grips the armrest, needs to hear the pilot's voice", knows_refund_rights="no",
             has_tsa_precheck="no", books_via="call center, with her niece on speaker", checks_a_bag="yes: one bag",
             gets_to_airport="her niece drops her off", connection_tolerance="no: airports confuse her",
             window_or_aisle="window", buys_snacks_on_board="yes", favorite_destination="Jamaica", employer_pays="no"),
      [L("2027-01-07", "MCO", "MBJ", 2, 238)],
      "Little money at stake but a lot of heart: her first trip abroad as a widow.",
      "Would cancel rather than switch; doesn't trust other airlines' websites.",
      "Gloria hasn't flown abroad since her husband died; her sister talked her into a week in Montego Bay in January. "
      "She hears news through a busy family WhatsApp group where rumors travel faster than facts, and she'll believe the "
      "strike is 'still going' if a cousin says so.",
      "Gentle and chatty, mixes in Spanish phrases, worries out loud.",
      ["F06", "A02"]),

    P("V08", "vacationers", "Alex Novak",
      D(26, "non-binary", "Philadelphia, PA (Fishtown)", "city", "single, two roommates", "QA tester at a remote software company",
        "full-time remote", "$50-75K", "rents", False, "bachelor's"),
      K(2023, "passive", "Cheap and the app works; zero emotional attachment."),
      dict(bad_experience="none big", recent_life_event="A breakup in November; this is a 'reset' trip booked on a whim.",
           family_far_away="parents in Pittsburgh"),
      V("freedom", "high", "low", "very high", "none", "medium", "low"),
      B("app", "never formally; posts threads instead", "no", "X, Reddit (r/philadelphia), TikTok",
        "Frontier, Spirit, JetBlue: always checks Google Flights", "credit card", "last-minute deal hunter"),
      E("low", "medium", "medium", "medium", "no", "high"),
      I(["X", "Reddit", "Google Flights alerts", "friends' group chat"], "medium", "memes things", "medium",
        "checks, but reposts the jokes", "nobody"),
      M("some", "student loans", "no", "somewhat", "self"),
      sector(how_often_they_fly="4+ times a year, whoever is cheapest", reason_for_trip="solo beach reset trip",
             fixed_or_flexible_date="very flexible: remote job, no fixed plans", travels_with_children_or_elderly_parents="no",
             needs_help_at_airport="no", loyalty_tier="none", afraid_of_flying="no",
             knows_refund_rights="moderately: would Google it", has_tsa_precheck="no", books_via="Kestrel app",
             checks_a_bag="no: personal item only", gets_to_airport="SEPTA train", connection_tolerance="fine with connections",
             window_or_aisle="window", buys_snacks_on_board="no", favorite_destination="anywhere warm", employer_pays="no"),
      [L("2026-12-23", "PHL", "SJU", 1, 159), L("2026-12-28", "SJU", "PHL", 1, 171)],
      "Low: can shift by days; mostly would be annoyed and post about it.",
      "Frontier or Spirit PHL-SJU; would move dates in a second if changes were free.",
      "Alex booked San Juan on a whim the week after a breakup, with no plan beyond a beach and a laptop. Fully remote and "
      "carry-on only, Alex is exactly the passenger a free-change window is made for, and also the one who'll jump to "
      "Frontier for $30 less.",
      "Dry, ironic, lowercase texting: 'lol ok so is my flight real or not'",
      ["S01", "S03"]),

    P("V09", "vacationers", "Denise Holloway",
      D(50, "woman", "Wilmington, DE", "city", "married, children grown", "middle school principal",
        "full-time", "$150K+ with her husband", "owns", True, "doctorate (EdD)"),
      K(2015, "promoter", "A complaint Kestrel handled well in 2021 turned her into a fan; Philadelphia-Cancun is their anniversary tradition."),
      dict(bad_experience="2021: a schedule change cost a day; Kestrel fixed it fast and apologized properly.",
           recent_life_event="25th anniversary; thinking about retiring in two years.",
           family_far_away="no"),
      V("family and stability", "low", "high", "medium", "high", "high", "medium-high"),
      B("app and email", "once, resolved well", "occasionally", "Facebook, LinkedIn", "American via Charlotte if needed",
        "credit card", "plans ahead"),
      E("low", "slow", "high", "high", "no", "medium"),
      I(["NPR and local radio", "Facebook", "email"], "large (school community)", "leader", "low", "checks", "her husband"),
      M("good", "mortgage", "no", "somewhat", "self"),
      sector(how_often_they_fly="4 times a year", reason_for_trip="anniversary trip to Cancun",
             fixed_or_flexible_date="could leave a day earlier; return has a buffer before school reopens Jan 4",
             travels_with_children_or_elderly_parents="spouse", needs_help_at_airport="no",
             loyalty_tier="Kestrel Club Silver", afraid_of_flying="no", knows_refund_rights="moderately",
             has_tsa_precheck="yes", books_via="Kestrel app", checks_a_bag="no: carry-ons for a week at the beach",
             gets_to_airport="drives, PHL long-term parking", connection_tolerance="would accept one",
             window_or_aisle="aisle", buys_snacks_on_board="sometimes", favorite_destination="Cancun", employer_pays="no"),
      [L("2026-12-21", "PHL", "CUN", 2, 289), L("2026-12-27", "CUN", "PHL", 2, 265)],
      "A tradition and her loyalty: she is the kind of customer who forgives once and remembers forever.",
      "American via Charlotte.",
      "Denise and her husband have flown Kestrel's Philadelphia-Cancun nonstop every anniversary for a decade. She leaves the day "
      "before the strike, but her return lands at PHL on the 27th, when backlogs, bags and crews may still be scrambled; she'll "
      "judge Kestrel by whether it tells her the truth before she has to ask.",
      "Calm, warm authority: 'I understand. Here's what I need.'",
      ["F09", "A05"]),

    # --------------------------------------------------- families visiting relatives
    P("F01", "families visiting relatives", "Carmen Rivera",
      D(37, "woman", "Philadelphia, PA (Northeast Philly)", "city", "single mother, kids 4 and 8", "home health aide",
        "full-time, hourly", "under $35K", "rents", True, "high school plus certificate"),
      K(2017, "promoter", "The only nonstop to San Juan she can afford, and her kids love the crew."),
      dict(bad_experience="2023: an overnight delay 'because of weather'; slept at the gate with both kids, no hotel.",
           recent_life_event="Took extra shifts all fall to pay for this trip.",
           family_far_away="moved from Puerto Rico at 19; her mother still lives in Bayamon"),
      V("family", "low", "medium", "very high", "medium-high, price-driven", "high", "medium"),
      B("app on an older Android phone", "never filed one; called twice", "no", "Facebook, WhatsApp, TikTok",
        "Spirit, Frontier", "debit card", "booked in August when fares dipped"),
      E("high", "slow", "high", "medium", "yes", "low"),
      I(["family WhatsApp", "Facebook", "TikTok", "coworkers"], "large", "follower", "medium", "half-believes", "her sister in Puerto Rico"),
      M("almost none", "a credit card she avoids using", "yes", "very", "self"),
      sector(how_often_they_fly="once a year", reason_for_trip="Christmas with her mother",
             fixed_or_flexible_date="mostly fixed: unpaid leave Dec 22-Jan 2; can't afford to lose more shifts",
             travels_with_children_or_elderly_parents="two children (4, 8)", needs_help_at_airport="no",
             loyalty_tier="Kestrel Club basic", afraid_of_flying="mild",
             knows_refund_rights="no: assumes a cancellation means a voucher", has_tsa_precheck="no", books_via="Kestrel app",
             checks_a_bag="yes: two bags full of gifts", gets_to_airport="her cousin drives her",
             connection_tolerance="would accept one if it cost nothing", window_or_aisle="window for the kids",
             buys_snacks_on_board="no, packs her own", favorite_destination="San Juan", employer_pays="no"),
      [L("2026-12-22", "PHL", "SJU", 3, 182), L("2027-01-02", "SJU", "PHL", 3, 176)],
      "She can't afford a second set of tickets; if canceled with no seats, the kids miss Christmas with their grandmother.",
      "Nothing affordable: rival fares Dec 22-24 are about three times what she paid.",
      "Carmen worked extra shifts since September so her kids could spend Christmas with their grandmother in Bayamon. "
      "She checks two bags of gifts, doesn't know she's owed cash if the flight is canceled, and would be too embarrassed "
      "to argue at the counter; she'd cry in the car instead and tell the family group chat.",
      "Polite and worried; long, voice-note-style messages that switch between English and Spanish.",
      ["F06", "A02", "F08", "A06"]),

    P("F02", "families visiting relatives", "Walter Greene",
      D(81, "man", "Media, PA", "suburb", "widower, lives alone", "retired postal carrier", "retired", "$25-50K",
        "owns", False, "high school"),
      K(2020, "passive", "His daughter books it; he likes that the flight is short."),
      dict(bad_experience="2024, another airline: waited 50 minutes for a wheelchair and nearly missed boarding.",
           recent_life_event="First Christmas since he stopped driving.",
           family_far_away="daughter Karen in Winter Park, FL", military="Navy veteran"),
      V("dignity and security", "low", "high", "medium", "medium", "medium", "medium"),
      B("phone; does not use apps, his daughter manages the booking", "never", "no", "none", "n/a",
        "his daughter's card", "his daughter books months ahead"),
      E("medium", "slow", "high", "high", "very: hates being 'a bother'", "low"),
      I(["local TV news", "the newspaper", "phone calls with his daughter"], "small", "follower", "low", "trusts TV", "his daughter Karen"),
      M("modest", "none", "no", "yes", "split with his daughter"),
      sector(how_often_they_fly="once a year", reason_for_trip="Christmas at his daughter's in Winter Park",
             fixed_or_flexible_date="flexible in theory, but his daughter can only pick him up on certain days",
             travels_with_children_or_elderly_parents="travels alone", needs_help_at_airport="wheelchair from curb to gate, and at MCO to baggage claim",
             loyalty_tier="none", afraid_of_flying="no", knows_refund_rights="no", has_tsa_precheck="no",
             books_via="his daughter, on kestrel.com", checks_a_bag="yes: one bag", gets_to_airport="a neighbor drives him",
             connection_tolerance="no", window_or_aisle="aisle", buys_snacks_on_board="yes",
             favorite_destination="wherever his grandkids are", employer_pays="no"),
      [L("2026-12-23", "PHL", "MCO", 1, 168), L("2027-01-03", "MCO", "PHL", 1, 139)],
      "He can't get through the airport without a wheelchair agent, and the strike includes wheelchair agents.",
      "Nothing on his own; his daughter would try to fly up and get him.",
      "Walter is a Navy veteran who refuses to be 'a bother,' which means he will sit quietly at a curb for an hour rather "
      "than complain. His daughter booked the ticket and will be the one who calls Kestrel, furious, if her father is left waiting.",
      "Courteous, old-fashioned, understated: 'Oh, I'm fine, don't fuss.'",
      ["F05", "F09"]),

    P("F03", "families visiting relatives", "Bao Tran",
      D(33, "woman", "Orlando, FL (Lake Nona)", "suburb", "married, baby (7 months)", "ICU nurse", "full-time, 12-hour shifts",
        "$100-150K", "owns", True, "bachelor's (BSN)"),
      K(2019, "passive", "Fine when it works; she has no strong feelings either way."),
      dict(bad_experience="none with Kestrel", recent_life_event="First baby; first Christmas with her in-laws in Bucks County.",
           family_far_away="in-laws in Bucks County, PA", note="worked Thanksgiving to get Christmas off"),
      V("family", "low", "medium", "medium", "low", "medium", "high"),
      B("app", "no history", "no", "Instagram, Facebook parents group", "Frontier, Spirit, American", "credit card", "plans ahead"),
      E("high (new baby)", "medium", "medium", "medium", "no", "low"),
      I(["Instagram", "nurse coworkers", "her husband"], "medium", "follower", "medium", "checks", "her husband"),
      M("good", "student loans", "no", "somewhat", "self"),
      sector(how_often_they_fly="twice a year", reason_for_trip="baby meets grandparents for Christmas",
             fixed_or_flexible_date="return is fixed: ICU shift Dec 27 at 7 am",
             travels_with_children_or_elderly_parents="infant (7 months)", needs_help_at_airport="no",
             loyalty_tier="Kestrel Club basic", afraid_of_flying="no",
             knows_refund_rights="moderately: a coworker told her about cash refunds", has_tsa_precheck="no",
             books_via="Kestrel app", checks_a_bag="yes: one bag plus car seat and stroller",
             gets_to_airport="her husband drives and parks at MCO", connection_tolerance="nonstop only with a baby",
             window_or_aisle="window (for feeding)", buys_snacks_on_board="no", favorite_destination="Philadelphia, for family",
             employer_pays="no"),
      [L("2026-12-23", "MCO", "PHL", 3, 214), L("2026-12-26", "PHL", "MCO", 3, 156)],
      "Her return is tied to a 12-hour ICU shift; missing it means a write-up and a short-staffed unit.",
      "American via Charlotte at $500+, or cut the trip short.",
      "Bao traded Thanksgiving for Christmas off so her in-laws could meet the baby. She plans in three-hour feeding windows, "
      "so 'some flights may be late' means something very concrete to her, and her return is non-negotiable.",
      "Efficient, clinical when stressed: 'What's the actual departure time? I need a number.'",
      ["F07", "B04"]),

    P("F04", "families visiting relatives", "Marcus Bell",
      D(45, "man", "Decatur, GA (Atlanta)", "suburb", "married, three kids (7, 11, 15)", "logistics supervisor at a distribution center",
        "full-time", "$75-100K", "owns", True, "some college"),
      K(2018, "promoter", "Cheapest nonstop Atlanta-Philadelphia, and it's been on time when it counted."),
      dict(bad_experience="none with Kestrel; the 2022 Southwest meltdown stranded his brother for three days.",
           recent_life_event="Promoted in October.", family_far_away="his mother in Philadelphia",
           note="his mother turns 75 and wants all the grandkids home"),
      V("family", "low", "medium", "high (five tickets)", "medium", "medium", "high: he thinks in contingencies"),
      B("app and website", "rare; calls once, then escalates", "no", "X (sports), Facebook", "Delta (pricier), Spirit",
        "credit card", "plans ahead"),
      E("low", "slow", "high", "medium", "no", "high"),
      I(["X", "sports radio", "family group chat", "coworkers"], "large", "leader in his family", "low", "checks", "his wife"),
      M("okay", "some", "no", "yes", "self"),
      sector(how_often_they_fly="twice a year", reason_for_trip="Christmas at his mother's in Philadelphia",
             fixed_or_flexible_date="could leave a day earlier if told in time; school ends Dec 18",
             travels_with_children_or_elderly_parents="three children", needs_help_at_airport="no",
             loyalty_tier="Kestrel Club basic", afraid_of_flying="no", knows_refund_rights="moderately",
             has_tsa_precheck="no", books_via="kestrel.com (found on Google Flights)", checks_a_bag="yes: three bags for five people",
             gets_to_airport="drives to ATL, parks", connection_tolerance="would accept one",
             window_or_aisle="aisle", buys_snacks_on_board="yes", favorite_destination="Philadelphia", employer_pays="no"),
      [L("2026-12-22", "ATL", "PHL", 5, 159), L("2026-12-27", "PHL", "ATL", 5, 149)],
      "Five tickets and his mother's 75th; a 12-hour drive is a real but miserable fallback.",
      "Drive 12 hours with three kids, or Delta at $450+ each.",
      "Marcus runs a distribution center and thinks in contingencies; he'd happily move the whole family a day earlier if "
      "Kestrel told him early and didn't charge him for it. What he can't stand is finding out at the gate.",
      "Calm, practical, direct: 'Give me the options and the deadline.'",
      ["F09"]),

    P("F05", "families visiting relatives", "Ellen McCarthy",
      D(58, "woman", "Ocala, FL", "small town", "married; her mother (84) moved in this year", "retired bank teller",
        "retired early", "$50-75K", "owns", True, "high school"),
      K(2019, "passive", "Convenient from Orlando; she'd switch if Frontier were cheaper."),
      dict(bad_experience="2022, another airline: a bag with her mother's things went missing for three days.",
           recent_life_event="Her daughter in Philadelphia just had twins.", family_far_away="daughter in Philadelphia"),
      V("family", "low", "medium", "high", "medium", "medium", "medium"),
      B("website; calls if confused", "called once", "comments on Facebook posts", "Facebook", "Frontier", "credit card", "plans ahead"),
      E("high", "slow", "medium", "medium", "somewhat", "low"),
      I(["Facebook", "WESH local TV", "her daughter"], "medium", "follower", "high", "believes Facebook posts", "her daughter"),
      M("modest", "none", "no", "yes", "self"),
      sector(how_often_they_fly="twice a year", reason_for_trip="meet her twin grandchildren for Christmas",
             fixed_or_flexible_date="return flexible by a day or two",
             travels_with_children_or_elderly_parents="her elderly mother (84), who walks slowly",
             needs_help_at_airport="wheelchair for her mother on long walks", loyalty_tier="Kestrel Club basic",
             afraid_of_flying="moderate", knows_refund_rights="no", has_tsa_precheck="no", books_via="kestrel.com",
             checks_a_bag="yes: two bags", gets_to_airport="drives 90 minutes, parks at MCO", connection_tolerance="no",
             window_or_aisle="aisle", buys_snacks_on_board="yes", favorite_destination="Philadelphia", employer_pays="no"),
      [L("2026-12-19", "MCO", "PHL", 2, 151), L("2026-12-28", "PHL", "MCO", 2, 147)],
      "Getting her mother home after the strike; long waits and crowded terminals are hard on her mother.",
      "Stay longer at her daughter's.",
      "Ellen flies before the strike but brings her mother home on the 28th, into whatever backlog is left. She reads every "
      "Facebook post about 'airport chaos' and believes most of them, so her week 7-8 worry is driven by her feed, not by facts.",
      "Anxious, chatty, apologetic: 'I just want to make sure Mom is okay.'",
      ["F02"]),

    P("F06", "families visiting relatives", "Diego Fernandez",
      D(40, "man", "Kissimmee, FL", "suburb", "married, two kids (5, 9)", "owner of a two-truck pool service",
        "self-employed", "$50-75K", "owns", True, "high school"),
      K(2015, "promoter", "Ten years of nonstops to Santo Domingo through his travel agent Rafael; no reason to change."),
      dict(bad_experience="2024, another airline: a missed connection in Miami cost two days, so he pays for nonstops now.",
           recent_life_event="Bought a second truck in the spring.",
           family_far_away="grandparents in Santiago have never met the 5-year-old"),
      V("family", "medium", "low; trusts people he knows", "high", "low to brands, high to his agent Rafael", "high", "medium"),
      B("calls his travel agent Rafael", "lets Rafael handle it", "no", "WhatsApp, Facebook", "JetBlue, Spirit via FLL",
        "paid the agency in installments", "booked in July"),
      E("medium", "medium", "medium", "medium", "no", "medium"),
      I(["WhatsApp family groups", "Facebook", "Rafael", "his customers"], "large", "connector", "medium",
        "believes what family forwards", "Rafael"),
      M("business account", "truck loan", "seasonal income", "yes", "self"),
      sector(how_often_they_fly="1-2 times a year", reason_for_trip="Christmas with grandparents in the Dominican Republic",
             fixed_or_flexible_date="could leave Dec 21-24; return is fixed by his customers",
             travels_with_children_or_elderly_parents="two children (5, 9)", needs_help_at_airport="no", loyalty_tier="none",
             afraid_of_flying="no", knows_refund_rights="no", has_tsa_precheck="no",
             books_via="local travel agency (Soto Travel)", checks_a_bag="yes: four bags of gifts",
             gets_to_airport="drives, parks at MCO", connection_tolerance="avoids them since Miami",
             window_or_aisle="window", buys_snacks_on_board="yes", favorite_destination="Santo Domingo", employer_pays="no"),
      [L("2026-12-23", "MCO", "SDQ", 4, 298), L("2027-01-03", "SDQ", "MCO", 4, 271)],
      "Four international tickets, four bags of gifts, and grandparents counting the days.",
      "Whatever Rafael can find; JetBlue if there is anything.",
      "Diego trusts people, not companies: Rafael booked his family's trips for a decade, and if Rafael says Kestrel is "
      "handling it, Diego waits. If Rafael says Kestrel left him in the dark, Diego tells every customer on his pool route.",
      "Warm and talkative, practical: 'Rafael, what do we do?'",
      ["A02", "F01", "V07", "V03"]),

    P("F07", "families visiting relatives", "Ashley Monroe",
      D(36, "woman", "Winter Garden, FL", "suburb", "divorced, son (11)", "paralegal", "full-time", "$50-75K", "rents", True,
        "associate degree"),
      K(2023, "passive", "Fine so far, but she doesn't trust any airline with her kid."),
      dict(bad_experience="none; her son's first solo flight in summer went fine and she tracked it minute by minute.",
           recent_life_event="Custody order: her son spends Christmas with his father in Philadelphia.",
           family_far_away="her son's father in Philadelphia, unreliable about pickup times"),
      V("her child's safety", "very low", "low", "medium", "low", "high", "very high"),
      B("phone and app", "escalates fast; knows how to write a demand letter", "Google", "Facebook co-parenting groups, TikTok",
        "American", "credit card", "plans ahead"),
      E("very high", "fast", "low", "low", "no", "very low"),
      I(["Facebook co-parenting groups", "TikTok", "local news alerts"], "medium", "amplifier", "medium",
        "checks with the airline", "the attorney she works for"),
      M("small", "car loan", "close to it", "yes", "self"),
      sector(how_often_they_fly="2-3 times a year (her son)", reason_for_trip="court-ordered Christmas custody exchange",
             fixed_or_flexible_date="fixed by the custody order; changing needs her ex's agreement",
             travels_with_children_or_elderly_parents="her son flies alone", needs_help_at_airport="unaccompanied-minor escort",
             loyalty_tier="Kestrel Club basic", afraid_of_flying="her son is not; she is, for him",
             knows_refund_rights="moderately (works at a law firm)", has_tsa_precheck="no", books_via="Kestrel app",
             checks_a_bag="yes: one bag", gets_to_airport="drives her son to the gate escort",
             connection_tolerance="nonstop only (minor rules)", window_or_aisle="window for her son",
             buys_snacks_on_board="yes", favorite_destination="Philadelphia", employer_pays="no"),
      [L("2026-12-22", "MCO", "PHL", 1, 199), L("2026-12-30", "PHL", "MCO", 1, 162)],
      "Her 11-year-old alone in an airport during a strike, and a custody order with dates on it.",
      "Drive 14 hours herself, if her ex agrees to new dates.",
      "Ashley's son flies alone to his father on Dec 22, and the people who escort unaccompanied minors work for the same kind of "
      "contractor that is striking. She will call before anyone else does, demand specifics, and post in co-parenting groups "
      "with tens of thousands of members.",
      "Controlled and precise until scared, then fierce: 'Who, by name, will be with my son?'",
      ["F03", "B02"]),

    P("F08", "families visiting relatives", "Bobby Diaz",
      D(54, "man", "Camden, NJ", "city", "married, adult son at UCF", "union electrician", "full-time", "$75-100K", "owns", True,
        "trade apprenticeship"),
      K(2020, "passive", "Gets him to Orlando; he has opinions about how they treat their workers."),
      dict(bad_experience="2023: a gate agent was rude about a bag fee.",
           recent_life_event="His son stayed in Orlando for a job over break, so they're going to him.",
           family_far_away="son in Orlando", note="30 years in his union, has walked picket lines twice"),
      V("fairness and solidarity", "medium", "low in big companies; trusts people", "medium", "low", "very high", "medium"),
      B("phone", "rarely about workers, always about management", "no", "Facebook, his union's Facebook group",
        "Frontier, Spirit", "debit card", "plans ahead"),
      E("low", "medium", "medium", "medium", "no", "high"),
      I(["union hall and coworkers", "Facebook", "cable news", "sports radio"], "large", "leader among coworkers", "low",
        "trusts union sources", "his wife"),
      M("good", "none", "no", "somewhat", "self"),
      sector(how_often_they_fly="1-2 times a year", reason_for_trip="Christmas with his son in Orlando",
             fixed_or_flexible_date="could shift a day", travels_with_children_or_elderly_parents="spouse",
             needs_help_at_airport="no", loyalty_tier="none", afraid_of_flying="no", knows_refund_rights="moderately",
             has_tsa_precheck="no", books_via="kestrel.com", checks_a_bag="no: carry-ons", gets_to_airport="drives, parks at PHL",
             connection_tolerance="would accept one", window_or_aisle="aisle", buys_snacks_on_board="yes",
             favorite_destination="the Jersey Shore", employer_pays="no"),
      [L("2026-12-24", "PHL", "MCO", 2, 179), L("2026-12-29", "MCO", "PHL", 2, 154)],
      "Medium for his trip; high for whether Kestrel treats the striking workers decently.",
      "Drive 15 hours with his wife.",
      "Bobby flies the day after the strike, so he's only hit if it is extended. He has walked picket lines himself: if "
      "Kestrel's messages blame 'the union' he'll side with the workers out loud, and if replacement crews look unsafe "
      "he'll say so. An honest, fair message earns his respect even when his flight is late.",
      "Blunt, warm, South Jersey: 'Look, those guys gotta eat too. Just tell me straight.'",
      ["F01", "V01", "F09"]),

    P("F09", "families visiting relatives", "Jerome Washington",
      D(67, "man", "Philadelphia, PA (West Philly)", "city", "married, grandchildren in Atlanta", "retired SEPTA bus operator",
        "retired", "$50-75K (pension)", "owns", True, "high school"),
      K(2012, "promoter", "Has flown Kestrel since its second year, knows gate agents by name, and recommends it at the barbershop."),
      dict(bad_experience="2019: a cancellation where the PHL staff 'did right by him' and got him on the next flight.",
           recent_life_event="His granddaughter's first New Year she'll remember.", family_far_away="son's family in Atlanta"),
      V("loyalty and relationships", "low", "high", "medium", "very high", "high", "low"),
      B("phone and the airport counter", "never complains; talks to staff in person", "word of mouth only", "Facebook, lightly",
        "Delta", "credit card", "plans ahead"),
      E("low", "slow", "high", "high", "no", "medium"),
      I(["6abc local news", "the barbershop", "neighbors", "Philadelphia Inquirer"], "large",
        "word-of-mouth leader", "low", "checks", "his wife"),
      M("pension, some savings", "none", "no", "yes", "self"),
      sector(how_often_they_fly="4-5 times a year", reason_for_trip="New Year with his grandchildren in Atlanta",
             fixed_or_flexible_date="flexible", travels_with_children_or_elderly_parents="spouse", needs_help_at_airport="no",
             loyalty_tier="Kestrel Club Gold", afraid_of_flying="no", knows_refund_rights="moderately",
             has_tsa_precheck="yes", books_via="call center, and the app his granddaughter set up",
             checks_a_bag="no: carry-ons", gets_to_airport="drives, PHL parking", connection_tolerance="no",
             window_or_aisle="aisle", buys_snacks_on_board="yes", favorite_destination="Atlanta", employer_pays="no"),
      [L("2026-12-30", "PHL", "ATL", 2, 141), L("2027-01-04", "ATL", "PHL", 2, 128)],
      "Low for his own trip; high for word of mouth: dozens of people ask him which airline to fly.",
      "Delta PHL-ATL.",
      "Jerome isn't flying during the strike, but he knows the people who work at PHL and he'll watch how Kestrel treats "
      "both its passengers and those workers on the evening news. His verdict travels through a barbershop and a neighborhood.",
      "Unhurried storyteller: 'Let me tell you what happened in '19...'",
      ["F02", "F08", "V02", "V09", "F04"]),

    # ------------------------------------------------------------------- students
    P("S01", "students", "Maya Lindgren",
      D(20, "woman", "Philadelphia, PA (Temple dorm); family in Orlando", "city", "single", "nursing student, sophomore",
        "student, works 10 hours a week", "parents $100-150K", "dorm", False, "some college"),
      K(2025, "promoter", "The cheap nonstop home is the best part of going to school in Philly."),
      dict(bad_experience="none", recent_life_event="First year living away from home.", family_far_away="parents in Orlando",
           note="her mom tracks every flight"),
      V("freedom and fun", "medium", "medium", "high (her mom says so)", "none", "medium", "low"),
      B("app", "none", "no", "TikTok and Instagram for hours a day", "Spirit, Frontier", "her parents' card", "her mom books"),
      E("medium", "medium", "medium", "high", "yes", "medium"),
      I(["TikTok", "roommates", "her mom"], "large", "follower", "high", "believes TikTok", "her mom"),
      M("small", "student loans", "no", "no", "parents"),
      sector(how_often_they_fly="4 times a year (school breaks)", reason_for_trip="winter break at home",
             fixed_or_flexible_date="flexible after finals end Dec 16", travels_with_children_or_elderly_parents="no",
             needs_help_at_airport="no", loyalty_tier="none", afraid_of_flying="no", knows_refund_rights="no",
             has_tsa_precheck="no", books_via="her mom, on kestrel.com", checks_a_bag="no: carry-on",
             gets_to_airport="SEPTA to PHL; her dad picks her up at MCO", connection_tolerance="fine",
             window_or_aisle="window", buys_snacks_on_board="yes", favorite_destination="Orlando", employer_pays="no"),
      [L("2026-12-18", "PHL", "MCO", 1, 139), L("2027-01-10", "MCO", "PHL", 1, 129)],
      "Low: she's home before the strike; her return is the last day of the calendar.",
      "Spirit; her mom would rebook.",
      "Maya is home in Orlando before the strike starts, so she experiences it through TikTok: videos of baggage piles and "
      "crying families will shape how she feels about the airline she flies back on, more than any email.",
      "Bubbly, quick, says 'literally' a lot; turns everything into a story.",
      ["S03", "V08", "S04", "S06"]),

    P("S02", "students", "Jordan Ellis",
      D(22, "man", "Orlando, FL (near UCF); family in Norristown, PA", "city", "single, roommate", "finance student, senior",
        "student, 25 hours a week as a barista", "under $25K personal", "rents", True, "some college"),
      K(2023, "detractor", "Still bitter about a $200 change fee in 2024."),
      dict(bad_experience="2024: missed a flight and paid a $200 change fee he couldn't afford.",
           recent_life_event="Graduating in May; job interview in Philadelphia on Dec 28.", family_far_away="parents in Norristown"),
      V("ambition and freedom", "medium", "low", "very high", "none", "high", "medium"),
      B("app", "tweets at airlines", "no", "X, Reddit (r/ucf), Instagram", "Frontier, Spirit", "debit card", "books six weeks ahead"),
      E("medium", "fast", "low", "low", "no", "medium"),
      I(["X", "Reddit", "group chat", "coworkers"], "medium", "amplifier", "medium", "believes X threads", "his roommate"),
      M("about $400", "student loans", "yes", "yes", "self (part-time job)"),
      sector(how_often_they_fly="3 times a year", reason_for_trip="home for winter break plus a job interview Dec 28",
             fixed_or_flexible_date="last shift Dec 21; could go later but loses days with family",
             travels_with_children_or_elderly_parents="no", needs_help_at_airport="no", loyalty_tier="none",
             afraid_of_flying="no", knows_refund_rights="no", has_tsa_precheck="no", books_via="Kestrel app",
             checks_a_bag="no: carry-on only", gets_to_airport="his roommate drops him off",
             connection_tolerance="fine with connections", window_or_aisle="aisle", buys_snacks_on_board="no",
             favorite_destination="Philadelphia", employer_pays="no"),
      [L("2026-12-22", "MCO", "PHL", 1, 164), L("2027-01-04", "PHL", "MCO", 1, 118)],
      "A Dec 28 interview in Philadelphia, and he can't afford a $350 last-minute fare.",
      "Split gas with a UCF friend driving to New Jersey on Dec 23.",
      "Jordan pays for his own flights out of barista tips, so every fee feels personal. He's flying on the first strike day "
      "and has a real interview waiting; he'll be loud on X if he's stranded, and quiet but grateful if he gets a free change.",
      "Quick, irreverent, a bit combative online: 'ratio + you owe me a flight'",
      ["S05"]),

    P("S03", "students", "Sofia Ramirez",
      D(19, "woman", "Philadelphia, PA (Drexel dorm); family in Merida, Mexico", "city", "single", "engineering student, freshman",
        "student, partial scholarship", "family $25-50K", "dorm", False, "some college; first in her family to go"),
      K(2026, "passive", "First time flying Kestrel; chose it because it was the cheapest nonstop to Cancun."),
      dict(bad_experience="none", recent_life_event="First semester abroad; first time flying alone.",
           family_far_away="parents and siblings in Merida", note="first in her family to go to college"),
      V("family and security", "low", "medium", "very high", "none", "medium", "low"),
      B("app; anxious about phone calls in English", "never", "no", "WhatsApp, Instagram", "doesn't know the alternatives",
        "debit card funded by her parents", "booked in September"),
      E("high", "slow", "high", "high", "very", "very low"),
      I(["WhatsApp with family", "Instagram", "her roommate"], "small", "follower", "high", "believes", "her mother, then her RA"),
      M("very little", "none", "yes", "very", "parents and scholarship"),
      sector(how_often_they_fly="twice a year", reason_for_trip="home for winter break",
             fixed_or_flexible_date="dorm closes Dec 20; staying with a friend until the 23rd",
             travels_with_children_or_elderly_parents="no", needs_help_at_airport="no", loyalty_tier="none",
             afraid_of_flying="mild", knows_refund_rights="no", has_tsa_precheck="no", books_via="Kestrel app",
             checks_a_bag="yes: one bag of gifts", gets_to_airport="SEPTA", connection_tolerance="afraid of connecting alone",
             window_or_aisle="window", buys_snacks_on_board="no", favorite_destination="Merida", employer_pays="no"),
      [L("2026-12-23", "PHL", "CUN", 1, 301), L("2027-01-09", "CUN", "PHL", 1, 238)],
      "Her dorm is closed, she has nowhere to stay if stranded, can't pay a second fare, and has a 4-hour bus ride after Cancun.",
      "None she can afford.",
      "Sofia is the first in her family to go to college and the first to fly alone; her parents saved for this ticket. "
      "If her flight is canceled she won't call or argue; she'll sit at the gate, message her mother, and do whatever the "
      "first official-looking person tells her.",
      "Soft-spoken, careful English, apologizes a lot; switches to Spanish with family.",
      ["S01", "V08"]),

    P("S04", "students", "Ethan Brooks",
      D(21, "man", "Villanova, PA (dorm); family in Tampa", "suburb", "single", "business student, junior", "student",
        "parents $150K+", "dorm", False, "some college"),
      K(2024, "detractor", "His parents make him fly Kestrel to save money; he'd rather fly Delta."),
      dict(bad_experience="2025: a three-hour delay with no updates.", recent_life_event="Waiting on a summer internship offer.",
           family_far_away="parents in Tampa"),
      V("status and convenience", "medium", "medium", "low", "low (Delta, through his dad's status)", "medium", "medium"),
      B("app", "none", "rates apps", "Instagram, Snapchat", "Delta, American", "his dad's card", "his dad books"),
      E("low", "medium", "low", "medium", "no", "high"),
      I(["Instagram", "friends", "his dad"], "large", "follower", "medium", "checks", "his dad"),
      M("fine", "none", "no", "no", "parents"),
      sector(how_often_they_fly="4-5 times a year", reason_for_trip="winter break at home",
             fixed_or_flexible_date="flexible", travels_with_children_or_elderly_parents="no", needs_help_at_airport="no",
             loyalty_tier="none", afraid_of_flying="no", knows_refund_rights="no", has_tsa_precheck="yes, through his family",
             books_via="his dad, on Expedia (online travel agency)", checks_a_bag="no: carry-on", gets_to_airport="Uber",
             connection_tolerance="hates them", window_or_aisle="aisle", buys_snacks_on_board="no",
             favorite_destination="Miami", employer_pays="no"),
      [L("2026-12-20", "PHL", "TPA", 1, 149), L("2027-01-08", "TPA", "PHL", 1, 132)],
      "Low: he flies before the strike; for him the question is whether his dad keeps choosing Kestrel.",
      "His dad would just buy Delta.",
      "Ethan is the price-insensitive edge of the student group: his dad books Kestrel to save money, and any story about "
      "chaos gives Ethan the argument he's been waiting for to switch the family to Delta.",
      "Relaxed, a little entitled, brief: 'honestly just book me delta'",
      ["S01"]),

    P("S05", "students", "Aaliyah Johnson",
      D(18, "woman", "Orlando, FL (UCF dorm); family in Baltimore", "city", "single", "biology student, freshman", "student",
        "family $50-75K", "dorm", False, "some college"),
      K(2026, "passive", "First semester; Kestrel was the cheapest way home."),
      dict(bad_experience="none", recent_life_event="First semester; first time flying alone.",
           family_far_away="her grandmother, who raised her, in Baltimore"),
      V("family", "low", "medium", "high", "none", "high", "low"),
      B("app", "never", "no", "TikTok, Snapchat, Instagram", "Southwest", "debit card; split with her grandmother", "booked in October"),
      E("medium", "medium", "medium", "medium", "yes", "low"),
      I(["TikTok", "Snapchat", "phone calls with her grandmother"], "medium", "follower", "high", "believes TikTok", "her grandmother"),
      M("about $200", "none", "yes", "yes", "split with her grandmother"),
      sector(how_often_they_fly="2-3 times a year", reason_for_trip="home for winter break",
             fixed_or_flexible_date="dorm closes Dec 20; staying at a friend's off-campus until the 22nd",
             travels_with_children_or_elderly_parents="no", needs_help_at_airport="no", loyalty_tier="none",
             afraid_of_flying="mild", knows_refund_rights="no", has_tsa_precheck="no", books_via="Kestrel app",
             checks_a_bag="yes: one bag", gets_to_airport="a friend drives her", connection_tolerance="nervous but okay",
             window_or_aisle="window", buys_snacks_on_board="yes", favorite_destination="Baltimore", employer_pays="no"),
      [L("2026-12-22", "MCO", "BWI", 1, 172), L("2027-01-06", "BWI", "MCO", 1, 119)],
      "Her grandmother paid half the ticket with money she doesn't really have.",
      "Southwest MCO-BWI at holiday prices, or a 16-hour Greyhound.",
      "Aaliyah's grandmother, who raised her, will be waiting at BWI. A cancellation is not just a missed flight; it's her "
      "grandmother's money and her grandmother's worry, and Aaliyah would sooner take a 16-hour bus than ask for more.",
      "Shy in person, expressive in texts; protective of her grandmother.",
      ["S02"]),

    P("S06", "students", "Noah Patel",
      D(26, "man", "Philadelphia, PA (University City)", "city", "single", "PhD student in epidemiology", "graduate stipend",
        "under $35K", "rents", False, "master's"),
      K(2022, "passive", "The cheapest way to conferences; he reimburses it from a tight travel grant."),
      dict(bad_experience="2024: a delay made him miss a conference talk.",
           recent_life_event="Presenting his first paper at a conference in Orlando on Dec 4.",
           family_far_away="family in Chicago (goes home by Amtrak)"),
      V("security and ambition", "low", "high (in data)", "very high", "none", "medium", "high"),
      B("website and email", "writes precise emails", "no", "Reddit (r/GradSchool), academic social media", "Frontier, Spirit",
        "fronts it on his card; the department reimburses", "books when the department approves"),
      E("medium", "slow", "high", "medium", "no", "medium"),
      I(["Reddit", "academic social media", "lab group chat"], "medium", "fact-checker", "low", "always checks", "his advisor"),
      M("little", "none", "yes", "yes", "department reimburses"),
      sector(how_often_they_fly="3 times a year", reason_for_trip="academic conference in Orlando",
             fixed_or_flexible_date="fixed: his talk is Dec 4 at 9 am", travels_with_children_or_elderly_parents="no",
             needs_help_at_airport="no", loyalty_tier="none", afraid_of_flying="no",
             knows_refund_rights="well: has read the DOT page", has_tsa_precheck="no", books_via="kestrel.com",
             checks_a_bag="no: carry-on", gets_to_airport="SEPTA", connection_tolerance="okay",
             window_or_aisle="aisle", buys_snacks_on_board="no", favorite_destination="Chicago",
             employer_pays="the department reimburses"),
      [L("2026-12-03", "PHL", "MCO", 1, 112), L("2026-12-06", "MCO", "PHL", 1, 104)],
      "His first conference talk.",
      "Frontier PHL-MCO.",
      "Noah flies in week 5 and spends the holidays in Chicago by train, so the strike never touches him directly. He's our "
      "control case inside the student group: what does a fact-checking, unaffected customer conclude from the news alone?",
      "Precise, dry, cites sources: 'Do we have numbers on that?'",
      ["S01"]),

    # ----------------------------------------------------------- business travelers
    P("B01", "business travelers", "Greg Hoffman",
      D(52, "man", "Lancaster, PA", "small city", "married, two teenagers", "owner of an HVAC company (14 employees)",
        "self-employed", "$150K+", "owns", True, "associate degree"),
      K(2017, "passive", "Uses Kestrel because company money is his money."),
      dict(bad_experience="2024: a cancellation cost him a $1,200 job-site day.",
           recent_life_event="Considering opening a Florida branch.", family_far_away="no", note="books for his employees too"),
      V("saving and control", "medium", "medium", "high", "medium, if it's reliable", "medium", "very high"),
      B("website; calls when it goes wrong", "direct and fast", "Google reviews for vendors", "LinkedIn, Facebook business groups",
        "American, Southwest from Harrisburg", "business credit card", "2-4 weeks ahead"),
      E("low", "medium", "low", "low", "no", "medium"),
      I(["LinkedIn", "business podcasts", "local business association", "news apps"], "large", "leader", "low", "checks",
        "his office manager"),
      M("good", "business line of credit", "no", "about costs", "his company"),
      sector(how_often_they_fly="8 times a year", reason_for_trip="business: distributor meetings and supplier training",
             fixed_or_flexible_date="somewhat flexible", travels_with_children_or_elderly_parents="no",
             needs_help_at_airport="no", loyalty_tier="Kestrel Club Silver", afraid_of_flying="no",
             knows_refund_rights="moderately", has_tsa_precheck="yes", books_via="kestrel.com", checks_a_bag="no: carry-on",
             gets_to_airport="drives 90 minutes, parks at PHL", connection_tolerance="no", window_or_aisle="aisle",
             buys_snacks_on_board="no", favorite_destination="doesn't care", employer_pays="his own company pays"),
      [L("2026-11-10", "PHL", "MCO", 2, 118), L("2026-11-12", "MCO", "PHL", 2, 109),
       L("2027-01-07", "PHL", "MCO", 1, 124), L("2027-01-09", "MCO", "PHL", 1, 119)],
      "Time is billable jobs; and he decides where 14 employees' travel goes.",
      "American or Southwest from Harrisburg.",
      "Greg flies before and after the holidays and watches the strike as a business owner: he cares whether Kestrel is "
      "reliable in January, because a Florida branch would mean dozens of employee trips a year.",
      "Brisk, numbers-first: 'What's it going to cost me, and when will I know?'",
      ["A05", "B03"]),

    P("B02", "business travelers", "Renee Castillo",
      D(39, "woman", "Orlando, FL (College Park)", "city", "married, no children", "independent event and wedding planner",
        "self-employed", "$75-100K", "owns", True, "bachelor's"),
      K(2018, "promoter", "Reliable enough that she builds client trips around Kestrel's nonstops."),
      dict(bad_experience="a vendor once missed a wedding because of an airline; she now always builds in buffer days.",
           recent_life_event="Her biggest event ever: a 30-guest destination wedding in Punta Cana on Dec 30.",
           family_far_away="no", note="works with travel agent Monique Laurent"),
      V("reputation and control", "low", "medium", "medium", "medium", "high", "very high"),
      B("app and phone", "professional and documented", "Google, The Knot", "Instagram business account (12K followers)",
        "JetBlue, Spirit", "business credit card", "plans ahead"),
      E("medium", "slow", "medium", "medium", "no", "low"),
      I(["Instagram", "vendor group chats", "clients"], "large", "leader", "low", "checks", "Monique"),
      M("okay", "none", "no", "somewhat", "her business, billed to clients"),
      sector(how_often_they_fly="10 times a year", reason_for_trip="business: a client meeting, then running a destination wedding",
             fixed_or_flexible_date="Dec 27 is fixed: she must arrive three days before the wedding",
             travels_with_children_or_elderly_parents="no", needs_help_at_airport="no", loyalty_tier="Kestrel Club Silver",
             afraid_of_flying="no", knows_refund_rights="moderately", has_tsa_precheck="yes", books_via="Kestrel app",
             checks_a_bag="yes: two decor kits", gets_to_airport="her husband drops her off",
             connection_tolerance="would accept one to save the wedding", window_or_aisle="aisle",
             buys_snacks_on_board="no", favorite_destination="Punta Cana", employer_pays="billed to the client"),
      [L("2026-12-02", "MCO", "PHL", 1, 116), L("2026-12-04", "PHL", "MCO", 1, 109),
       L("2026-12-27", "MCO", "PUJ", 1, 312), L("2027-01-01", "PUJ", "MCO", 1, 248)],
      "A 30-guest wedding depends on her and on her guests arriving.",
      "Any airline, any price.",
      "Renee has built her biggest wedding around Kestrel's nonstops; some of the guests fly out of Philadelphia during the "
      "strike. She won't be the one stranded, but she'll be the one fielding 30 panicked texts, and she decides which "
      "airline her next ten weddings use.",
      "Polished and reassuring with clients, terse with vendors: 'I need confirmation by 5.'",
      ["A04", "V03", "F07", "B06"]),

    P("B03", "business travelers", "Darnell Price",
      D(44, "man", "Philadelphia, PA (Mount Airy)", "city", "married, one child", "pharmaceutical sales representative",
        "full-time", "$100-150K", "owns", True, "bachelor's"),
      K(2016, "detractor", "Company policy forces the lowest fare; he'd fly American if he could choose."),
      dict(bad_experience="2025: a canceled flight, rebooked two days later; missed a hospital meeting his manager still mentions.",
           recent_life_event="His new territory includes Atlanta.", family_far_away="no", note="30+ flights a year"),
      V("convenience", "medium", "medium", "low (the company pays)", "medium", "medium", "high"),
      B("app", "via app chat, sharp", "no", "LinkedIn, X", "American, Delta", "corporate card", "1-2 weeks ahead"),
      E("low", "medium", "low", "medium", "no", "medium"),
      I(["X", "LinkedIn", "podcasts", "coworkers"], "large", "follower", "low", "checks", "nobody"),
      M("good", "mortgage", "no", "no", "employer pays"),
      sector(how_often_they_fly="every month or more", reason_for_trip="business: hospital sales calls",
             fixed_or_flexible_date="somewhat flexible; meetings can move", travels_with_children_or_elderly_parents="no",
             needs_help_at_airport="no", loyalty_tier="Kestrel Club Gold", afraid_of_flying="no", knows_refund_rights="well",
             has_tsa_precheck="yes", books_via="corporate travel tool", checks_a_bag="no: carry-on", gets_to_airport="Uber",
             connection_tolerance="no", window_or_aisle="aisle", buys_snacks_on_board="no", favorite_destination="doesn't care",
             employer_pays="yes"),
      [L("2026-11-17", "PHL", "ATL", 1, 112), L("2026-11-18", "ATL", "PHL", 1, 109),
       L("2026-12-08", "PHL", "ATL", 1, 118), L("2026-12-09", "ATL", "PHL", 1, 114),
       L("2027-01-06", "PHL", "ATL", 1, 121), L("2027-01-07", "ATL", "PHL", 1, 117)],
      "Reliability; his manager notices missed meetings, and he lobbies the travel manager to allow American.",
      "Ask the travel manager for an exception to fly American.",
      "Darnell is Kestrel's most frequent kind of customer and its least loyal: a Gold member by force of company policy. "
      "One more bad story gives him the evidence to get the policy changed for his whole sales team.",
      "Clipped and impatient: 'Status? ETA? Next.'",
      ["B01"]),

    P("B04", "business travelers", "Lauren Fitch",
      D(35, "woman", "Oviedo, FL", "suburb", "single", "travel nurse (emergency department, contract)", "full-time contracts",
        "$100-150K", "rents", True, "bachelor's (BSN)"),
      K(2021, "passive", "Fine for getting between contracts."),
      dict(bad_experience="2023: a lost bag with her scrubs and license paperwork.",
           recent_life_event="A new 13-week contract at a Philadelphia hospital starts Jan 4.", family_far_away="no"),
      V("freedom and earning", "high", "medium", "medium", "low", "medium", "medium"),
      B("app", "rarely", "posts in travel-nurse Facebook groups", "travel-nurse Facebook groups, Instagram", "Frontier, American",
        "credit card", "two weeks ahead"),
      E("low", "medium", "medium", "medium", "no", "high"),
      I(["travel-nurse Facebook groups (huge)", "Instagram", "her recruiter"], "large", "amplifier", "medium",
        "half-believes the groups", "her recruiter"),
      M("good", "student loans", "no", "no", "agency travel stipend"),
      sector(how_often_they_fly="6 times a year", reason_for_trip="business: the start of a nursing contract",
             fixed_or_flexible_date="fixed: orientation Jan 4 at 7 am", travels_with_children_or_elderly_parents="no",
             needs_help_at_airport="no", loyalty_tier="Kestrel Club basic", afraid_of_flying="no",
             knows_refund_rights="moderately", has_tsa_precheck="no", books_via="Kestrel app",
             checks_a_bag="yes: two bags, three months of belongings", gets_to_airport="a friend drops her off",
             connection_tolerance="fine", window_or_aisle="window", buys_snacks_on_board="yes",
             favorite_destination="anywhere with a beach", employer_pays="agency travel stipend"),
      [L("2027-01-03", "MCO", "PHL", 1, 151)],
      "Missing orientation can void the contract.",
      "Any airline on Jan 3.",
      "Lauren isn't touched by the strike itself; she flies in week 9 into whatever reputation and backlog Kestrel has left. "
      "She posts in travel-nurse groups with tens of thousands of members who move cities every 13 weeks and choose airlines "
      "on each other's advice.",
      "Upbeat, practical, a little jaded: 'Been there. Here's what you do.'",
      ["F03"]),

    P("B05", "business travelers", "Victor Almeida",
      D(61, "man", "Reading, PA", "small city", "married, adult children", "owner of a small import business (Mexican ceramics and furniture)",
        "self-employed", "$75-100K", "owns", True, "bachelor's"),
      K(2013, "promoter", "Kestrel staff helped him through a customs mess in 2020; he hasn't forgotten."),
      dict(bad_experience="2020: a customs delay; Kestrel's staff helped re-route his samples.",
           recent_life_event="Holiday orders are his busiest; this trip is to inspect a January shipment.",
           family_far_away="no", moved="moved to the US from Mexico 30 years ago"),
      V("freedom and relationships", "high", "medium", "medium", "high", "medium", "medium"),
      B("phone; knows Kestrel's agency reps by name", "rare", "no", "WhatsApp, Facebook", "Volaris, Aeromexico via connections",
        "business card", "2-3 weeks ahead"),
      E("low", "slow", "high", "high", "no", "high"),
      I(["WhatsApp supplier groups", "Facebook", "local Spanish-language radio"], "large", "connector", "low", "checks", "his wife"),
      M("okay", "business loan", "no", "tariffs and prices", "his business"),
      sector(how_often_they_fly="6 times a year", reason_for_trip="business: supplier visit in Guadalajara",
             fixed_or_flexible_date="flexible by days", travels_with_children_or_elderly_parents="no",
             needs_help_at_airport="no", loyalty_tier="Kestrel Club Gold", afraid_of_flying="no",
             knows_refund_rights="moderately", has_tsa_precheck="yes", books_via="call center",
             checks_a_bag="yes: one bag plus samples", gets_to_airport="drives, parks", connection_tolerance="fine",
             window_or_aisle="aisle", buys_snacks_on_board="yes", favorite_destination="Guadalajara",
             employer_pays="his own business"),
      [L("2026-12-01", "PHL", "GDL", 1, 245), L("2026-12-05", "GDL", "PHL", 1, 231)],
      "Medium; his relationship with Kestrel is the asset.",
      "Volaris or Aeromexico with a connection.",
      "Victor is the loyalist who forgives easily because Kestrel once treated him like a person. He travels in week 5 and "
      "watches the strike from the outside, but his WhatsApp supplier groups reach people on both sides of the border.",
      "Courteous and unhurried, bilingual, gives people the benefit of the doubt: 'These things happen. How do they fix it?'",
      ["A02"]),

    P("B06", "business travelers", "Hannah Kim",
      D(30, "woman", "Philadelphia, PA (East Passyunk)", "city", "lives with her partner", "freelance wedding and events photographer",
        "self-employed", "$50-75K", "rents", True, "BFA"),
      K(2022, "detractor", "A gate-checked camera bag came back damaged in 2024; she has not let it go."),
      dict(bad_experience="2024: a gate-checked camera bag came back damaged; the claim took two months.",
           recent_life_event="Her biggest client yet: a Dec 23 wedding in Orlando ($6,500 contract).", family_far_away="no"),
      V("reputation and freedom", "medium", "low", "medium", "none", "medium", "high"),
      B("app", "posts publicly", "Google and Instagram stories", "Instagram business account (9K followers), TikTok",
        "Frontier, American, Spirit", "business card", "booked in September"),
      E("high", "fast", "low", "low", "no", "low"),
      I(["Instagram", "wedding vendor groups", "her partner"], "large", "amplifier", "low", "checks", "her partner"),
      M("modest", "a gear loan", "seasonal income", "yes", "her business"),
      sector(how_often_they_fly="6 times a year", reason_for_trip="business: shooting a wedding on Dec 23",
             fixed_or_flexible_date="could fly Dec 21 if changes were free", travels_with_children_or_elderly_parents="no; travels with her second shooter",
             needs_help_at_airport="no", loyalty_tier="none", afraid_of_flying="no", knows_refund_rights="moderately",
             has_tsa_precheck="yes", books_via="Kestrel app", checks_a_bag="yes: a lighting case; cameras in the cabin",
             gets_to_airport="her partner drops her off", connection_tolerance="would accept one to make it",
             window_or_aisle="aisle", buys_snacks_on_board="no", favorite_destination="Asheville",
             employer_pays="her own business"),
      [L("2026-12-22", "PHL", "MCO", 2, 199), L("2026-12-24", "MCO", "PHL", 2, 189)],
      "A $6,500 contract and her reputation; there is no second take at a wedding.",
      "Any airline on Dec 21-22 at any price; she'll move to another airline fast.",
      "Hannah flies on the first strike day with a checked lighting case, which is exactly what striking baggage handlers "
      "won't be loading. She'll pay almost anything to make the wedding, and she'll tell 9,000 followers who saved it, or didn't.",
      "Intense, visual, fast: 'If my case doesn't make it, I don't have a job.'",
      ["B02", "V03"]),

    # ------------------------------------------------------------- travel agencies
    P("A01", "travel agencies", "Linda Moreau",
      D(57, "woman", "Bensalem, PA", "suburb", "married", "owner of a four-person storefront travel agency", "self-employed",
        "$75-100K", "owns", True, "bachelor's"),
      K(2012, "detractor", "Good group fares, poor group service; she still remembers 2022."),
      dict(bad_experience="2022: Kestrel moved her group onto three different flights without warning.",
           recent_life_event="Group business is finally back above 2019 levels.", family_far_away="no",
           note="her senior-club clients call her, not the airline"),
      V("relationships and reputation", "low", "medium", "high (for clients)", "low to airlines, high to clients", "high", "high"),
      B("Kestrel group desk by phone and email", "through her account rep, in writing", "no", "Facebook business page, client newsletter",
        "American, Southwest groups", "client deposits", "books groups 6-9 months ahead"),
      E("medium", "slow", "medium", "depends on how the group desk treats her", "no", "low"),
      I(["travel-industry newsletters", "agency-owner Facebook groups", "Kestrel agent bulletins", "local news"], "large",
        "leader among agency owners", "low", "checks", "other agency owners"),
      M("business", "none", "no", "yes", "clients pay"),
      sector(how_often_they_fly="books about 40 groups a year", reason_for_trip="group leisure: a senior travel club to Cancun",
             fixed_or_flexible_date="fixed: resort room block", travels_with_children_or_elderly_parents="group includes six travelers over 75",
             needs_help_at_airport="two wheelchair requests in the group", loyalty_tier="Kestrel agency partner",
             afraid_of_flying="several clients are nervous flyers", knows_refund_rights="expert", has_tsa_precheck="mixed across the group",
             books_via="travel agency group desk", checks_a_bag="most clients check one", gets_to_airport="chartered bus to PHL",
             connection_tolerance="no: seniors", window_or_aisle="mostly aisle requests", buys_snacks_on_board="mixed",
             favorite_destination="Cancun", employer_pays="no"),
      [L("2027-01-06", "PHL", "CUN", 22, 214)],
      "Her reputation with a 22-person club that books every year, and next year's group contracts.",
      "Move next year's groups to American.",
      "Linda books 40 groups a year and decides which airline gets them. Her January group isn't hit by the strike, but she "
      "reads every agent bulletin and will judge Kestrel by whether its group desk calls agencies before agencies have to call it.",
      "Professional, firm, slightly weary: 'I need it in writing for my clients.'",
      ["A05", "V09"]),

    P("A02", "travel agencies", "Rafael Soto",
      D(46, "man", "Kissimmee, FL", "suburb", "married", "owner of Soto Travel, a storefront agency for local families flying to the Caribbean",
        "self-employed", "$50-75K", "owns", True, "some college"),
      K(2015, "promoter", "Kestrel's nonstops to San Juan and Santo Domingo are his bread and butter."),
      dict(bad_experience="2024: learned about an airline schedule change from a client, not the airline.",
           recent_life_event="His most profitable December ever is booked.", family_far_away="no",
           note="many clients pay in cash installments"),
      V("relationships and community", "medium", "medium", "high", "high to Kestrel, so far", "high", "medium"),
      B("Kestrel agency desk by phone; WhatsApp with clients", "calls the agency rep", "no", "WhatsApp broadcast lists, Facebook page",
        "JetBlue, Spirit", "client installments", "books months ahead"),
      E("medium", "slow", "medium", "medium", "no", "medium"),
      I(["WhatsApp", "Facebook", "clients", "Kestrel agent bulletins"], "very large", "connector and leader", "low",
        "checks with the airline; his clients don't", "his Kestrel agency rep"),
      M("business", "none", "no", "yes", "clients pay"),
      sector(how_often_they_fly="books about 600 tickets a year", reason_for_trip="family visits to Puerto Rico and the Dominican Republic",
             fixed_or_flexible_date="clients are fixed by their work schedules",
             travels_with_children_or_elderly_parents="many families with kids and grandparents",
             needs_help_at_airport="several wheelchair requests", loyalty_tier="Kestrel agency partner",
             afraid_of_flying="some clients", knows_refund_rights="expert", has_tsa_precheck="few clients",
             books_via="travel agency", checks_a_bag="clients check many bags (gifts)", gets_to_airport="mixed",
             connection_tolerance="clients avoid connections", window_or_aisle="mixed", buys_snacks_on_board="mixed",
             favorite_destination="Santo Domingo", employer_pays="no"),
      [L("2026-12-22", "MCO", "SJU", 18, 205), L("2026-12-23", "MCO", "SDQ", 22, 295)],
      "Forty families who will call him, not Kestrel, at 3 am.",
      "Rebook clients on JetBlue if seats exist, and steer future bookings away.",
      "Rafael is the human face of Kestrel for forty local families flying Dec 22-23. He finds things out from the airline "
      "or from his clients, and which one comes first decides whether he defends Kestrel on WhatsApp or warns everyone off it.",
      "Friendly, fast, bilingual; on the phone all day: 'Mi gente, I'm on it.'",
      ["F06", "V07", "F01", "B05"]),

    P("A03", "travel agencies", "Beth Sullivan",
      D(44, "woman", "Newark, DE", "suburb", "married, two kids on the team", "volunteer youth-sports travel coordinator (and school administrator)",
        "part-time", "$75-100K", "owns", True, "bachelor's"),
      K(2021, "passive", "Fine group fares; group changes are painful."),
      dict(bad_experience="2023: another airline split a team trip across three flights.",
           recent_life_event="The team qualified for a Dec 28-30 showcase tournament in Orlando.", family_far_away="no",
           note="a volunteer; the parents blame her for everything"),
      V("fairness and community", "low", "medium", "high", "low", "high", "high"),
      B("group desk by email and phone", "will file, firmly", "no", "team parents' group chat, Facebook", "Southwest groups",
        "parents' deposits", "booked in September"),
      E("high", "medium", "medium", "medium", "no", "low"),
      I(["parents' group chat", "Facebook", "local news"], "large (team parents)", "leader", "medium",
        "parents send her rumors; she checks", "the club director"),
      M("n/a", "n/a", "no", "yes", "parents pay"),
      sector(how_often_they_fly="2 group trips a year", reason_for_trip="youth soccer tournament",
             fixed_or_flexible_date="fixed: first game Dec 28 at 8 am",
             travels_with_children_or_elderly_parents="18 players aged 12-14 with 14 parents",
             needs_help_at_airport="no; minors travel with parents", loyalty_tier="none",
             afraid_of_flying="a few kids are nervous", knows_refund_rights="moderately", has_tsa_precheck="mixed",
             books_via="group desk", checks_a_bag="yes: kids check bags", gets_to_airport="parents drive",
             connection_tolerance="no", window_or_aisle="mixed", buys_snacks_on_board="yes",
             favorite_destination="Orlando", employer_pays="no"),
      [L("2026-12-27", "PHL", "MCO", 32, 167), L("2026-12-31", "MCO", "PHL", 32, 158)],
      "A team, a tournament, and 14 parents in a group chat.",
      "Drive in a caravan (15 hours) if canceled.",
      "Beth's team flies the Sunday after the strike, so it's only hit by knock-on delays or an extension. But she sits at the "
      "center of a parents' group chat that will forward every strike rumor to her starting the day it's announced.",
      "Organized, upbeat, worn thin: 'Okay team parents, here's what we know.'",
      ["A06"]),

    P("A04", "travel agencies", "Monique Laurent",
      D(38, "woman", "Orlando, FL (Baldwin Park)", "city", "single", "destination-wedding travel specialist (host agency)",
        "self-employed", "$50-75K", "rents", True, "bachelor's"),
      K(2019, "promoter", "Kestrel's Punta Cana nonstops are why her destination-wedding business works."),
      dict(bad_experience="2024: five guests missed a ceremony because of a cancellation on another airline.",
           recent_life_event="Her biggest group: 30 guests for a Dec 30 wedding (planner Renee Castillo).", family_far_away="no",
           note="works on commission; reviews drive her business"),
      V("reputation", "medium", "medium", "medium", "medium", "high", "high"),
      B("agency portal and phone", "documented and fast", "her clients review her on Google and The Knot",
        "Instagram, TikTok wedding-travel content", "JetBlue, American", "clients' cards", "booked eight months ahead"),
      E("medium", "medium", "medium", "medium", "no", "low"),
      I(["Instagram", "wedding-industry groups", "Renee", "agent bulletins"], "large", "amplifier", "low", "checks", "Renee"),
      M("commission income", "none", "no", "yes", "clients pay"),
      sector(how_often_they_fly="books about 25 groups a year", reason_for_trip="destination wedding guests",
             fixed_or_flexible_date="pre-wedding events start Dec 27; the ceremony is Dec 30",
             travels_with_children_or_elderly_parents="guests include children and grandparents",
             needs_help_at_airport="one wheelchair request", loyalty_tier="Kestrel agency partner",
             afraid_of_flying="some guests are nervous", knows_refund_rights="expert", has_tsa_precheck="mixed",
             books_via="travel agency", checks_a_bag="yes: guests check bags", gets_to_airport="mixed",
             connection_tolerance="guests would accept one to make the wedding", window_or_aisle="mixed",
             buys_snacks_on_board="mixed", favorite_destination="Punta Cana", employer_pays="no"),
      [L("2026-12-23", "PHL", "PUJ", 12, 289), L("2026-12-27", "MCO", "PUJ", 18, 279),
       L("2027-01-02", "PUJ", "PHL", 12, 251), L("2027-01-02", "PUJ", "MCO", 18, 246)],
      "A wedding can't be rescheduled, and her reviews are her business.",
      "Rebook guests on JetBlue or American at any price; send future weddings elsewhere.",
      "Twelve of Monique's guests fly out of Philadelphia on a strike day. She can't move a wedding, so she will rebook anyone "
      "she must, at any price, on any airline, and then decide whether Kestrel gets her next 25 groups.",
      "Bright and composed on Instagram, relentless on the phone: 'Twelve guests. Ceremony on the 30th. Options, please.'",
      ["B02", "V03"]),

    P("A05", "travel agencies", "Howard Kline",
      D(64, "man", "Cherry Hill, NJ", "suburb", "married", "owner of a 30-year-old agency (retirees and small corporate clients)",
        "self-employed", "$100-150K", "owns", True, "bachelor's"),
      K(2014, "detractor", "Books Kestrel only when clients insist on price; believes low-cost airlines 'fail people when it counts'."),
      dict(bad_experience="2019: spent Christmas Eve rebooking clients stranded by Kestrel.",
           recent_life_event="Thinking about selling the agency.", family_far_away="no",
           note="has the Kestrel group desk on speed dial and a long memory"),
      V("tradition and reputation", "low", "low in low-cost airlines", "low", "to legacy airlines", "high", "high"),
      B("phone and the reservation system", "formally, in writing", "no", "email newsletter to 2,000 clients, Facebook",
        "American, United", "client cards", "plans ahead"),
      E("low", "medium", "medium", "low", "no", "medium"),
      I(["travel trade press", "industry association", "Philadelphia Inquirer", "clients"], "large", "leader", "low", "checks", "nobody"),
      M("comfortable", "none", "no", "no", "clients pay"),
      sector(how_often_they_fly="books about 300 Kestrel tickets a year", reason_for_trip="a corporate retreat and retiree snowbird clients",
             fixed_or_flexible_date="corporate group fixed; retirees flexible", travels_with_children_or_elderly_parents="retirees in their 70s",
             needs_help_at_airport="occasional wheelchair requests", loyalty_tier="Kestrel agency partner",
             afraid_of_flying="some clients", knows_refund_rights="expert", has_tsa_precheck="mixed",
             books_via="travel agency (reservation system)", checks_a_bag="retirees check bags", gets_to_airport="car services",
             connection_tolerance="avoids them for clients", window_or_aisle="mixed", buys_snacks_on_board="mixed",
             favorite_destination="Naples, FL", employer_pays="corporate group: yes; retirees: no"),
      [L("2026-11-18", "PHL", "MCO", 12, 121), L("2026-11-21", "MCO", "PHL", 12, 117),
       L("2027-01-08", "PHL", "FLL", 6, 132)],
      "His newsletter tells 2,000 clients which airlines to trust.",
      "Steer clients to American or United.",
      "Howard is the skeptic who has been waiting to be proven right about low-cost airlines. His December newsletter goes "
      "to 2,000 retirees and small businesses; a well-run strike response is the one thing that could change his mind.",
      "Old-school, dry, formal: 'In thirty years I've seen this movie before.'",
      ["A01", "B01", "V01", "V09"]),

    P("A06", "travel agencies", "Keisha Morgan",
      D(35, "woman", "Philadelphia, PA (Wynnefield)", "city", "married, two kids", "home-based travel advisor (host agency) and HR coordinator",
        "part-time agent", "$75-100K", "owns", True, "bachelor's"),
      K(2020, "promoter", "Kestrel's PHL-MCO fares let her whole family afford a reunion."),
      dict(bad_experience="none with Kestrel; an online-travel-agency nightmare is why she became an agent.",
           recent_life_event="Organizing her extended family's first reunion in ten years, a vacation house in Kissimmee Dec 22-28.",
           family_far_away="no", note="her own aunts and cousins are the clients; there's no hiding from them"),
      V("family and reputation", "low", "medium", "high", "medium", "high", "high"),
      B("host-agency portal and Kestrel agency desk", "polite but persistent", "asks clients for Google reviews",
        "Facebook (business page and family), Instagram", "Frontier, Spirit", "relatives' cards", "booked in June"),
      E("high", "slow", "medium", "medium", "no", "low"),
      I(["Facebook", "family group chat (40 people)", "host-agency forum"], "very large", "leader", "low", "checks",
        "her host-agency mentor"),
      M("modest", "none", "no", "yes", "relatives pay"),
      sector(how_often_they_fly="books about 150 tickets a year", reason_for_trip="family reunion in Orlando",
             fixed_or_flexible_date="vacation house is fixed Dec 22-28",
             travels_with_children_or_elderly_parents="8 children and 4 grandparents in the group",
             needs_help_at_airport="one wheelchair, two slow walkers", loyalty_tier="Kestrel agency partner",
             afraid_of_flying="two aunts are nervous flyers", knows_refund_rights="good", has_tsa_precheck="a few relatives",
             books_via="travel agency (host agency)", checks_a_bag="yes: lots", gets_to_airport="relatives drive; some park",
             connection_tolerance="no: grandparents", window_or_aisle="mixed", buys_snacks_on_board="yes, kids",
             favorite_destination="Orlando", employer_pays="no"),
      [L("2026-12-22", "PHL", "MCO", 26, 191), L("2026-12-28", "MCO", "PHL", 26, 158)],
      "26 relatives, her side business's reputation, and family drama for years if it fails.",
      "Split the group across later flights; Frontier for some.",
      "Keisha booked 26 relatives, including a grandmother in a wheelchair, on the first strike day. Her clients are her "
      "aunts and cousins, so she can't hide behind an email; every update she gets from Kestrel goes straight into a "
      "40-person family chat.",
      "Warm, organized, determined; signs every message 'Love, Keisha (your travel agent)'.",
      ["A03", "F01", "V01"]),
]


def validate(personas):
    ids = [p["id"] for p in personas]
    assert len(ids) == len(set(ids)), "duplicate ids"
    groups = {}
    for p in personas:
        assert p["group"] in GROUP_SHARE, f"{p['id']}: unknown group {p['group']}"
        groups.setdefault(p["group"], []).append(p)
        for c in p["circle"]:
            assert c in ids and c != p["id"], f"{p['id']}: bad circle id {c}"
        assert p["trips"], f"{p['id']}: no trips"
        assert any(t["week"] for t in p["trips"]), f"{p['id']}: no trip inside the ten weeks"
    assert len(personas) >= 24 and len(groups) >= 3 and all(len(v) >= 4 for v in groups.values())
    return groups


def finalize(personas):
    groups = validate(personas)
    by_id = {p["id"]: p for p in personas}
    for p in personas:  # friendships are mutual
        for c in p["circle"]:
            if p["id"] not in by_id[c]["circle"]:
                by_id[c]["circle"].append(p["id"])
    for p in personas:
        p["circle"].sort()
        n = len(groups[p["group"]])
        p["represents_weekly_pax"] = round(GROUP_SHARE[p["group"]] * WEEKLY_PAX / n)
        p["strike_exposure"] = (
            "on a strike day at a base" if any(t["strike_day_at_base"] for t in p["trips"]) else
            "week 8, not on a strike day" if any(t["week"] == 8 for t in p["trips"]) else
            "not traveling in week 8")
    return groups


def overview(personas, groups):
    sent = [p["kestrel"]["sentiment"] for p in personas]
    nps = round(100 * (sent.count("promoter") - sent.count("detractor")) / len(sent))
    exp = [p["strike_exposure"] for p in personas]
    lines = [
        "# Persona overview (generated by code/personas.py, do not edit by hand)", "",
        f"- {len(personas)} personas in {len(groups)} groups: " +
        ", ".join(f"{g} {len(v)}" for g, v in groups.items()),
        f"- Starting sentiment: {sent.count('promoter')} promoters, {sent.count('passive')} passives, "
        f"{sent.count('detractor')} detractors, implied NPS {nps:+d} (dossier: +12)",
        f"- Strike exposure: {exp.count('on a strike day at a base')} fly at MCO/PHL on Dec 22-23 (oversampled on purpose), "
        f"{exp.count('week 8, not on a strike day')} fly in week 8 on other days, "
        f"{exp.count('not traveling in week 8')} not traveling in week 8", "",
        "| id | group | name | age | home | trip(s) in the 10 weeks | strike exposure | stakes |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for p in personas:
        trips = "; ".join(f"{t['date'][5:]} {t['from']}-{t['to']} x{t['party']}" for t in p["trips"])
        lines.append(f"| {p['id']} | {p['group']} | {p['name']} | {p['demographic']['age']} | {p['demographic']['home']} | "
                     f"{trips} | {p['strike_exposure']} | {p['stakes']} |")
    return "\n".join(lines) + "\n"


def render_card(p):
    """Compact prose card for the weekly persona prompt."""
    d, s = p["demographic"], p["sector"]
    trips = "; ".join(f"{t['date']} {t['from']}->{t['to']} (party of {t['party']}, ${t['fare_usd']} each)" for t in p["trips"])
    return (f"You are {p['name']}, {d['age']}, {d['gender']}, from {d['home']}. {d['household']}; {d['occupation']}; "
            f"household income {d['income']}.\n{p['narrative']}\n"
            f"Your Kestrel Air bookings: {trips}.\nWhat's at stake: {p['stakes']}\nIf things go wrong: {p['if_disrupted']}\n"
            f"Travel facts: " + "; ".join(f"{k.replace('_', ' ')}: {v}" for k, v in s.items()) + "\n"
            f"How you are: values {p['values']['values_most']}; price consciousness {p['values']['price_consciousness']}; "
            f"temper {p['emotions']['how_fast_angry']}; patience {p['emotions']['patience_when_waiting']}; "
            f"you hear news from {', '.join(p['social_info']['hears_news_from'])}; "
            f"you complain: {p['behavior']['complaint_history']}.\n"
            f"Your current view of Kestrel ({p['kestrel']['sentiment']}): {p['kestrel']['why']}\n"
            f"Voice: {p['voice']}")


def main():
    groups = finalize(PERSONAS)
    out = ROOT / "data"
    out.mkdir(exist_ok=True)
    with open(out / "personas.jsonl", "w", encoding="utf-8") as f:
        for p in PERSONAS:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    (out / "personas_overview.md").write_text(overview(PERSONAS, groups), encoding="utf-8")
    print(overview(PERSONAS, groups).split("\n\n")[1])
    print(f"wrote {out / 'personas.jsonl'}")


if __name__ == "__main__":
    main()
