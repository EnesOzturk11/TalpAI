"""Kestrel Air persona simulation.

One run = check-in probe (week 0) -> 10 weeks of persona decisions + persona chats -> probe (week 11).
The world (who has a flight, whether it is canceled) is drawn from a seeded RNG; what each persona
says, does and decides comes from the LLM.

Personas live in code/personas/*.md, one file per persona (files starting with '_' are notes).
Every persona gets the same prompt templates, filled with its own fields ($profile) and '### custom' text ($custom).

CLI:
  python sim.py personas [seed]               draft the missing code/personas/*.md with Gemini (keeps existing)
  python sim.py check-personas                parse code/personas/ and list problems
  python sim.py run <name> <kind> <seed> [set] kind: plan | nodecision | plan_nosurprises; set: a candidates.json key
Key: TALP_KEY env var, else TALP_KEY=... in the repo-root .env (outside lab/, so never in the ZIP).
TALP_MOCK=1 gives fake answers for plumbing tests only.
"""
import json
import os
import random
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from string import Template

import stats

CODE = Path(__file__).resolve().parent
ROOT = CODE.parent
RUNS = ROOT / "runs"
PERSONAS_DIR = CODE / "personas"
PERSONA_FILE = re.compile(r"^[A-Za-z0-9_-]+\.md$")
COMPANY_ID = "kestrel"
STATUSES = ["flies as planned", "rebooked", "moved to another airline", "canceled the trip"]
BOOK_AGAIN = ["yes", "maybe", "no"]
BLAME = ["kestrel air", "ground handling contractor", "union", "nobody", "no trouble seen"]
ACTIONS = ["nothing", "wait and see", "check the app or news", "call support", "complain in the app",
           "complain to the DOT", "post on social media", "write a review", "tell friends",
           "ask for a refund", "ask for a credit", "rebook on Kestrel", "book another airline",
           "cancel the trip", "dispute the charge", "recommend Kestrel"]
PROBE_KEYS = ["1a", "1b", "2a", "2b", "3a", "3b", "4a", "4b"]


# ---------- files ----------

def load(name):
    return json.loads((CODE / name).read_text("utf-8"))


def read_jsonl(path):
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text("utf-8").split("\n") if x.strip()]


def write_jsonl(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), "utf-8")


# ---------- LLM ----------

def make_llm(cfg):
    """Return llm(prompt, seed, schema) -> text."""
    if os.environ.get("TALP_MOCK"):
        return _mock_llm
    from google import genai
    from google.genai import types
    os.environ.setdefault("TALP_KEY", api_key())  # also lets CallLog mask it in error text
    # vertexai + api_key, no project/location: the global aiplatform.googleapis.com endpoint
    client = genai.Client(vertexai=True, api_key=os.environ["TALP_KEY"],
                          http_options=types.HttpOptions(retry_options=types.HttpRetryOptions(attempts=5)))

    def llm(prompt, seed, schema):
        kw = dict(temperature=cfg["temperature"], seed=seed,
                  response_mime_type="application/json", response_schema=schema)
        if cfg.get("thinking_budget") is not None:
            kw["thinking_config"] = types.ThinkingConfig(thinking_budget=cfg["thinking_budget"])
        r = client.models.generate_content(model=cfg["model"], contents=prompt,
                                           config=types.GenerateContentConfig(**kw))
        return r.text or ""
    return llm


def api_key():
    if os.environ.get("TALP_KEY"):
        return os.environ["TALP_KEY"]
    env = ROOT.parent / ".env"  # repo root, outside lab/, so it never reaches the submission ZIP
    for line in env.read_text("utf-8").splitlines() if env.exists() else []:
        k, _, v = line.partition("=")
        if k.strip() == "TALP_KEY" and v.strip():
            return v.strip()
    raise RuntimeError("no key: export TALP_KEY=... or put TALP_KEY=... in the repo-root .env")


