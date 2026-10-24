#!/usr/bin/env python3
"""Run one Kestrel Air simulation.

    .venv/bin/python code/sim.py --name plan_1 --type plan --seed 1
    .venv/bin/python code/sim.py --name nodecision_1 --type nodecision --seed 1
    .venv/bin/python code/sim.py --name plan_nosurprises --type plan_nosurprises --seed 3
    options: --out runs_dev  --weeks 4  --personas V01,F01  --mock  --model gemini-3.5-flash

Each week: the world resolves flights (code), then every persona decides what to do (one LLM call each,
in parallel). Personas see only what reaches them: their own flights, Kestrel's messages if they are in
the target, news through their own sources, and what friends posted last week.
"""
import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path
from typing import List, Literal

from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm import LLM, DEFAULT_MODEL  # noqa: E402
from personas import render_card  # noqa: E402
import world as W  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STATUSES = ("flies as planned", "rebooked", "moved to another airline", "canceled the trip")
ACTIONS = ("nothing special", "wait and see", "check the app or email", "call Kestrel support", "complain to Kestrel",
           "file a complaint with the DOT", "post on social media", "tell friends or family", "ask for a refund",
           "accept the rebooking", "change to a different date", "book another airline", "cancel the trip",
           "write a review", "use a travel credit or points", "book a future Kestrel trip")
SOCIAL = ("facebook", "instagram", "tiktok", "x", "reddit", "snapchat", "whatsapp", "groupme", "social")

QUESTIONS = {
    "1a": "How much do you trust {company}? 1 = not at all, 5 = completely.",
    "1b": '"I can count on {company} to treat me right." 1 = strongly disagree, 5 = strongly agree.',
    "2a": "How likely are you to keep using {company} over the next three months? 1 = very unlikely, 5 = very likely.",
    "2b": '"I am thinking about leaving {company}." 1 = strongly disagree, 5 = strongly agree.',
    "3a": "How likely are you to recommend {company} to a friend or colleague? 1 = very unlikely, 5 = very likely.",
    "3b": "If a friend asked you about {company} today, what would you tell them? 1 = stay away, 5 = go for it.",
    "4a": "How fairly has {company} treated you? 1 = very unfairly, 5 = very fairly.",
    "4b": '"{company} takes advantage of people like me." 1 = strongly disagree, 5 = strongly agree.',
}


class WeekAnswer(BaseModel):
    what_you_noticed: str
    how_you_feel: str
    actions: List[Literal[ACTIONS]]
    what_you_said_or_posted: str
    posted_publicly: bool
    complaint: Literal["none", "to Kestrel", "to the DOT"]
    would_book_kestrel_again: Literal["yes", "maybe", "no"]
    recommend_0_to_10: int
    diary: str
    status: Literal[STATUSES]


class ProbeAnswer(BaseModel):
    q1a: int
    q1b: int
    q2a: int
    q2b: int
    q3a: int
    q3b: int
    q4a: int
    q4b: int


PREAMBLE = (
    "You are playing one specific, real person for a whole winter, one week at a time. Stay fully in character: "
    "you are not an assistant, not an analyst, and you do not know anyone is studying you. Behave the way this person "
    "really would, including being busy, distracted, impatient, loyal, forgiving or unfair. Most people skim or ignore "
    "airline emails, believe what their friends say, and only act when something touches them. Do not be more rational, "
    "calm or well-informed than this person is. If nothing happened to you this week, it is fine to do nothing.")

BAU = ("Kestrel's normal policy: a canceled flight is rebooked on the next Kestrel flight with a free seat, or refunded. "
       "Support is the call center and the app. Meal vouchers only for delays over 3 hours that Kestrel causes; hotels only "
       "for overnight delays Kestrel causes. Changing a flight yourself normally costs the fare difference, which is high "
       "in holiday weeks.")


def sees_social(p):
    src = " ".join(p["social_info"]["hears_news_from"] + [p["behavior"]["social_media"]]).lower()
    return any(s in src for s in SOCIAL)


