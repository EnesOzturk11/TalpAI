"""Turn saved runs into board metrics, group distributions with 95% Wilson intervals, and a decision brief."""
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

RUNS = Path(__file__).resolve().parent.parent / "runs"
WORLD = Path(__file__).resolve().parent / "world.json"
STATUSES = ["flies as planned", "rebooked", "moved to another airline", "canceled the trip"]
LOST = {"moved to another airline", "canceled the trip"}
COMPLAINTS = {"complain in the app", "complain to the DOT", "dispute the charge"}
REVERSED = {"2b", "4b"}  # worded the other way round; 'aligned' = 6 - score


def wilson(k, n, z=1.96):
    """Share k/n with a 95% Wilson interval; safe for small n and 0 or n successes."""
    if n == 0:
        return [None, None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(p, 3), round(max(0.0, c - h), 3), round(min(1.0, c + h), 3)]


def persona_weights(personas, mix):
    """Share of real Kestrel passengers each persona stands for (sums to 1): its group's share in
    world.json customer_mix, split evenly over that group's personas, renormalized over the groups
    present, so a 10-persona test set still represents the whole customer base."""
    mix = {g: v for g, v in mix.items() if not g.startswith("_")}
    count = Counter(p["group"] for p in personas)
    missing = sorted(set(count) - set(mix))
    if missing:
        raise ValueError(f"world.json customer_mix has no share for: {', '.join(missing)}")
    total = sum(mix[g] for g in count)
    return {p["id"]: mix[p["group"]] / count[p["group"]] / total for p in personas}


def wshare(sel, ids, w):
    """Weighted share of sel among ids, 95% Wilson interval on the effective sample size (Kish n_eff).
    Equal weights give exactly the unweighted k/n interval."""
    tot = sum(w[i] for i in ids)
    if not tot:
        return [None, None, None]
    n_eff = tot ** 2 / sum(w[i] ** 2 for i in ids)
    return wilson(sum(w[i] for i in sel) / tot * n_eff, n_eff)


def mix_of(run):
    """The customer mix a run was made with (saved in run.json), else today's world.json."""
    return run.get("customer_mix") or json.loads(WORLD.read_text("utf-8"))["customer_mix"]


def complaint_share(personas, weekly, mix, weeks):
    """Weighted share of passengers who complain in an average week of `weeks`."""
    w = persona_weights(personas, mix)
    return sum(w[r["persona"]] for r in weekly if r["week"] in weeks and COMPLAINTS & set(r.get("actions", []))) / len(weeks)