def _mock_llm(prompt, seed, schema):
    """Schema-shaped random JSON. Plumbing only: a mock run is NOT a simulation."""
    rng = random.Random(f"{seed}|{prompt}")

    def fake(s):
        t = s["type"]
        if "enum" in s:
            return rng.choice(s["enum"])
        if t == "OBJECT":
            return {k: fake(v) for k, v in s["properties"].items()}
        if t == "ARRAY":
            return [fake(s["items"]) for _ in range(rng.randint(1, 3))]
        if t == "INTEGER":
            return rng.randint(s.get("minimum", 1), s.get("maximum", 5))
        if t == "BOOLEAN":
            return rng.random() < 0.5
        return f"mock text {rng.randint(0, 999)}"
    out = fake(schema)
    for part in [out] + [v for v in out.values() if isinstance(v, dict)]:
        if "trip_weeks" in part:
            part["trip_weeks"] = sorted(rng.sample(range(1, 11), 2))
    if "dialogue" in out:
        out["dialogue"] = [{"speaker": s, "text": "mock line"} for s in "ABAB"]
    return json.dumps(out)


def S(t, **kw):
    return {"type": t, **kw}


def obj(props, required=None):
    return S("OBJECT", properties=props, required=required or list(props), property_ordering=list(props))


WEEKLY_SCHEMA = obj({
    "thinking":S("STRING", description="1-3 sentences in your own voice"),
    "actions": S("ARRAY", items=S("STRING", enum=ACTIONS)),
    "blame": S("STRING", enum=BLAME),
    "note_to_self": S("STRING", description="one sentence you want to remember next week"),
    "book_again": S("STRING", enum=BOOK_AGAIN, description="would you book Kestrel again"),
    "status": S("STRING", enum=STATUSES),
})

CHAT_SCHEMA = obj({
    "dialogue": S("ARRAY", items=obj({"speaker": S("STRING", enum=["A", "B"]), "text": S("STRING")})),
    "a_takeaway": S("STRING"), "b_takeaway": S("STRING"),
})

PROBE_SCHEMA = obj({f"q{k}": S("INTEGER", minimum=1, maximum=5) for k in PROBE_KEYS})


class CallLog:
    """Thread-safe: asks the LLM, validates, retries, logs every attempt (calls.jsonl)."""

    def __init__(self, llm, model, seed, progress=None):
        self.llm, self.model, self.seed, self.progress = llm, model, seed, progress
        self.rows, self.lock, self.done = [], threading.Lock(), 0

    def ask(self, cid, persona, week, prompt, schema, check, tries=3):
        for attempt in range(tries):
            call_id = cid if attempt == 0 else f"{cid}-r{attempt}"
            try:
                text = self.llm(prompt, self.seed + 7919 * attempt, schema)
            except Exception as e:  # network or quota: log it, try again
                msg = str(e).replace(os.environ.get("TALP_KEY") or "\0", "***")  # never let the key reach the ZIP
                text = f"ERROR {type(e).__name__}: {msg[:200]}"
            with self.lock:
                self.rows.append({"id": call_id, "persona": persona, "week": week,
                                  "prompt": prompt, "response": text, "model": self.model})
            try:
                data = json.loads(text)
                if check(data):
                    break
            except ValueError:
                pass
        else:
            raise RuntimeError(f"{cid}: no valid answer after {tries} tries; last: {text[:200]}")
        with self.lock:
            self.done += 1
            if self.progress:
                self.progress(self.done)
        return data, call_id


def fill(template, **kw):
    return Template(template).safe_substitute(**kw)


def pmap(fn, items, workers):
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(fn, items))


# ---------- personas (personas/*.md) ----------

# Section headings of yeni-case-5-sirket/03-audience-attributes.md (A-I) plus the dossier's sector attributes (J).
SECTIONS = ("A. Demographic", "B. Life story", "C. Values and attitudes", "D. Behavior",
            "E. Emotions and reactions", "F. Social and information", "G. Money pressure",
            "H. What they can do", "I. Lifestyle and personal details", "J. Kestrel Air (sector)")
TOP = ("group", "name", "narrative")  # fields above the first '###', not in a catalog section
REQUIRED = TOP + ("age", "state", "route", "trip_weeks", "reason_for_the_trip")


