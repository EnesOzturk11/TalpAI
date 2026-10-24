"""World model: calendar, decision menu, crises, flight outcomes, news, fleet-level operations.

Code decides what happens to flights (dice with the run's seed); the LLM decides what people do about it.
Every number marked ASSUMPTION is ours and is listed in TEAM_DOC.md.
"""
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAL_START = date(2026, 11, 2)
STRIKE_DAYS = {date(2026, 12, 22), date(2026, 12, 23)}
BASES = {"MCO", "PHL"}
BUDGET_M = 3.0

# Decision menu (dossier), CFO cost in $M per level. scope: "ops" applies to the whole operation,
# "passenger" only to the decision's target. weeks: how long it stays in force from the decision week.
MENU = {
    "lease an aircraft with crew for 2 weeks": dict(levels={"1 aircraft": 0.7, "2 aircraft": 1.4}, scope="ops", weeks=2),
    "backup ground handling contract at both bases for the strike days": dict(levels={"on": 0.5}, scope="ops", weeks=10),
    "free changes and cancellations for bookings in a 2-week window": dict(levels={"on": 0.2}, scope="passenger", weeks=2),
    "goodwill for affected passengers, up to 10,000 passengers": dict(
        levels={"a $75 travel credit": 0.3, "$50 cash": 0.5}, scope="passenger", weeks=10),
    "rebooking deal with a partner airline for 2 disrupted weeks": dict(levels={"on": 0.25}, scope="ops", weeks=2),
    "hotel rooms held for stranded passengers, whatever the cause": dict(levels={"on": 0.2}, scope="ops", weeks=2),
    "extra airport and call-center staff for 2 weeks": dict(levels={"on": 0.15}, scope="ops", weeks=2),
    "fare cap on the busiest routes for 2 weeks": dict(levels={"on": 0.5}, scope="ops", weeks=2),
    "fare sale on quiet routes for 2 weeks": dict(levels={"on": 0.3}, scope="ops", weeks=2),
    "double loyalty points for affected passengers": dict(levels={"on": 0.1}, scope="passenger", weeks=10),
    "merge low-load flights, announced at least 7 days ahead": dict(levels={"on": -0.25}, scope="ops", weeks=2),
}

# ASSUMPTIONS for fleet-level operations
FLIGHTS_PER_DAY = 188          # 210,000 pax/week / 86% load / ~186 seats / 7 days
BASE_SHARE = 0.6               # "6 in 10 Kestrel flights start or end in Orlando or Philadelphia" (dossier)
BASELINE_CANCEL = 0.008        # normal cancellation rate on an ordinary day
MERGE_SHARE = 0.03             # share of flights merged away while that action is in force
SIM_CANCEL_MIN = 0.6           # importance sampling floor for cancellations on crisis days (not an assumption about reality)


def week_start(w):
    return CAL_START + timedelta(days=7 * (w - 1))


def week_label(w):
    s = week_start(w)
    e = s + timedelta(days=6)
    return f"week {w} ({s:%b} {s.day} - {e:%b} {e.day})"


def norm_action(a):
    return " ".join(a.lower().split())


def load_decisions(path):
    decs = json.loads(Path(path).read_text())["decisions"]
    total = 0.0
    for d in decs:
        assert 1 <= d["week"] <= 10 and 1 <= len(d["actions"]) <= 3, d
        assert len(d["message"]) <= 600, f"message is {len(d['message'])} characters (max 600)"
        for a in d["actions"]:
            item = MENU[norm_action(a["action"])]
            total += item["levels"][a["level"]]
    assert len(decs) in (0, 2), "exactly two decisions (or none)"
    budget = BUDGET_M + sum(0.25 for d in decs for a in d["actions"] if norm_action(a["action"]).startswith("merge"))
    assert total <= budget + 1e-9, f"decisions cost ${total:.2f}M, budget ${budget:.2f}M"
    return decs, round(total, 2)


def load_crises(surprises=True):
    cs = json.loads((ROOT / "config" / "crises.json").read_text())["crises"]
    return [c for c in cs if surprises or c["kind"] == "known"]


