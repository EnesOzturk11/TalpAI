#!/usr/bin/env python3
"""Side-by-side goals for every run in a folder.   usage: python code/compare.py runs"""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else "runs")
print(f"{'run':18}{'G1 ops%':>8}{'G2 24h%':>9}{'G3 NPS':>8}{'G3b cmp':>9}{'G4 rev%':>9}  G2 sample        final status mix (% weighted)")
for d in sorted(p for p in root.iterdir() if (p / "metrics.json").exists()):
    m = json.loads((d / "metrics.json").read_text())
    x = m["detail"]
    mix = x["final_status_mix_pct"]
    s = x["goal_2_sample"]
    print(f"{d.name:18}{m['goal_1']:8}{m['goal_2']:9}{m['goal_3']:8}{m['goal_3b']:9}{m['goal_4']:9}  "
          f"{s['ok']}/{s['disrupted_legs']} legs      "
          f"kept {mix['flies as planned'] + mix['rebooked']:.0f} / other airline {mix['moved to another airline']:.0f} / canceled {mix['canceled the trip']:.0f}")