def run_metrics(personas, weekly, probe, world):
    w = persona_weights(personas, world["customer_mix"])
    fares = world["fares"]
    route = {p["id"]: p.get("route", "domestic") for p in personas}

    trips = [r for r in weekly if r.get("trip")]
    normal = [r for r in trips if not r["trip"]["strike_day"]]
    flown_w = sum(w[r["persona"]] for r in normal if r["trip"]["outcome"] != "canceled")
    goal_1 = 100 * flown_w / (sum(w[r["persona"]] for r in normal) or 1)

    hit = [r for r in trips if r["trip"]["outcome"] in ("canceled", "delayed over 3 hours")]
    goal_2 = 100 * sum(w[r["persona"]] for r in hit if r["trip"]["rebook24"]) / sum(w[r["persona"]] for r in hit) if hit else 100.0

    # complaints: plain weekly share. Scaling to the dossier's 2,500/month needs a pre-strike baseline the personas
    # do not give (near zero), so any scale-up explodes; compare runs on the share instead.
    goal_3 = 100 * complaint_share(personas, weekly, world["customer_mix"], range(1, 11))

    end3a = {r["persona"]: r["score"] for r in probe if r["when"] == "end" and r["question"] == "3a"}
    if end3a:
        prom = sum(w[i] for i, s in end3a.items() if s == 5)
        det = sum(w[i] for i, s in end3a.items() if s <= 3)
        goal_3b = 100 * (prom - det) / (sum(w[i] for i in end3a) or 1)
    else:  # no probe in this run: fall back to week-10 'book again'
        last = {r["persona"]: r["book_again"] for r in weekly if r["week"] == 10}
        goal_3b = 100 * (sum(w[i] for i, b in last.items() if b == "yes") -
                         sum(w[i] for i, b in last.items() if b == "no")) / (sum(w[i] for i in last) or 1)

    late = [r for r in trips if 5 <= r["week"] <= 10]
    plan_rev = sum(w[r["persona"]] * fares[route[r["persona"]]] for r in late)
    # kept: still on Kestrel, and a canceled flight only counts if the persona was rebooked (else refunded)
    kept = sum(w[r["persona"]] * fares[route[r["persona"]]] for r in late
               if r["status"] not in LOST and (r["trip"]["outcome"] != "canceled" or r["status"] == "rebooked"))
    goal_4 = 100 * kept / plan_rev if plan_rev else 100.0

    return {
        "goal_1": round(goal_1, 2), "goal_2": round(goal_2, 2), "goal_3": round(goal_3, 2),
        "goal_3b": round(goal_3b, 1), "goal_4": round(goal_4, 2),
        "units": {
            "goal_1": "% of persona flights operated, strike days excluded (target >= 98). Driven by world.json "
                      "assumptions (action_effects), not persona behaviour",
            "goal_2": "% of canceled or 3h+ delayed persona flights rebooked or refunded within 24h (target >= 90; 100 if "
                      "none). Driven by world.json assumptions (action_effects), not persona behaviour",
            "goal_3": "% of passengers (weighted) who complain (app, DOT, card dispute) in an average week, weeks 1-10",
            "goal_3b": "NPS proxy from end check-in 3a: % 5s minus % 1-3s. Personas are not calibrated to the +12 "
                       "baseline: read it as a difference from nodecision, not as a level",
            "goal_4": "% of planned fare revenue weeks 5-10 kept on Kestrel by personas with a flight then (target >= 96)",
        },
        "note": "weighted by world.json customer_mix (team assumption); persona counts are small, read with the dashboard's intervals",
    }


def load_run(name):
    d = RUNS / name

    def jl(f):
        p = d / f
        return [json.loads(x) for x in p.read_text("utf-8").split("\n") if x.strip()] if p.exists() else []
    return {"name": name, "run": json.loads((d / "run.json").read_text("utf-8")),
            "metrics": json.loads((d / "metrics.json").read_text("utf-8")) if (d / "metrics.json").exists() else {},
            "personas": jl("personas.jsonl"), "weekly": jl("weekly.jsonl"), "probe": jl("probe.jsonl"),
            "chats": jl("chats.jsonl")}


def dist(rows, key, options, w):
    ids = [x["persona"] for x in rows]
    return {"n": len(rows), **{o: wshare([x["persona"] for x in rows if x[key] == o], ids, w) for o in options}}


