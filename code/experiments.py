#!/usr/bin/env python3
"""Run decision packages x seeds (and scenarios) and print a comparison.

    .venv/bin/python code/experiments.py run  [--seeds 1,2] [--scenario base|severe] [--only A_shield_w7,...]
    .venv/bin/python code/experiments.py report
"""
import argparse
import json
import math
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "runs_dev" / "exp"
SCEN = {"base": None, "severe": "config/experiments/crises_severe.json"}


def packages():
    return ["nodecision"] + sorted(p.stem for p in (ROOT / "config" / "experiments").glob("*.json") if not p.stem.startswith("crises"))


def write_severe():
    """Severe scenario = the current crises.json (surprises included) with a harder, extended strike."""
    doc = json.loads((ROOT / "config" / "crises.json").read_text())
    for c in doc["crises"]:
        if c["id"] == "strike":
            e = c["effects"][0]
            e.update(dates=["2026-12-22", "2026-12-23", "2026-12-24"], cancel_rate=0.5, delay_hours=5)
            e["mitigated_by"] = {"backup ground handling contract at both bases for the strike days": 0.4}
            c["reading"] = "SEVERE test scenario: half of base flights canceled, 5h delays, strike extended to Dec 24."
    (ROOT / SEVERE_FILE).write_text(json.dumps(doc, indent=2, ensure_ascii=False))


SEVERE_FILE = "config/experiments/crises_severe.json"


def one(pkg, seed, scenario):
    name = f"{scenario}__{pkg}__s{seed}"
    cmd = [str(ROOT / ".venv/bin/python"), "-I", "code/sim.py", "--name", name, "--seed", str(seed), "--out", "runs_dev/exp",
           "--type", "nodecision" if pkg == "nodecision" else "plan", "--workers", "16", "--probe"]
    if pkg != "nodecision":
        cmd += ["--decisions", f"config/experiments/{pkg}.json"]
    if SCEN[scenario]:
        cmd += ["--crises", SCEN[scenario]]
    env = dict(os.environ, SSL_CERT_FILE=os.environ.get("SSL_CERT_FILE", "/etc/ssl/cert.pem"))
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)
    print(("ok   " if r.returncode == 0 else "FAIL ") + name + ("" if r.returncode == 0 else "\n" + r.stderr[-800:]), flush=True)


def wilson(k, n, z=1.96):
    if n == 0:
        return (0, 0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(100 * (c - h)), round(100 * (c + h)))


def report():
    rows = {}
    for d in sorted(OUT.iterdir()):
        if not (d / "metrics.json").exists():
            continue
        scen, pkg, _ = d.name.split("__")
        m = json.loads((d / "metrics.json").read_text())
        W = [json.loads(l) for l in open(d / "weekly.jsonl")]
        run = json.loads((d / "run.json").read_text())
        moved = {r["persona"] for r in W if "change to a different date" in r["actions"]}
        rows.setdefault((scen, pkg), []).append((m, W, run, moved))
    print(f"{'scenario':8} {'package':18} {'cost':>5} {'G1 ops':>7} {'G2 24h (pooled, 95% CI)':>25} {'G3 NPS':>11} "
          f"{'cmpl idx':>9} {'G4 rev':>11} {'other airl':>10} {'moved early':>11}")
    for (scen, pkg), rs in sorted(rows.items(), key=lambda x: (x[0][0], x[0][1] != "nodecision", x[0][1])):
        def rng(key):
            v = [r[0][key] for r in rs]
            return f"{min(v):.0f}-{max(v):.0f}" if len(v) > 1 and round(min(v)) != round(max(v)) else f"{v[0]:.0f}"
        k = sum(r[0]["detail"]["goal_2_sample"]["ok"] for r in rs)
        n = sum(r[0]["detail"]["goal_2_sample"]["disrupted_legs"] for r in rs)
        g2 = sum(r[0]["goal_2"] for r in rs) / len(rs)
        lo, hi = wilson(k, n)
        other = [r[0]["detail"]["final_status_mix_pct"]["moved to another airline"] for r in rs]
        moved = sorted(set().union(*[r[3] for r in rs]))
        cost = rs[0][2].get("cost_musd", 0)
        print(f"{scen:8} {pkg:18} {cost:5.2f} {rng('goal_1'):>7} {f'{g2:.0f}% ({k}/{n} legs, {lo}-{hi})':>25} "
              f"{rng('goal_3'):>11} {rng('goal_3b'):>9} {rng('goal_4'):>11} {f'{min(other):.0f}-{max(other):.0f}%':>10} "
              f"{len(moved):>4} {','.join(moved)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "report"])
    ap.add_argument("--seeds", default="1,2")
    ap.add_argument("--scenario", default="base", choices=list(SCEN))
    ap.add_argument("--only", default="")
    ap.add_argument("--parallel", type=int, default=6)
    a = ap.parse_args()
    if a.cmd == "report":
        return report()
    if a.scenario == "severe":
        write_severe()
    pk = a.only.split(",") if a.only else packages()
    jobs = [(p, int(s), a.scenario) for p in pk for s in a.seeds.split(",")]
    with ThreadPoolExecutor(a.parallel) as ex:
        list(ex.map(lambda j: one(*j), jobs))
    report()


if __name__ == "__main__":
    sys.exit(main())
