"""python test_personas.py -> personas/ parser self-check (no LLM calls, no files written)."""
import sim

GOOD = """# header text is ignored

## stu01
- group: students
- name: Ana Ruiz
- narrative: Second-year nursing student, flies home for Christmas.

### A. Demographic
- age: 20
- state: PA
- place: Philadelphia

### e
- patience when waiting: low

### J. Kestrel Air (sector)
- route: domestic
- trip_weeks: 8, 4, 8
- reason_for_the_trip: home for Christmas

### custom
Gets anxious when plans change.
Checks Reddit first.
"""

ps, probs = sim.parse_personas(GOOD)
assert probs == [], probs
p = ps[0]
assert p["id"] == "stu01" and p["trip_weeks"] == [4, 8] and p["patience_when_waiting"] == "low"
assert p["sections"] == {"A. Demographic": ["age", "state", "place"], "E. Emotions and reactions": ["patience_when_waiting"],
                         "J. Kestrel Air (sector)": ["route", "trip_weeks", "reason_for_the_trip"]}
assert p["custom"] == "Gets anxious when plans change.\nChecks Reddit first."
assert sim.parse_personas(sim.to_md(ps))[0] == ps, "to_md -> parse must round-trip"

prompt = sim.system_prompt(p, sim.load("prompts.json"))
assert "Ana Ruiz, 20, from Philadelphia, PA" in prompt and "Emotions and reactions:" in prompt
assert "Checks Reddit first." in prompt

bad = (GOOD.replace("- route: domestic", "- route: europe").replace("- name: Ana Ruiz\n", "")
       .replace("### e\n", "### Z. Horoscope\n").replace("- narrative:", "- age: 3\n- narrative:")
       + "\n## stu01\nstray line\n")
probs = sim.parse_personas(bad)[1]
for want in ("route", "missing name", "unique", "stray line", "unknown section", "under a ### section"):
    assert any(want in x for x in probs), (want, probs)

# folder: one file per persona; the same id in two files is refused; empty text = deleted file
Z = GOOD.replace("## stu01", "## zz99")  # an id that is not on disk
ps, probs = sim.read_personas({"zz_a.md": Z, "zz_b.md": Z})
assert any("also in zz_a.md" in x for x in probs), probs
assert "zz99" not in [p["id"] for p in sim.read_personas({"zz_a.md": ""})[0]]
assert sim.parse_personas(sim.persona_template("new01"))[0][0]["id"] == "new01"
assert sim.parse_personas("<!--\n" + GOOD + "\n-->")[0] == [], "a commented persona is off"
assert sim.parse_personas("<!-- x -->\n## a\n- bad")[1][0].startswith("line 3"), "line numbers survive comments"

fields = sim.load("prompts.json")["persona_fields"]
assert set(fields) == set(sim.SECTIONS), "persona_fields must use the catalog headings A-J"
sim.persona_schema(fields)
# customer-mix weights: group share split over its personas, renormalized over groups present
import stats
ps = [{"id": "a", "group": "x"}, {"id": "b", "group": "x"}, {"id": "c", "group": "y"}]
w = stats.persona_weights(ps, {"_note": "", "x": 0.6, "y": 0.2, "z": 0.2})
assert abs(sum(w.values()) - 1) < 1e-9 and all(abs(w[k] - v) < 1e-9 for k, v in {"a": 0.375, "b": 0.375, "c": 0.25}.items()), w
assert stats.wshare(["a"], ["a", "b", "c"], {i: 1 / 3 for i in "abc"}) == stats.wilson(1, 3), "equal weights = plain Wilson"
try:
    stats.persona_weights(ps, {"x": 1.0})
    raise AssertionError("a group without a share must be refused")
except ValueError:
    pass
print("ok")