def section_of(heading):
    """'### A. Demographic', '### a', '### Demographic' -> 'A. Demographic'; None if unknown."""
    h = heading.strip().lower().rstrip(".")
    for s in SECTIONS:
        letter, name = s.split(". ", 1)
        if h in (s.lower(), letter.lower(), name.lower()):
            return s
    return None


def parse_personas(text):
    """One persona file's text -> (personas, problems). Format per persona:
    ## <id>
    - group: ... / - name: ... / - narrative: ...      (top fields)
    ### A. Demographic                                  (catalog sections, in any order, any fields)
    - age: 34
    ### custom                                          (free text for this persona only)
    Text before the first '## ' is ignored. <!-- HTML comments --> are skipped: wrap a persona in one to switch it off."""
    # blank out comments but keep their newlines, so problem line numbers still match the file
    text = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    personas, problems, cur, sec = [], [], None, None
    for n, line in enumerate(text.split("\n"), 1):
        if line.startswith("## "):
            cur, sec = {"id": line[3:].strip(), "custom": "", "sections": {}}, None
            personas.append(cur)
        elif cur is None:
            continue
        elif line.startswith("### "):
            heading = line[4:].strip()
            sec = "custom" if heading.lower() == "custom" else section_of(heading)
            if sec is None:
                problems.append(f"line {n}: unknown section '{heading}' (use A-J from the catalog, or custom)")
        elif sec == "custom":
            cur["custom"] += line + "\n"
        elif m := re.match(r"^\s*[-*]\s*([^:]+):\s*(.*)$", line):
            key = re.sub(r"[^a-z0-9]+", "_", m.group(1).strip().lower()).strip("_")
            if key in cur:  # also catches the reserved id / custom / sections
                problems.append(f"line {n}: {cur['id']}: field '{key}' appears twice or is reserved")
            if sec is None and key not in TOP:
                problems.append(f"line {n}: {cur['id']}: '{key}' must be under a ### section (only {', '.join(TOP)} go on top)")
            cur[key] = m.group(2).strip()
            if sec:
                cur["sections"].setdefault(sec, []).append(key)
        elif line.strip():
            problems.append(f"line {n}: not '- field: value' ({line.strip()[:40]})")
    seen = set()
    for p in personas:
        p["custom"] = p["custom"].strip()
        pid = p["id"]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", pid) or pid in seen:
            problems.append(f"{pid!r}: id must be unique, letters/digits/_/- only")
        seen.add(pid)
        missing = [f for f in REQUIRED if not str(p.get(f, "")).strip()]
        if missing:
            problems.append(f"{pid}: missing {', '.join(missing)}")
            continue
        p["trip_weeks"] = sorted({int(w) for w in re.findall(r"\d+", str(p["trip_weeks"]))})
        if not p["trip_weeks"] or not all(1 <= w <= 10 for w in p["trip_weeks"]):
            problems.append(f"{pid}: trip_weeks must be weeks 1-10, e.g. '4, 8'")
        if p["route"] not in ("domestic", "mexico_caribbean"):
            problems.append(f"{pid}: route must be domestic or mexico_caribbean")
    return personas, problems


def persona_files():
    return sorted(f for f in PERSONAS_DIR.glob("*.md") if not f.name.startswith("_"))


def read_personas(override=None):
    """All personas/*.md -> (personas, problems). override={file name: text} checks unsaved text in place."""
    texts = {f.name: f.read_text("utf-8") for f in persona_files()} | (override or {})
    personas, problems, where = [], [], {}
    for name, text in sorted(texts.items()):
        if not text.strip():
            continue
        ps, probs = parse_personas(text)
        problems += [f"{name}: {x}" for x in probs]
        for p in ps:
            if p["id"] in where:
                problems.append(f"{name}: id {p['id']} is also in {where[p['id']]}")
            where[p["id"]] = name
        personas += ps
    return personas, problems


def load_personas():
    personas, problems = read_personas()
    if problems:
        raise ValueError("personas/: " + "; ".join(problems[:5]))
    if not personas:
        raise ValueError("personas/ has no personas yet")
    return personas