def summarize_run(r, w):
    group = {p["id"]: p["group"] for p in r["personas"]}
    groups = sorted(set(group.values()))
    weekly = r["weekly"]
    by_g = lambda rows, g: [x for x in rows if group[x["persona"]] == g]
    w10 = [x for x in weekly if x["week"] == 10]
    ever_lost = {x["persona"] for x in weekly if x["status"] in LOST}

    out = {"name": r["name"], "type": r["run"]["type"], "seed": r["run"]["seed"], "metrics": r["metrics"],
           "groups": {}, "weekly": {}}
    for wk in range(1, 11):
        out["weekly"][wk] = dist([x for x in weekly if x["week"] == wk], "status", STATUSES, w)

    start = {(x["persona"], x["question"]): x["score"] for x in r["probe"] if x["when"] == "start"}
    for g in groups + ["ALL"]:
        ids = [i for i, gg in group.items() if g in ("ALL", gg)]
        rows = weekly if g == "ALL" else by_g(weekly, g)
        last = w10 if g == "ALL" else by_g(w10, g)
        acts = Counter(a for x in rows for a in x.get("actions", []))
        disrupted = [x for x in rows if x.get("trip") and x["trip"]["outcome"] != "on time"]
        probe = defaultdict(lambda: {"start": [], "end": []})
        for x in r["probe"]:
            if x["persona"] in ids:
                s = 6 - x["score"] if x["question"] in REVERSED else x["score"]
                probe[x["question"]][x["when"]].append((s, w[x["persona"]]))
        said_stay = [i for i in ids if start.get((i, "2a"), 0) >= 4]
        out["groups"][g] = {
            "n": len(ids),
            "weight": round(sum(w[i] for i in ids), 3),
            "status_week10": dist(last, "status", STATUSES, w),
            "ever_lost": wshare(ever_lost & set(ids), ids, w),
            "book_again_week10": dist(last, "book_again", ["yes", "maybe", "no"], w),
            "blame_when_disrupted": dict(Counter(x.get("blame") for x in disrupted)),
            "actions_per_persona_week": {a: round(c / max(1, len(rows)), 3) for a, c in acts.most_common(8)},
            "probe_aligned_mean": {q: {k: round(sum(s * x for s, x in v) / sum(x for _, x in v), 2) if v else None
                                       for k, v in se.items()}
                                   for q, se in sorted(probe.items())},
            # talp's say-do gap: said 'likely to stay' (2a >= 4) at the start, then left in the run
            "say_do_gap": {"said_stay": len(said_stay),
                           "then_left": wshare(set(said_stay) & ever_lost, said_stay, w)},
        }
    return out


TREND_METRICS = [
    ("satisfaction", "Satisfaction index", "book again: yes = 100, maybe = 50, no = 0; weighted mean"),
    ("moved", "Moved to another airline", "% of passengers (weighted) with this status in the week"),
    ("canceled", "Canceled the trip", "% of passengers (weighted) with this status in the week"),
    ("rebooked", "Rebooked on Kestrel", "% of passengers (weighted) with this status in the week"),
    ("complained", "Complained", "% of passengers (weighted) who complained in the app, to the DOT or disputed the charge"),
    ("blame_kestrel", "Blames Kestrel Air", "% of passengers (weighted) who hold Kestrel responsible this week"),
]
BOOK_SCORE = {"yes": 100, "maybe": 50, "no": 0}


def decision_label(run):
    """One line per decision: runs with the same decisions (any seed) share a label and are averaged."""
    if run["type"] == "nodecision":
        return "nodecision"
    label = run.get("decision_set") or "decisions.json"
    return label + " (no surprises)" if run["type"] == "plan_nosurprises" else label


def week_values(rows, w):
    n = sum(w[x["persona"]] for x in rows) or 1
    share = lambda f: 100 * sum(w[x["persona"]] for x in rows if f(x)) / n
    return {"satisfaction": sum(w[x["persona"]] * BOOK_SCORE.get(x["book_again"], 0) for x in rows) / n,
            "moved": share(lambda x: x["status"] == "moved to another airline"),
            "canceled": share(lambda x: x["status"] == "canceled the trip"),
            "rebooked": share(lambda x: x["status"] == "rebooked"),
            "complained": share(lambda x: COMPLAINTS & set(x.get("actions", []))),
            "blame_kestrel": share(lambda x: x.get("blame") == "kestrel air")}