class Sim:
    def __init__(self, a):
        self.a = a
        self.personas_file = ROOT / a.personas_file
        self.personas = [json.loads(l) for l in open(self.personas_file, encoding="utf-8")]
        self.all_personas = list(self.personas)
        if a.personas:
            keep = set(a.personas.split(","))
            self.personas = [p for p in self.personas if p["id"] in keep]
        dec_file = ROOT / "config" / "decisions" / ("nodecision.json" if a.type == "nodecision" else "plan.json")
        self.decisions, self.cost = W.load_decisions(a.decisions or dec_file)
        self.crises = W.load_crises(surprises=a.type != "plan_nosurprises")
        self.world = W.World(self.personas, self.decisions, self.crises, a.seed)
        self.llm = LLM(a.seed, model=a.model, mock=a.mock)
        self.state = {p["id"]: {"status": "flies as planned", "diary": [], "posts": {}, "moved": {}} for p in self.personas}
        self.weekly, self.probe = [], []

    # ------------------------------------------------------------------ prompts
    def week_prompt(self, p, week):
        st, w = self.state[p["id"]], self.world
        agent = p["group"] == "travel agencies"
        parts = [PREAMBLE, "", "WHO YOU ARE", render_card(p)]
        if agent:
            parts.append("You are a travel agent: the bookings above are your clients' group bookings. Your 'status' "
                         "describes what happens to those clients' Kestrel bookings.")
        parts += ["", f"NOW: {W.week_label(week)}."]
        if st["diary"]:
            parts += ["YOUR DIARY FROM EARLIER WEEKS:"] + [f"- {d}" for d in st["diary"][-4:]]
        parts.append(f"Your Kestrel status last week: {st['status']}.")
        if "recommend" in st:
            parts.append(f"Last week you said you would recommend Kestrel {st['recommend']}/10 and would book it again: "
                         f"{st['book_again']}. People's opinions are sticky: change these only if something this week "
                         f"actually changed your view, and only as much as it really would.")
        legs = w.describe_legs(p["id"], week)
        upcoming = [f"{t['date']} {t['from']}->{t['to']}" + ("" if t.get("booked", True) else " (not booked yet; you are thinking about it)")
                    for t in p["trips"]
                    if t["week"] and t["week"] > week and st["status"] not in STATUSES[2:]]
        parts += ["", "YOUR FLIGHTS THIS WEEK:"] + (legs or ["none"])
        if upcoming:
            parts.append("Coming up later: " + "; ".join(upcoming))
        msgs = w.messages_for(p["id"], week)
        if msgs:
            parts += ["", "MESSAGES FROM KESTREL AIR (in your app, email and texts):"] + [f'"{m}"' for m in msgs]
        perks = self.perks(p["id"], week)
        if perks:
            parts += ["What Kestrel is offering you right now: " + "; ".join(perks)]
        parts += ["", f"NEWS THAT REACHED YOU (through {', '.join(p['social_info']['hears_news_from'])}):"]
        parts += [f"- {n}" for n in w.news(week)]
        friends = [f"{self.name(f)}: \"{self.state[f]['posts'][week - 1]}\"" for f in p["circle"]
                   if f in self.state and self.state[f]["posts"].get(week - 1)]
        if friends:
            parts += ["", "WHAT PEOPLE YOU KNOW SAID LAST WEEK:"] + [f"- {x}" for x in friends]
        trending = self.trending(week - 1, exclude=p["circle"] + [p["id"]])
        if trending and sees_social(p):
            parts += ["", "POSTS GOING AROUND ON SOCIAL MEDIA:"] + [f"- \"{x}\"" for x in trending]
        parts += ["", BAU, f"If you call Kestrel this week the wait is {w.support_wait(week)}.", "",
                  "WHAT TO ANSWER: what you noticed, how you feel, what you actually do this week (actions), anything you "
                  "said to people or posted (empty if nothing), whether you complained, whether you would book Kestrel "
                  "again, how likely you are to recommend Kestrel (0-10), one diary line to remember this week, and your "
                  "status. Status means what is happening to your Kestrel travel: 'flies as planned' (your booking stands "
                  "or you flew as booked), 'rebooked' (Kestrel moved you to another Kestrel flight or date), 'moved to "
                  "another airline' (you booked a different airline instead), 'canceled the trip' (you are not making "
                  "the trip, or took a refund). Keep last week's status unless something actually changed. Be consistent: if you "
                  "book another airline your status is 'moved to another airline'; if you cancel, 'canceled the trip'; "
                  "if you change to a different date or accept a rebooking, 'rebooked'."]
        return "\n".join(parts)

    def perks(self, pid, week):
        w, out = self.world, []
        if w.has(week, "free changes", pid):
            out.append("free changes or cancellation for flights in the next two weeks")
            for t in self.world.personas[pid]["trips"]:
                if t["strike_day_at_base"] and t["week"] and t["week"] >= week:
                    alt = "Dec 21" if t["date"] == "2026-12-22" else "Dec 24"
                    out.append(f"you could move your {t['date']} {t['from']}->{t['to']} flight to {alt} at no cost "
                               f"(seats are still available that day), or cancel it for a full refund")
        if w.has(week, "goodwill", pid):
            out.append(f"goodwill: {w.has(week, 'goodwill', pid)} for your disrupted trip")
        if w.has(week, "double loyalty", pid):
            out.append("double Kestrel Club points for your disrupted trip")
        return out

    def name(self, pid):
        return next(p["name"] for p in self.all_personas if p["id"] == pid)

    def trending(self, week, exclude, k=2):
        rows = [r for r in self.weekly if r["week"] == week and r["posted_publicly"] and r["what_you_said_or_posted"]
                and r["persona"] not in exclude]
        rows.sort(key=lambda r: (r["recommend_0_to_10"], r["persona"]))   # angriest first: outrage travels
        return [r["what_you_said_or_posted"] for r in rows[:k]]

    # ------------------------------------------------------------------ one week
    def step(self, p, week):
        prompt = self.week_prompt(p, week)
        legs = [self.world.leg_outcome.get((p["id"], k)) for k, t in enumerate(p["trips"])
                if t["week"] == week and t.get("booked", True)]
        canceled = any(o and o["canceled"] for o in legs)
        prev = self.state[p["id"]]["status"]

        def mock(rng):
            status = rng.choice(["rebooked", "rebooked", "canceled the trip", "moved to another airline"]) if canceled else prev
            return {"what_you_noticed": "mock", "how_you_feel": "mock", "actions": ["wait and see"],
                    "what_you_said_or_posted": "mock post" if canceled else "", "posted_publicly": canceled,
                    "complaint": "to Kestrel" if canceled and rng.random() < 0.4 else "none",
                    "would_book_kestrel_again": rng.choice(["yes", "maybe", "no"]),
                    "recommend_0_to_10": rng.randint(3, 9), "diary": f"mock week {week}", "status": status}

        cid, ans = self.llm.json(prompt, WeekAnswer, persona=p["id"], week=week, mock=mock)
        return p, cid, ans, legs

    def apply(self, p, cid, ans, legs, week):
        st = self.state[p["id"]]
        st["status"] = ans["status"]
        st["diary"].append(f"{W.week_label(week)}: {ans['diary']}")
        if ans["what_you_said_or_posted"].strip():
            st["posts"][week] = ans["what_you_said_or_posted"].strip()[:280]
        if "change to a different date" in ans["actions"]:
            self.change_date(p, week)
        ans["recommend_0_to_10"] = max(0, min(10, int(ans["recommend_0_to_10"])))
        st["recommend"], st["book_again"] = ans["recommend_0_to_10"], ans["would_book_kestrel_again"]
        self.weekly.append({
            "persona": p["id"], "week": week, "status": ans["status"], "call": cid,
            "book_again": ans["would_book_kestrel_again"], **{k: ans[k] for k in (
                "recommend_0_to_10", "complaint", "actions", "posted_publicly", "what_you_said_or_posted",
                "what_you_noticed", "how_you_feel")},
            "flights": [o for o in legs if o], "messages_seen": len(self.world.messages_for(p["id"], week)),
            "free_change": bool(self.world.has(week, "free changes", p["id"])),
        })

    def change_date(self, p, week):
        """A persona moves an upcoming strike-day flight. Free if the offer is in force, otherwise they pay."""
        for k, t in enumerate(p["trips"]):
            if t["strike_day_at_base"] and t["week"] and t["week"] >= week and (p["id"], k) not in self.world.leg_outcome:
                new = "2026-12-21" if t["date"] == "2026-12-22" else "2026-12-24"
                t.update(date=new, strike_day_at_base=False, week=(date.fromisoformat(new) - W.CAL_START).days // 7 + 1)
                self.state[p["id"]]["moved"][k] = {"to": new, "free": bool(self.world.has(week, "free changes", p["id"]))}

    # ------------------------------------------------------------------ probes
    def ask_probe(self, p, when):
        week = 0 if when == "start" else 11
        qs = "\n".join(f"q{k}: {v.format(company='Kestrel Air')}" for k, v in QUESTIONS.items())
        ctx = ["Think about Kestrel Air as you feel today, before this winter's travel."] if when == "start" else (
            ["This winter is over. Your diary:"] + [f"- {d}" for d in self.state[p["id"]]["diary"]] +
            [f"Your final Kestrel status: {self.state[p['id']]['status']}."])
        prompt = "\n".join([PREAMBLE, "", "WHO YOU ARE", render_card(p), ""] + ctx + [
            "", "Answer each question with a whole number from 1 to 5, as this person honestly would. Read each "
            "question carefully: some are worded so that a high number is negative.", qs])
        cid, ans = self.llm.json(prompt, ProbeAnswer, persona=p["id"], week=week,
                                 mock=lambda rng: {f"q{k}": rng.randint(2, 5) for k in QUESTIONS})
        for k in QUESTIONS:
            self.probe.append({"persona": p["id"], "when": when, "question": k,
                               "score": max(1, min(5, int(ans[f"q{k}"]))), "call": cid})

    # ------------------------------------------------------------------ run
    def run(self):
        t0 = time.time()
        pool = ThreadPoolExecutor(self.a.workers)
        probe = self.a.name in ("plan_1", "nodecision_1") or self.a.probe
        if probe:
            list(pool.map(lambda p: self.ask_probe(p, "start"), self.personas))
        for week in range(1, self.a.weeks + 1):
            self.world.fix_targets(week, self.state)
            self.world.operate_week(week)
            for p in self.personas:  # resolve this week's flights before anyone decides
                for k, t in enumerate(p["trips"]):
                    if t["week"] == week:
                        self.world.resolve_leg(p["id"], k, t, week)
            for p, cid, ans, legs in pool.map(lambda p: self.step(p, week), self.personas):
                self.apply(p, cid, ans, legs, week)
            print(f"  {self.a.name} {W.week_label(week)} done ({time.time() - t0:.0f}s, {len(self.llm.calls)} calls)",
                  flush=True)
        if probe:
            list(pool.map(lambda p: self.ask_probe(p, "end"), self.personas))
        self.write()
        print(f"{self.a.name}: {len(self.llm.calls)} calls in {time.time() - t0:.0f}s -> {self.out}")

    def write(self):
        import metrics
        self.out = ROOT / self.a.out / self.a.name
        self.out.mkdir(parents=True, exist_ok=True)
        decs = [{k: v for k, v in d.items() if k != "target_rule"} for d in self.decisions]
        run = {"company": "kestrel", "type": self.a.type, "seed": self.a.seed, "model": self.llm.model,
               "decisions": decs, "cost_musd": self.cost,
               "targeting": {str(i + 1): {"rule": d["target_rule"], "personas": sorted(self.world.targets.get(i, []))}
                             for i, d in enumerate(self.decisions)},
               "crises": [c["id"] for c in self.crises]}
        (self.out / "run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False))
        (self.out / "personas.jsonl").write_bytes(self.personas_file.read_bytes())
        for name, rows in (("calls", self.llm.calls), ("weekly", self.weekly), ("probe", self.probe)):
            if name == "probe" and not rows:
                continue
            with open(self.out / f"{name}.jsonl", "w", encoding="utf-8") as f:
                f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
        m = metrics.compute(self.all_personas, self.personas, self.weekly, self.world, self.probe)
        (self.out / "metrics.json").write_text(json.dumps(m, indent=2, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--type", required=True, choices=["plan", "nodecision", "plan_nosurprises"])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--decisions")
    ap.add_argument("--out", default="runs")
    ap.add_argument("--weeks", type=int, default=10)
    ap.add_argument("--personas", default="")
    ap.add_argument("--personas-file", default="data/personas.jsonl")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--probe", action="store_true", help="ask the check-in questions in any run")
    ap.add_argument("--mock", action="store_true")
    Sim(ap.parse_args()).run()


if __name__ == "__main__":
    main()
