"""Compare single-action runs against the no-decision base: python compare_actions.py [base] [prefix]
Writes lab/EXPERIMENT_single_actions.md and prints it. All shares are weighted by world.json customer_mix."""
import sys

import sim
import stats

args = sys.argv[1:]
base, prefix = (args[0] if args else "x_base"), (args[1] if len(args) > 1 else "x_")
names = [base] + sorted(d.name for d in stats.RUNS.iterdir()
                        if d.name.startswith(prefix) and d.name != base and (d / "run.json").exists())
summary = stats.summarize(names)
world = sim.load("world.json")
costs = world["costs"]


def row(r, s):
    run, a = r["run"], (r["run"]["decisions"] or [{"week": "-", "actions": [{"action": "(none)", "level": ""}]}])[0]
    act = a["actions"][0]
    tr = summary["trends"]["lines"][stats.decision_label(run)]["series"]
    w8 = [x for x in r["weekly"] if x["week"] == 8 and x["trip"]]
    hit = [x for x in w8 if x["trip"]["outcome"] in ("canceled", "delayed over 3 hours")]
    g = s["groups"]["ALL"]
    return {"run": r["name"], "action": act["action"], "level": act["level"], "week": a["week"],
            "cost": costs.get(act["action"], {}).get(act["level"], 0) if run["decisions"] else 0,
            "lost": g["ever_lost"][0] * 100, "lost_ci": g["ever_lost"][1:],
            "again_no": g["book_again_week10"]["no"][0] * 100,
            "sat8": tr["satisfaction"][7], "sat10": tr["satisfaction"][9], "blame8": tr["blame_kestrel"][7],
            "hit": len(hit), "stranded": sum(not x["trip"]["rebook24"] for x in hit), "w8": len(w8),
            **{k: s["metrics"][k] for k in ("goal_2", "goal_3b", "goal_4")}}


loaded = {r["name"]: r for r in (stats.load_run(n) for n in names)}
rows = [row(loaded[s["name"]], s) for s in summary["runs"]]
b = rows[0]
SHORT = {"Backup ground handling contract at both bases for the strike days": "backup ground handling",
         "Rebooking deal with a partner airline for 2 disrupted weeks": "partner airline",
         "Extra airport and call-center staff for 2 weeks": "extra staff",
         "Hotel rooms held for stranded passengers, whatever the cause": "hotel rooms",
         "Free changes and cancellations for bookings in a 2-week window": "free changes",
         "Goodwill for affected passengers, up to 10,000 passengers": "goodwill"}
d = lambda x, k: f"{x[k] - b[k]:+.1f}" if x is not b else "–"

L = ["# Single-action experiments (simulation output, not measurements)", "",
     f"Runs: {', '.join(names)} · seed {loaded[base]['run']['seed']} · {len(loaded[base]['personas'])} personas · "
     f"model {loaded[base]['run']['model']} · weighted by world.json customer_mix (team assumption).",
     "Same seed in every run, so each run faces the same dice; differences come from the action and the model.", "",
     "| action | week | cost $M | week-8 flights hit / stranded | lost at any week % (Δ) | book again 'no' wk10 % (Δ) | satisfaction wk8 → wk10 (Δ wk10) | blame Kestrel wk8 % (Δ) | rebooked ≤24h % | NPS proxy | revenue wk5-10 % |",
     "|---|---|---|---|---|---|---|---|---|---|---|"]
for x in sorted(rows, key=lambda x: (x is not b, x["lost"], x["again_no"], -x["sat10"])):
    name = "**no decision (base)**" if x is b else f"{SHORT.get(x['action'], x['action'])} {x['level'] if x['level'] != 'on' else ''}".strip()
    L.append(f"| {name} | {x['week']} | {x['cost']} | {x['hit']}/{x['w8']} · {x['stranded']} | {x['lost']:.1f} ({d(x, 'lost')}) | "
             f"{x['again_no']:.1f} ({d(x, 'again_no')}) | {x['sat8']} → {x['sat10']} ({d(x, 'sat10')}) | "
             f"{x['blame8']} ({d(x, 'blame8')}) | {x['goal_2']} | {x['goal_3b']} | {x['goal_4']} |")
L += ["", "Sorted by fewest passengers lost. Δ = difference from the no-decision base (percentage points). "
      "'hit' = week-8 flights canceled or 3h+ late; 'stranded' = of those, no new seat within 24h.",
      f"With {len(loaded[base]['personas'])} personas and one seed, a few personas move these numbers: "
      f"'lost' interval for the base is {b['lost_ci'][0]*100:.0f}-{b['lost_ci'][1]*100:.0f}%. Treat small Δ as noise."]
out = "\n".join(L)
(stats.RUNS.parent / "EXPERIMENT_single_actions.md").write_text(out + "\n", "utf-8")
print(out)
