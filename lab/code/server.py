"""Local dashboard for the simulation: python server.py  ->  http://127.0.0.1:8765"""
import json
import re
import subprocess
import sys
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import sim
import stats

CONFIGS = ("prompts.json", "world.json", "decisions.json", "candidates.json")
RUN_FILES = ("run.json", "metrics.json", "calls.jsonl", "weekly.jsonl", "chats.jsonl", "probe.jsonl", "personas.jsonl")
NAME = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
CHECK = sim.ROOT.parent / "yeni-case-5-sirket" / "check.py"

# ponytail: one job at a time behind a global lock; a queue if teams need parallel runs
JOB = {"state": "idle", "label": "", "done": 0, "total": 0, "error": ""}
JOB_LOCK = threading.Lock()


def start_job(label, total, fn):
    if not JOB_LOCK.acquire(blocking=False):
        raise ValueError(f"busy: {JOB['label']}")
    JOB.update(state="running", label=label, done=0, total=total, error="")

    def work():
        try:
            fn(lambda done, tot=None: JOB.update(done=done, total=tot or JOB["total"]))
            JOB["state"] = "done"
        except Exception as e:
            traceback.print_exc()
            JOB.update(state="error", error=f"{type(e).__name__}: {e}"[:500])
        finally:
            JOB_LOCK.release()
    threading.Thread(target=work, daemon=True).start()


def budget(decisions, world):
    total, problems = 0.0, []
    for d in decisions:
        for a in d.get("actions", []):
            c = world["costs"].get(a.get("action"), {}).get(a.get("level"))
            if c is None:
                problems.append(f"not in the menu: {a.get('action')} / {a.get('level')}")
            else:
                total += c
        if len(d.get("message", "")) > 600:
            problems.append(f"week {d.get('week')}: message over 600 characters")
    return {"total_musd": round(total, 2), "limit_musd": world["budget"],
            "ok": total <= world["budget"] and not problems, "problems": problems}


def list_runs():
    out = []
    for d in sorted(sim.RUNS.glob("*/run.json")):
        r = json.loads(d.read_text("utf-8"))
        m = d.parent / "metrics.json"
        out.append({"name": d.parent.name, "type": r["type"], "seed": r["seed"], "model": r["model"],
                    "decision_set": r.get("decision_set", ""),
                    "metrics": json.loads(m.read_text("utf-8")) if m.exists() else {}})
    return out