def persona_template(pid):
    """A new persona file: required fields first, every catalog section heading ready to fill."""
    req = {"A. Demographic": ["age", "state", "place"], "J. Kestrel Air (sector)": ["route", "trip_weeks", "reason_for_the_trip"]}
    out = [f"## {pid}", "- group: ", "- name: ", "- narrative: "]
    for s in SECTIONS:
        out += ["", f"### {s}"] + [f"- {k}: " for k in req.get(s, [])]
    return "\n".join(out + ["", "### custom", ""])


def fmt(v):
    return ", ".join(map(str, v)) if isinstance(v, list) else str(v)


def to_md(personas):
    out = []
    for p in personas:
        out += [f"## {p['id']}"] + [f"- {k}: {p[k]}" for k in TOP]
        for s in SECTIONS:
            if p["sections"].get(s):
                out += ["", f"### {s}"] + [f"- {k}: {fmt(p[k])}" for k in p["sections"][s]]
        out += ["", "### custom", p.get("custom", ""), ""]
    return "\n".join(out)


PERSONAS_FORMAT = """# Kestrel Air personas: file format

One file per persona in code/personas/ (any name ending .md; files starting with '_' are ignored).
A file may also hold several personas. The parser checks every file:
- '## <id>' starts a persona. Under it, before any section: '- group:', '- name:', '- narrative:'.
- Then '### <section>' blocks named after the audience attribute catalog (03-audience-attributes.md):
  A. Demographic · B. Life story · C. Values and attitudes · D. Behavior · E. Emotions and reactions ·
  F. Social and information · G. Money pressure · H. What they can do · I. Lifestyle and personal details ·
  J. Kestrel Air (sector) for the dossier's sector attributes.
  Each holds '- field: value' lines; use only the fields that matter, any order.
- Required: group, name, narrative; age and state (A); route (domestic | mexico_caribbean),
  trip_weeks (weeks 1-10 with a booked Kestrel flight, e.g. 4, 8) and reason_for_the_trip (J).
- '### custom': free text for this persona only, added to its prompt as is.
Every persona gets the same templates from prompts.json; its sections fill $profile and its custom text fills $custom.
"""


def profile_text(p):
    out = [f"In short: {p['narrative']}"]
    for s in SECTIONS:
        keys = p["sections"].get(s)
        if keys:
            out += [f"{s.split('. ', 1)[1]}:"] + [f"- {k.replace('_', ' ')}: {fmt(p[k])}" for k in keys]
    return "\n".join(out)


def home_of(p):
    return ", ".join(x for x in (p.get("place"), p.get("state")) if x) or "the US"


def system_prompt(p, cfg):
    """The one persona prompt: same template for everyone, filled from this persona's personas/ file."""
    custom = f"\nAbout you, in particular:\n{p['custom']}" if p.get("custom") else ""
    return fill(cfg["persona_system"], name=p["name"], age=p["age"], home=home_of(p), company=cfg["company"],
                group=p["group"], profile=profile_text(p), custom=custom)


def persona_schema(fields):
    """Draft schema from prompts.json persona_fields: {section: {field: description}}."""
    special = {"age": S("INTEGER", minimum=18, maximum=90),
               "trip_weeks": S("ARRAY", items=S("INTEGER", minimum=1, maximum=10)),
               "route": S("STRING", enum=["domestic", "mexico_caribbean"])}
    props = {"name": S("STRING"), "narrative": S("STRING", description="2-3 sentences: life now and what this trip means")}
    for sec, fs in fields.items():
        if fs:
            props["sec_" + sec[0]] = obj({k: {**special.get(k, S("STRING")), "description": d} for k, d in fs.items()})
    return props