def trends(loaded):
    """{label: {runs, series: {metric: [week 1..10]}}}: mean over the runs (seeds) of each decision."""
    by = defaultdict(list)
    for r in loaded:
        by[decision_label(r["run"])].append(r)
    lines = {}
    for label, rs in by.items():
        per_run = [[week_values([x for x in r["weekly"] if x["week"] == wk], r["w"]) for wk in range(1, 11)] for r in rs]
        lines[label] = {"runs": [r["name"] for r in rs],
                        "series": {m: [round(sum(pr[wk][m] for pr in per_run) / len(per_run), 1) for wk in range(10)]
                                   for m, _, _ in TREND_METRICS}}
    return {"metrics": [{"key": k, "title": t, "note": n} for k, t, n in TREND_METRICS], "lines": lines}


def lost_any(personas, weekly, mix):
    w = persona_weights(personas, mix)
    lost = {x["persona"] for x in weekly if x["status"] in LOST}
    return 100 * sum(w[i] for i in lost)


def blame_share(personas, weekly, mix, weeks):
    w = persona_weights(personas, mix)
    return 100 * sum(w[x["persona"]] for x in weekly if x["week"] in weeks and x.get("blame") == "kestrel air") / len(weeks)


BOOT_KEYS = ("goal_4", "goal_3b", "goal_3", "lost_any")


def boot_ci(rs, world, B=500, seed=0):
    """95% bootstrap interval of the seed-mean of each BOOT_KEYS metric: personas resampled with replacement within
    each group (group sizes kept, so the customer-mix weights stay valid); one draw is shared by all seeds."""
    groups = defaultdict(list)
    for p in sorted(rs[0]["personas"], key=lambda p: p["id"]):
        groups[p["group"]].append(p["id"])
    rng, out = random.Random(seed), {k: [] for k in BOOT_KEYS}
    by_id = [({p["id"]: p for p in r["personas"]}, defaultdict(list), defaultdict(list)) for r in rs]
    for (_, wk, pr), r in zip(by_id, rs):
        for x in r["weekly"]:
            wk[x["persona"]].append(x)
        for x in r["probe"]:
            pr[x["persona"]].append(x)
    for _ in range(B):
        draw = [(i, f"{i}#{j}") for g in groups.values() for j, i in enumerate(rng.choices(g, k=len(g)))]
        vals = {k: [] for k in BOOT_KEYS}
        for (pp, wk, pr), r in zip(by_id, rs):
            ps = [pp[i] | {"id": n} for i, n in draw]
            weekly = [x | {"persona": n} for i, n in draw for x in wk[i]]
            probe = [x | {"persona": n} for i, n in draw for x in pr[i]]
            mix = mix_of(r["run"])
            m = run_metrics(ps, weekly, probe, world | {"customer_mix": mix})
            m["lost_any"] = lost_any(ps, weekly, mix)
            for k in BOOT_KEYS:
                vals[k].append(m[k])
        for k in BOOT_KEYS:
            out[k].append(sum(vals[k]) / len(vals[k]))
    return {k: [round(sorted(v)[int(0.025 * B)], 2), round(sorted(v)[int(0.975 * B) - 1], 2)] for k, v in out.items()}


def summarize(names, boot=True):
    loaded = [load_run(n) for n in names]
    world = json.loads(WORLD.read_text("utf-8"))
    for r in loaded:  # weights and board metrics recomputed with the run's own customer mix
        r["w"] = persona_weights(r["personas"], mix_of(r["run"]))
        r["metrics"] = run_metrics(r["personas"], r["weekly"], r["probe"], world | {"customer_mix": mix_of(r["run"])})
        r["metrics"]["lost_any"] = round(lost_any(r["personas"], r["weekly"], mix_of(r["run"])), 2)
        r["metrics"]["blame_8_10"] = round(blame_share(r["personas"], r["weekly"], mix_of(r["run"]), range(8, 11)), 2)
    runs = [summarize_run(r, r["w"]) for r in loaded]
    by_type, by_runs = defaultdict(list), defaultdict(list)  # keyed by decision, like the trend lines
    for r, s in zip(loaded, runs):
        by_type[decision_label(r["run"])].append(s["metrics"])
        by_runs[decision_label(r["run"])].append(r)
    keys = ["goal_1", "goal_2", "goal_3", "goal_3b", "goal_4", "lost_any", "blame_8_10"]
    compare = {t: {k: {"mean": round(sum(m.get(k, 0) for m in ms) / len(ms), 2),
                       "min": min(m.get(k, 0) for m in ms), "max": max(m.get(k, 0) for m in ms)}
                   for k in keys} | {"runs": len(ms)} for t, ms in by_type.items()}
    if boot:
        for t, rs in by_runs.items():
            compare[t]["boot"] = boot_ci(rs, world)
    # NPS proxy and revenue are read as differences from the no-decision runs, not as levels
    if "nodecision" in compare:
        for t, c in compare.items():
            if t != "nodecision":
                c["delta"] = {k: round(c[k]["mean"] - compare["nodecision"][k]["mean"], 2) for k in ("goal_3b", "goal_4")}
    return {"runs": runs, "compare": compare, "trends": trends(loaded)}