class World:
    def __init__(self, personas, decisions, crises, seed):
        self.personas = {p["id"]: p for p in personas}
        self.decisions, self.crises, self.seed = decisions, crises, seed
        self.targets = {}         # decision index -> set of persona ids, fixed when its week starts
        self.leg_outcome = {}     # (persona, leg index) -> outcome dict
        self.weekly_stats = {}

    # ---------------------------------------------------------------- decisions
    def actions_in_force(self, week):
        out = []
        for i, d in enumerate(self.decisions):
            for a in d["actions"]:
                item = MENU[norm_action(a["action"])]
                if d["week"] <= week < d["week"] + item["weeks"]:
                    out.append((i, norm_action(a["action"]), a["level"], item["scope"]))
        return out

    def has(self, week, prefix, persona=None):
        for i, name, level, scope in self.actions_in_force(week):
            if name.startswith(prefix) and (scope == "ops" or persona is None or persona in self.targets.get(i, ())):
                return level
        return None

    def fix_targets(self, week, state):
        for i, d in enumerate(self.decisions):
            if d["week"] == week and i not in self.targets:
                self.targets[i] = {pid for pid in self.personas if self._matches(d["target_rule"], pid, week, state)}

    def _matches(self, rule, pid, week, state):
        legs = [(k, t) for k, t in enumerate(self.personas[pid]["trips"]) if t["week"]]
        if rule == "all":
            return True
        if rule == "week8_base":
            return any(t["week"] == 8 and t["touches_base"] for _, t in legs)
        if rule == "strike_exposed":
            return any(t["strike_day_at_base"] for _, t in legs)
        if rule == "affected":  # disrupted in the strike week (week 8)
            return any((o := self.leg_outcome.get((pid, k))) and o["disrupted"] and t["week"] == 8 for k, t in legs)
        if rule == "upcoming_travelers":
            return any(t["week"] >= week for _, t in legs)
        raise ValueError(f"unknown target_rule {rule}")

    def messages_for(self, pid, week):
        """Decision messages this persona has received, word for word, from the decision's week on."""
        return [d["message"] for i, d in enumerate(self.decisions)
                if d["week"] <= week and pid in self.targets.get(i, ())]

    # ---------------------------------------------------------------- crises
    def effects_on(self, day, airport_pair):
        out = []
        for c in self.crises:
            for e in c["effects"]:
                if day.isoformat() in e["dates"] and (e["bases"] == "all" or set(e["bases"]) & set(airport_pair)):
                    out.append(e)
        return out

    def _mitigation(self, e, week):
        m = 1.0
        for name, factor in e.get("mitigated_by", {}).items():
            if self.has(week, name):
                m *= factor
        return m

    def news(self, week):
        items = []
        for c in self.crises:
            if c["announced_week"] == week:
                items.append(f"NEW: {c['text']}")
            elif c["announced_week"] < week and any(
                    date.fromisoformat(d) >= week_start(week) for e in c["effects"] for d in e["dates"]):
                items.append(f"Still expected: {c['title']}.")
            for u in c.get("updates", []):
                if u["week"] == week:
                    items.append(f"UPDATE on {c['title']}: {u['text']}")
        last = self.weekly_stats.get(week - 1)
        if last and last["disrupted_flights"] > 0:
            items.append(f"Reported last week: about {last['canceled_pct']:.0f}% of Kestrel Air flights were canceled on the "
                         f"worst day and many others ran hours late; local TV showed long lines and piles of bags.")
        return items or ["Nothing in the news about Kestrel Air this week."]

    # ---------------------------------------------------------------- flights
    def resolve_leg(self, pid, k, leg, week, free_change_moved=False):
        """Decide what happens to one leg. Deterministic for a given seed."""
        if (pid, k) in self.leg_outcome:
            return self.leg_outcome[(pid, k)]
        rng = random.Random(f"{self.seed}|{pid}|{k}")
        day = date.fromisoformat(leg["date"])
        effects = self.effects_on(day, (leg["from"], leg["to"]))
        cancel_p, delay_h, bags, assist, cause = BASELINE_CANCEL, 0, False, False, None
        for e in effects:
            m = self._mitigation(e, week)
            cancel_p = max(cancel_p, e["cancel_rate"] * m)
            delay_h = max(delay_h, e["delay_hours"] * (0.5 if m < 1 else 1))
            bags, assist, cause = bags or (e["bags"] and m == 1), assist or (e["assistance"] and m == 1), e["cause"]
        if self.has(week, "lease an aircraft"):
            cancel_p *= 0.8
        # Importance sampling: on crisis days we draw cancellations at least SIM_CANCEL_MIN of the time, so enough
        # personas live through a cancellation; metrics reweight each leg by true/simulated probability.
        q = max(cancel_p, SIM_CANCEL_MIN) if effects else cancel_p
        canceled = rng.random() < q
        iw = (cancel_p / q) if canceled else ((1 - cancel_p) / (1 - q))
        delayed = 0 if canceled else (delay_h if effects and rng.random() < 0.7 else 0)
        o = {"date": leg["date"], "from": leg["from"], "to": leg["to"], "canceled": canceled, "delay_hours": delayed,
             "bag_delayed": bool(effects) and bags and not canceled and rng.random() < 0.5,
             "assistance_slow": bool(effects) and assist, "cause": cause or "a mechanical problem with the aircraft",
             "disrupted": canceled or delayed >= 3, "moved_by_free_change": free_change_moved,
             "true_cancel_p": round(cancel_p, 4), "sim_cancel_p": round(q, 4), "iw": round(iw, 4)}
        if canceled:
            p24 = (0.25 if leg["week"] == 8 else 0.8)                      # own spare seats (97% booked in week 8)
            p24 += 0.5 if self.has(week, "rebooking deal") else 0
            p24 += 0.2 * bool(self.has(week, "lease an aircraft")) + 0.1 * bool(self.has(week, "extra airport"))
            o["rebook_within_24h"] = rng.random() < min(0.95, p24)
            o["rebook_offer"] = ("a seat on the next Kestrel flight with room, within 24 hours" if o["rebook_within_24h"]
                                 else "the next Kestrel flight with a free seat, about 3 days later")
            if o["rebook_within_24h"] and self.has(week, "rebooking deal"):
                o["rebook_offer"] = "a seat on a partner airline the same day"
        self.leg_outcome[(pid, k)] = o
        return o

    def describe_legs(self, pid, week):
        """Text for the persona prompt: this week's flights and what happened."""
        lines = []
        for k, leg in enumerate(self.personas[pid]["trips"]):
            if leg["week"] != week:
                continue
            o = self.resolve_leg(pid, k, leg, week)
            s = f"{leg['date']} {leg['from']}->{leg['to']} (party of {leg['party']}): "
            if not leg.get("booked", True):
                lines.append(s + "you had been thinking about booking this but have not bought it yet. Decide now "
                             "whether to book it on Kestrel, book another airline, or not travel.")
                continue
            if o["canceled"]:
                s += (f"CANCELED ({o['cause']}). Kestrel offered {o['rebook_offer']}, or a full refund (required by DOT rules).")
                if self.has(week, "hotel rooms"):
                    s += " Kestrel is holding hotel rooms for stranded passengers."
            elif o["delay_hours"]:
                s += f"left about {o['delay_hours']:.0f} hours late ({o['cause']})."
            else:
                s += "flew on time."
            if o["bag_delayed"]:
                s += " Checked bags arrived a day late."
            if o["assistance_slow"] and "no" != self.personas[pid]["sector"]["needs_help_at_airport"][:2].lower():
                s += " Wheelchair and escort help took over an hour."
            lines.append(s)
        return lines

    def support_wait(self, week):
        disrupted = any(self.effects_on(week_start(week) + timedelta(days=i), tuple(BASES)) for i in range(7))
        if not disrupted:
            return "about 9 minutes"
        return "about 25 minutes" if self.has(week, "extra airport") else "over an hour"

    # ---------------------------------------------------------------- fleet level (goal 1)
    def operate_week(self, week):
        planned = canceled = 0.0
        worst = 0.0
        disrupted_flights = 0.0
        for i in range(7):
            day = week_start(week) + timedelta(days=i)
            rate_base = BASELINE_CANCEL
            for e in self.effects_on(day, tuple(BASES)):
                rate_base = max(rate_base, e["cancel_rate"] * self._mitigation(e, week))
            if self.has(week, "lease an aircraft"):
                rate_base *= 0.8
            rate = BASE_SHARE * rate_base + (1 - BASE_SHARE) * BASELINE_CANCEL
            merged = MERGE_SHARE if self.has(week, "merge low-load") else 0
            day_cancel = FLIGHTS_PER_DAY * min(1, rate + merged)
            worst = max(worst, 100 * day_cancel / FLIGHTS_PER_DAY)
            if rate_base > BASELINE_CANCEL:
                disrupted_flights += FLIGHTS_PER_DAY * BASE_SHARE
            if day not in STRIKE_DAYS:  # goal 1 leaves the strike days out
                planned += FLIGHTS_PER_DAY
                canceled += day_cancel
        self.weekly_stats[week] = {"planned_ex_strike": planned, "canceled_ex_strike": canceled,
                                   "canceled_pct": worst, "disrupted_flights": disrupted_flights}
        return self.weekly_stats[week]