def generate_personas(seed=1, progress=None):
    """Draft the missing personas/<id>.md files with Gemini (ids from prompts.json persona_groups, fields from
    persona_fields). Existing files, commented-out ones included, are never touched or re-generated."""
    cfg = load("prompts.json")
    fields = {section_of(s) or s: fs for s, fs in cfg["persona_fields"].items()}
    unknown = [s for s in fields if s not in SECTIONS]
    have = set(TOP) | {k for fs in fields.values() for k in fs}
    if unknown or not set(REQUIRED) <= have:
        raise ValueError(f"persona_fields: unknown sections {unknown} or missing {sorted(set(REQUIRED) - have)}")
    schema = obj(persona_schema(fields))
    log = CallLog(make_llm(cfg), cfg["model"], seed, progress)
    rng = random.Random(seed)
    homes = ["Orlando area, FL", "Philadelphia area, PA", "elsewhere in Florida",
             "elsewhere in the Northeast", "the Midwest", "the South"]
    ages = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    jobs = []
    for group, n in cfg["persona_groups"].items():
        prefix = re.sub(r"[^a-z]", "", group)[:3]
        hints = [f"lives in {rng.choice(homes)}; age band {rng.choice(ages)}; "
                 f"income {rng.choice(['lower', 'middle', 'upper-middle'])}" for _ in range(n)]
        jobs.append((group, prefix, hints))

    def flatten(pid, group, d):
        p = {"id": pid, "group": group, "name": d["name"], "narrative": d["narrative"], "custom": "", "sections": {}}
        for sec, fs in fields.items():
            part = d.get("sec_" + sec[0], {})
            for k in fs:
                if k in part:
                    p[k] = part[k]
                    p["sections"].setdefault(sec, []).append(k)
        return p

    on_disk = {p["id"]: p for p in read_personas()[0]}

    def make_group(job):
        group, prefix, hints = job
        made = []
        for i, hint in enumerate(hints, 1):
            pid = f"{prefix}{i:02d}"
            if (PERSONAS_DIR / f"{pid}.md").exists():
                if pid in on_disk:  # active ones still steer the new ones away from duplicates
                    made.append(on_disk[pid])
                continue
            existing = "\n".join(f"- {m['name']}, {m.get('age')}, {home_of(m)}: {m['narrative'][:120]}"
                                 for m in made) or "- none yet"
            prompt = fill(cfg["persona_gen"], group=group, hint=hint, existing=existing)

            def ok(d):
                tw = flatten(pid, group, d).get("trip_weeks")
                return bool(tw) and all(isinstance(w, int) and 1 <= w <= 10 for w in tw)
            data, _ = log.ask(f"gen-{pid}", None, 0, prompt, schema, ok)
            p = flatten(pid, group, data)
            p["trip_weeks"] = sorted(set(p["trip_weeks"]))
            if group == "travel agencies":
                p["custom"] = "You answer for the agency and the group you booked, not only for yourself."
            (PERSONAS_DIR / f"{pid}.md").write_text(to_md([p]), "utf-8")  # saved at once: a stop keeps what is done
            made.append(p)
            new.append(pid)
        return made

    PERSONAS_DIR.mkdir(exist_ok=True)
    new = []
    try:
        pmap(make_group, jobs, len(jobs))
    finally:
        with open(CODE / "personas_gen_calls.jsonl", "a", encoding="utf-8") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in log.rows)
    return new


def missing_persona_ids(cfg):
    return [f"{re.sub(r'[^a-z]', '', g)[:3]}{i:02d}" for g, n in cfg["persona_groups"].items() for i in range(1, n + 1)
            if not (PERSONAS_DIR / f"{re.sub(r'[^a-z]', '', g)[:3]}{i:02d}.md").exists()]


# ---------- world ----------

def active_effects(decisions, week, world):
    """Multipliers/additions from decision actions that are in force this week."""
    eff = {"cancel_x": 1.0, "delay_x": 1.0, "strike_cancel_x": 1.0, "strike_delay_x": 1.0,
           "rebook24_add": 0.0, "merge": 0.0, "on_disrupted": [], "on_stranded": []}
    for d in decisions:
        for a in d["actions"]:
            e = world["action_effects"].get(a["action"])
            if not e or not d["week"] <= week < d["week"] + e.get("weeks", 10):
                continue
            for k in eff:
                v = e.get(k)
                v = v.get(a["level"]) if isinstance(v, dict) else v
                if v is None:
                    continue
                if isinstance(eff[k], list):  # what the passenger actually gets, told in their situation
                    eff[k].append(v)
                else:
                    eff[k] = eff[k] * v if k.endswith("_x") else eff[k] + v
    return eff