def brief_md(summary):
    """Markdown decision brief from summarize(): paste into CLIENT_MEMO / TEAM_DOC and edit."""
    pct = lambda w: "-" if w[0] is None else f"{w[0]*100:.0f}% [{w[1]*100:.0f}-{w[2]*100:.0f}]"
    L = ["# Decision brief (generated; numbers are simulation output, not measurements)", "",
         "## Board goals by decision (mean, min-max over seeds)", "",
         "| decision | runs | goal_1* | goal_2* | goal_3 % complaining/wk [boot] | goal_3b [boot] | Δ goal_3b | goal_4 [boot] | Δ goal_4 | lost any week % [boot] | blame Kestrel wk8-10 % |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for t, c in summary["compare"].items():
        cell = lambda k: f"{c[k]['mean']} ({c[k]['min']}-{c[k]['max']})"
        bc = lambda k: f"{c[k]['mean']} [{c['boot'][k][0]}-{c['boot'][k][1]}]" if "boot" in c else cell(k)
        dl = lambda k: f"{c['delta'][k]:+.2f}" if "delta" in c else "–"
        L.append(f"| {t} | {c['runs']} | {cell('goal_1')} | {cell('goal_2')} | {bc('goal_3')} | {bc('goal_3b')} | "
                 f"{dl('goal_3b')} | {bc('goal_4')} | {dl('goal_4')} | {bc('lost_any')} | {c['blame_8_10']['mean']} |")
    L += ["", "Mean over seeds; [boot] = 95% bootstrap interval of that mean (500 draws, personas resampled within groups). "
              "*goal_1 and goal_2 are driven by world.json assumptions (action_effects), not persona behaviour: "
              "do not present them as simulation output. goal_3b is not calibrated to the +12 baseline: read the Δ."]
    for s in summary["runs"]:
        L += ["", f"## {s['name']} ({s['type']}, seed {s['seed']})", "",
              "| group | n | lost at any week | week 10: flies / rebooked / moved / canceled | book again: yes / no | said stay, then left |",
              "|---|---|---|---|---|---|"]
        for g, d in s["groups"].items():
            st = d["status_week10"]
            ba = d["book_again_week10"]
            sd = d["say_do_gap"]
            L.append(f"| {g} | {d['n']} | {pct(d['ever_lost'])} | " +
                     " / ".join(pct(st[x]) for x in STATUSES) +
                     f" | {pct(ba['yes'])} / {pct(ba['no'])} | {pct(sd['then_left'])} of {sd['said_stay']} |")
    L += ["", "Shares are weighted by world.json customer_mix (team assumption). Brackets: 95% Wilson interval on the "
              "effective sample size. With few personas per group, intervals are wide: treat group differences as "
              "hypotheses unless they hold across seeds."]
    return "\n".join(L)


if __name__ == "__main__":
    import sys
    print(brief_md(summarize(sys.argv[1:])))