class H(BaseHTTPRequestHandler):
    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else (
            body.encode() if isinstance(body, str) else json.dumps(body, ensure_ascii=False).encode())
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 2_000_000:
            raise ValueError("body too large")
        return self.rfile.read(n).decode("utf-8")

    def do_GET(self):
        self.route("GET")

    def do_POST(self):
        self.route("POST")

    def route(self, method):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            fn = getattr(self, f"{method}_{u.path.strip('/').replace('/', '_') or 'index'}", None)
            if fn is None:
                return self.send(404, {"error": "not found"})
            fn(q)
        except ValueError as e:
            self.send(400, {"error": str(e)})
        except Exception as e:
            traceback.print_exc()
            self.send(500, {"error": f"{type(e).__name__}: {e}"})

    def GET_index(self, q):
        self.send(200, (sim.CODE / "index.html").read_bytes(), "text/html")

    def GET_api_state(self, q):
        world = sim.load("world.json")
        personas, problems = sim.read_personas()
        try:
            weights = stats.persona_weights(personas, sim.load("world.json")["customer_mix"])
        except ValueError as e:
            weights, problems = {}, problems + [str(e)]
        files = {f.name: [p["id"] for p in sim.parse_personas(f.read_text("utf-8"))[0]] for f in sim.persona_files()}
        self.send(200, {"job": JOB, "runs": list_runs(), "personas": personas, "persona_problems": problems,
                        "persona_missing": sim.missing_persona_ids(sim.load("prompts.json")),
                        "persona_files": files, "weights": weights,
                        "budgets": {k: budget(v, world) for k, v in sim.decision_sets().items()}})

    def GET_api_preview(self, q):
        """The exact persona prompt the run will send (system part), filled from its personas/ file."""
        p = next((x for x in sim.load_personas() if x["id"] == q.get("id")), None)
        if p is None:
            raise ValueError("unknown persona")
        self.send(200, sim.system_prompt(p, sim.load("prompts.json")), "text/plain")

    def GET_api_config(self, q):
        if q.get("name") not in CONFIGS:
            raise ValueError("unknown config")
        self.send(200, (sim.CODE / q["name"]).read_text("utf-8"), "text/plain")

    def POST_api_config(self, q):
        if q.get("name") not in CONFIGS:
            raise ValueError("unknown config")
        text = self.body()
        json.loads(text)  # refuse broken JSON before it reaches a run
        (sim.CODE / q["name"]).write_text(text, "utf-8")
        self.send(200, {"ok": True})

    def persona_path(self, q):
        name = q.get("name", "")
        if not sim.PERSONA_FILE.match(name) or name.startswith("_"):
            raise ValueError("file name: letters, digits, _ and - only, ending .md")
        return sim.PERSONAS_DIR / name

    def GET_api_persona_file(self, q):
        p = self.persona_path(q)
        self.send(200, p.read_text("utf-8") if p.exists() else sim.persona_template(p.stem), "text/plain")

    def POST_api_persona_file(self, q):
        """Save one persona file; empty text deletes it. Refused if it would break any persona."""
        p, text = self.persona_path(q), self.body()
        problems = [x for x in sim.read_personas({p.name: text})[1] if p.name in x]  # other files' problems don't block
        if problems:
            raise ValueError("not saved: " + "; ".join(problems[:8]))
        if text.strip():
            sim.PERSONAS_DIR.mkdir(exist_ok=True)
            p.write_text(text, "utf-8")
        elif p.exists():
            p.unlink()
        self.send(200, {"ok": True, "deleted": not text.strip()})

    def POST_api_personas(self, q):
        d = json.loads(self.body() or "{}")
        n = len(sim.missing_persona_ids(sim.load("prompts.json")))
        if not n:
            raise ValueError("no missing personas: every id in prompts.json persona_groups has a file")
        start_job("generate personas", n, lambda prog: sim.generate_personas(int(d.get("seed", 1)), prog))
        self.send(202, {"ok": True})

    def POST_api_run(self, q):
        d = json.loads(self.body())
        name, kind, seed = d["name"], d["kind"], int(d["seed"])
        if not NAME.match(name):
            raise ValueError("run name: letters, digits, _ and - only")
        if kind not in ("plan", "nodecision", "plan_nosurprises"):
            raise ValueError("unknown kind")
        sets, dset = sim.decision_sets(), d.get("decisions", "")
        if dset not in sets:
            raise ValueError(f"unknown decision set {dset!r}")
        sim.load_personas()  # fail now, not mid-run, if a persona file is broken
        if kind != "nodecision" and not budget(sets[dset], sim.load("world.json"))["ok"]:
            raise ValueError(f"{dset or 'decisions.json'} is over budget or off the menu; see the budget panel")
        start_job(f"run {name}", 0, lambda prog: sim.run(name, kind, seed, prog, dset))
        self.send(202, {"ok": True})

    def GET_api_job(self, q):
        self.send(200, JOB)

    def GET_api_run(self, q):
        name, f = q.get("name", ""), q.get("file", "")
        if not NAME.match(name) or f not in RUN_FILES:
            raise ValueError("bad run or file")
        p = sim.RUNS / name / f
        if not p.exists():
            return self.send(404, {"error": "no such file"})
        self.send(200, p.read_bytes(), "application/x-ndjson" if f.endswith("l") else "application/json")

    def GET_api_stats(self, q):
        names = [n for n in q.get("runs", "").split(",") if NAME.match(n) and (sim.RUNS / n / "run.json").exists()]
        if not names:
            raise ValueError("pick at least one run")
        s = stats.summarize(names)
        s["brief"] = stats.brief_md(s)
        self.send(200, s)

    def POST_api_check(self, q):
        if not CHECK.exists():
            raise ValueError(f"check.py not found at {CHECK}")
        r = subprocess.run([sys.executable, str(CHECK), str(sim.ROOT)], capture_output=True, text=True, timeout=120)
        self.send(200, {"output": r.stdout + r.stderr, "code": r.returncode})

    def log_message(self, fmt, *args):  # quiet: the dashboard polls every second
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"dashboard: http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