def draw_trip(p, week, rng, world, eff, surprise_x):
    """Seeded draw of what happens to this persona's flight this week (None = no flight)."""
    if week not in p["trip_weeks"]:
        return None
    kc = world["known_crisis"]
    strike_day = week in kc["weeks"] and rng.random() < kc["strike_day_share"]
    base = kc if strike_day else world["normal"]
    cancel = base["cancel"] * eff["cancel_x"] * surprise_x["cancel_x"]
    delay = base["delay3h"] * eff["delay_x"] * surprise_x["delay_x"]
    if strike_day:
        cancel *= eff["strike_cancel_x"]
        delay *= eff["strike_delay_x"]
    r = rng.random()
    if r < cancel:
        outcome = "canceled"
    elif r < cancel + delay:
        outcome = "delayed over 3 hours"
    elif rng.random() < eff["merge"]:
        outcome = "merged into another flight the same day (told 7 days ahead)"
    else:
        outcome = "on time"
    rebook24 = outcome in ("canceled", "delayed over 3 hours") and rng.random() < min(1.0, base["rebook24"] + eff["rebook24_add"])
    return {"strike_day": strike_day, "outcome": outcome, "rebook24": rebook24}


def trip_text(p, week, trip, world, eff):
    if trip is None:
        later = [w for w in p["trip_weeks"] if w > week]
        return f"You have no Kestrel flight this week. Next booked Kestrel flight: week {later[0]}." if later \
            else "You have no Kestrel flight this week and none booked later in these ten weeks."
    route = "to Mexico/the Caribbean" if p["route"] == "mexico_caribbean" else "within the US"
    day = " It is one of the strike days." if trip["strike_day"] else ""
    t = f"You have a Kestrel flight {route} this week ({p['reason_for_the_trip']}).{day} Your flight: {trip['outcome']}."
    if trip["outcome"] in ("canceled", "delayed over 3 hours"):
        t += (" Kestrel offered you a new seat within 24 hours." if trip["rebook24"]
              else " After more than 24 hours you still have no new seat or refund confirmed; the call center wait is long.")
        t += "".join(" " + x for x in eff["on_disrupted"])
        if not trip["rebook24"]:
            t += "".join(" " + x for x in eff["on_stranded"])
    return t


def surprise_reach(s, p):
    """Chance this persona hears the surprise: 'reach', or 'reach_high' (0.95) if a persona field contains any
    '|'-separated term in 'reach_if', e.g. {"afraid_of_flying": "yes", "news_sources": "tiktok|instagram"}."""
    hit = any(t in str(p.get(f, "")).lower() for f, terms in s.get("reach_if", {}).items() for t in terms.split("|"))
    return s.get("reach_high", 0.95) if hit else s.get("reach", 0.6)


def surprise_state(surprises, week):
    x = {"cancel_x": 1.0, "delay_x": 1.0}
    for s in surprises:
        if s["week"] <= week < s["week"] + s.get("effect_weeks", 1):
            x["cancel_x"] *= s.get("cancel_x", 1.0)
            x["delay_x"] *= s.get("delay_x", 1.0)
    return x


def targeted(d, p):
    t = str(d["target"]).lower()
    return t == "everyone" or p["id"].lower() in t or p["group"].lower() in t


# ---------- run ----------

def decision_sets():
    """'' = decisions.json (the locked plan; use it for the five submission runs), else a candidates.json key."""
    return {"": load("decisions.json")["decisions"]} | {k: v for k, v in load("candidates.json").items() if not k.startswith("_")}


