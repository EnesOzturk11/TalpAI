#!/usr/bin/env python3
"""Merge the field-research pool (data/personas.jsonl, 36) with the team's pool (data/personas_v2.jsonl, 48)
into data/personas_84.jsonl, mapped to the dossier's groups and re-weighted.

    python3 code/personas_all.py
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEEKLY_PAX = 210_000
GROUP_SHARE = {"families visiting relatives": 0.38, "vacationers": 0.37, "students": 0.09,
               "business travelers": 0.09, "travel agencies": 0.07}
V2_GROUP = {"Visiting family": "families visiting relatives", "Leisure": "vacationers",
            "Work travelers": "business travelers", "Older and assisted travelers": "families visiting relatives"}


def main():
    a = [json.loads(l) for l in open(ROOT / "data" / "personas.jsonl", encoding="utf-8")]
    b = [json.loads(l) for l in open(ROOT / "data" / "personas_v2.jsonl", encoding="utf-8")]
    for p in a:
        p["pool"] = "field research (36)"
    for p in b:
        p["pool"] = "team set (48)"
        p["segment"] = p["group"]
        p["group"] = V2_GROUP[p["group"]]
    allp = a + b
    n = Counter(p["group"] for p in allp)
    for p in allp:
        p["represents_weekly_pax"] = round(GROUP_SHARE[p["group"]] * WEEKLY_PAX / n[p["group"]])
    ids = [p["id"] for p in allp]
    assert len(ids) == len(set(ids))
    with open(ROOT / "data" / "personas_84.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps(p, ensure_ascii=False) + "\n" for p in allp)
    print(f"{len(allp)} personas:", dict(n))
    print("strike exposure:", dict(Counter(p["strike_exposure"] for p in allp)))
    legs = [t for p in allp for t in p["trips"] if t.get("week")]
    print("legs by week:", dict(sorted(Counter(t["week"] for t in legs).items())))


if __name__ == "__main__":
    main()