def run(name, kind, seed, progress=None, decision_set="", surprise_variant="", no_surprises=False, world_patch=None):
    if kind not in ("plan", "nodecision", "plan_nosurprises"):
        raise ValueError(f"unknown kind {kind}")
    cfg, world = load("prompts.json"), load("world.json")
    for k, v in (world_patch or {}).items():  # e.g. {"known_crisis": {"cancel": 0.9}} for a sanity run; saved in run.json
        world[k] = world[k] | v if isinstance(v, dict) else v
    personas = load_personas()
    stats.persona_weights(personas, world["customer_mix"])  # fail before any call if a group has no share
    decisions = [] if kind == "nodecision" else decision_sets()[decision_set]
    # a surprise may carry "variants": {"mild": {overrides}}; no variant = the entry as written
    surprises = [] if kind == "plan_nosurprises" or no_surprises else \
        [s | s.get("variants", {}).get(surprise_variant, {}) for s in world["surprises"]]
    rng = random.Random(seed)
    total = len(personas) * 12 + (len(personas) // 2) * 10
    log = CallLog(make_llm(cfg), cfg["model"], seed, progress and (lambda n: progress(n, total)))
    W = cfg["workers"]
    by_id = {p["id"]: p for p in personas}
    company = cfg["company"]

    def system(p):
        return system_prompt(p, cfg)

    def probe(when, week):
        text = ("Before the ten weeks start (early November)." if when == "start"
                else "The ten weeks are over (mid-January). Think back over everything that happened.")

        def one(p):
            mem = "" if when == "start" else "\nYour notes: " + " | ".join(state[p["id"]]["notes"][-5:])
            prompt = system(p) + mem + "\n\n" + fill(cfg["probe"], when_text=text, company=company)
            data, cid = log.ask(f"probe-{when}-{p['id']}", p["id"], week, prompt, PROBE_SCHEMA,
                                lambda d: all(isinstance(d.get(f"q{k}"), int) and 1 <= d[f"q{k}"] <= 5
                                              for k in PROBE_KEYS))
            return [{"persona": p["id"], "when": when, "question": k, "score": data[f"q{k}"], "call": cid}
                    for k in PROBE_KEYS]
        return [row for rows in pmap(one, personas, W) for row in rows]

    state = {p["id"]: {"notes": [], "news": [], "heard": [], "status": "flies as planned"} for p in personas}
    probe_rows = probe("start", 0)
    weekly, chats = [], []
    kc = world["known_crisis"]

    for week in range(1, 11):
        dates = world["weeks"][str(week)]
        eff = active_effects(decisions, week, world)
        sx = surprise_state(surprises, week)
        # world draws first, in persona order, so the same seed gives the same world
        trips, prompts = {}, {}
        for p in personas:
            st = state[p["id"]]
            trips[p["id"]] = draw_trip(p, week, rng, world, eff, sx)
            fresh = []
            if week >= kc["news_from_week"] and kc["news"] not in st["news"] and rng.random() < kc["news_reach"]:
                fresh.append(kc["news"])
            if week in kc["weeks"]:
                fresh.append(kc["strike_news"])
            for s in surprises:
                if s["week"] == week and rng.random() < surprise_reach(s, p):
                    fresh.append(s["text"])
            events = "\n".join(f"- (new) {x}" for x in fresh) + "".join(f"\n- (earlier) {x}" for x in st["news"][-4:])
            st["news"] += [x for x in fresh if x != kc["strike_news"]]
            msgs = [d["message"] for d in decisions if d["week"] <= week and targeted(d, p)]
            prompts[p["id"]] = system(p) + "\n\n" + fill(
                cfg["weekly"], week=week, dates=dates, company=company, bau=world["business_as_usual"],
                trip=trip_text(p, week, trips[p["id"]], world, eff),
                events=events.strip() or "- nothing about Kestrel",
                messages="\n".join(f'- "{m}"' for m in msgs) or "- none",
                heard="\n".join(f"- {h}" for h in st["heard"]) or "- nothing about Kestrel",
                memory="\n".join(f"- week {i + 1}: {n}" for i, n in enumerate(st["notes"])) or "- none (this is the first week)")

        def act(p):
            data, cid = log.ask(f"w{week:02d}-act-{p['id']}", p["id"], week, prompts[p["id"]], WEEKLY_SCHEMA,
                                lambda d: d.get("status") in STATUSES and d.get("book_again") in BOOK_AGAIN)
            return {"persona": p["id"], "week": week, "status": data["status"], "call": cid,
                    "book_again": data["book_again"], "blame": data.get("blame"),
                    "actions": data.get("actions", []), "thinking": data.get("thinking", ""),
                    "note": data.get("note_to_self", ""), "trip": trips[p["id"]]}
        rows = pmap(act, personas, W)
        weekly += rows
        for r in rows:
            st = state[r["persona"]]
            st["status"] = r["status"]
            st["last"] = r["thinking"]
            st["notes"].append(log_note(r))

        # persona-to-persona talk: random pairs each week
        # ponytail: uniform random mixing; weight pairs by group/home (homophily) if time allows
        order = [p["id"] for p in personas]
        rng.shuffle(order)
        pairs = list(zip(order[::2], order[1::2]))

        def talk(pair):
            a, b = by_id[pair[0]], by_id[pair[1]]
            prompt = fill(cfg["chat"], week=week, dates=dates, company=company,
                          a_name=a["name"], a_group=a["group"], a_profile=a["narrative"],
                          a_state=f"{state[a['id']]['last']} (status: {state[a['id']]['status']})",
                          b_name=b["name"], b_group=b["group"], b_profile=b["narrative"],
                          b_state=f"{state[b['id']]['last']} (status: {state[b['id']]['status']})")
            data, cid = log.ask(f"w{week:02d}-chat-{a['id']}-{b['id']}", a["id"], week, prompt, CHAT_SCHEMA,
                                lambda d: bool(d.get("dialogue")))
            return {"week": week, "a": a["id"], "b": b["id"], "dialogue": data["dialogue"],
                    "a_takeaway": data.get("a_takeaway", ""), "b_takeaway": data.get("b_takeaway", ""), "call": cid}
        week_chats = pmap(talk, pairs, W)
        chats += week_chats
        for st in state.values():
            st["heard"] = []
        for c in week_chats:
            state[c["a"]]["heard"].append(f"You talked with {by_id[c['b']]['name']}: {c['a_takeaway']}")
            state[c["b"]]["heard"].append(f"You talked with {by_id[c['a']]['name']}: {c['b_takeaway']}")

    probe_rows += probe("end", 11)

    out = RUNS / name
    out.mkdir(parents=True, exist_ok=True)
    (out / "run.json").write_text(json.dumps({
        "company": COMPANY_ID, "type": kind, "seed": seed, "model": "MOCK" if os.environ.get("TALP_MOCK") else cfg["model"],
        "decisions": [{k: d[k] for k in ("week", "target", "actions", "message", "channels", "why")} for d in decisions],
        "surprises": [s.get("title", s["text"][:60]) for s in surprises],
        "surprise_variant": surprise_variant or "as written",
        "world_patch": world_patch or {},
        "decision_set": "" if kind == "nodecision" else (decision_set or "decisions.json"),
        "customer_mix": world["customer_mix"],
    }, indent=2, ensure_ascii=False), "utf-8")
    write_jsonl(out / "personas.jsonl", personas)
    write_jsonl(out / "calls.jsonl", log.rows)
    write_jsonl(out / "weekly.jsonl", weekly)
    write_jsonl(out / "chats.jsonl", chats)
    write_jsonl(out / "probe.jsonl", probe_rows)
    (out / "metrics.json").write_text(json.dumps(stats.run_metrics(personas, weekly, probe_rows, world), indent=2), "utf-8")
    return out


def log_note(r):
    trip = r["trip"]["outcome"] if r["trip"] else "no flight"
    return f"{trip}; {r['status']}; did: {', '.join(r['actions']) or 'nothing'}. {r['note']}"


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["personas"]:
        print(len(generate_personas(int(args[1]) if len(args) > 1 else 1)), "new personas written to", PERSONAS_DIR)
    elif args[:1] == ["check-personas"]:
        ps, probs = read_personas()
        print(f"{len(ps)} personas", *probs, sep="\n")
    elif args[:1] == ["run"] and len(args) in (4, 5):
        print(run(args[1], args[2], int(args[3]), lambda n, t: print(f"\r{n}/{t}", end="", flush=True),
                  args[4] if len(args) == 5 else ""))
    else:
        print(__doc__)
