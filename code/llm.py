"""Thin LLM wrapper: Vertex AI (google-genai) with the TALP key, seeded calls, and a log of every call.

The key is read from the TALP_KEY environment variable (or a git-ignored .env file at the repo root).
It is never written anywhere: check.py rejects a submission that contains it.

mock=True is for developing the pipeline only (model "mock"); hand-in runs must use Vertex.
"""
import json
import os
import random
import threading
from pathlib import Path

DEFAULT_MODEL = os.environ.get("TALP_MODEL", "gemini-3.5-flash-lite")
ROOT = Path(__file__).resolve().parent.parent


def _load_key():
    key = os.environ.get("TALP_KEY")
    env = ROOT / ".env"
    if not key and env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith("TALP_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise SystemExit("TALP_KEY is not set: run `export TALP_KEY=<your key>` (or use --mock for a dry run)")
    return key


class LLM:
    def __init__(self, seed, model=DEFAULT_MODEL, mock=False, temperature=1.0):
        self.seed, self.mock, self.temperature = seed, mock, temperature
        self.model = "mock" if mock else model
        self.calls = []
        self._lock = threading.Lock()
        if not mock:
            from google import genai
            from google.genai import types
            self._types = types
            self._client = genai.Client(  # no project, no location: the models are on the global endpoint
                vertexai=True, api_key=_load_key(),
                http_options=types.HttpOptions(retry_options=types.HttpRetryOptions(attempts=5)))

    def _log(self, persona, week, prompt, response):
        with self._lock:
            cid = f"c{len(self.calls) + 1:06d}"
            self.calls.append({"id": cid, "persona": persona, "week": week, "prompt": prompt,
                               "response": response, "model": self.model})
        return cid

    def _generate(self, prompt, schema):
        cfg = self._types.GenerateContentConfig(
            temperature=self.temperature, seed=self.seed,
            response_mime_type="application/json", response_schema=schema)
        if os.environ.get("TALP_NO_THINK") == "1":
            cfg.thinking_config = self._types.ThinkingConfig(thinking_budget=0)
        return self._client.models.generate_content(model=self.model, contents=prompt, config=cfg).text or ""

    def json(self, prompt, schema, persona=None, week=0, mock=None, tries=3):
        """Ask for JSON matching a pydantic schema. Every attempt is logged. Returns (call_id, dict)."""
        last = None
        for attempt in range(tries):
            if self.mock:
                rng = random.Random(f"{self.seed}|{persona}|{week}|{attempt}|{len(prompt)}")
                text = json.dumps(mock(rng), ensure_ascii=False)
            else:
                try:
                    text = self._generate(prompt, schema)
                except Exception as e:  # network or quota errors after the SDK's own retries
                    last = e
                    continue
            cid = self._log(persona, week, prompt, text)
            try:
                return cid, schema.model_validate_json(text).model_dump()
            except Exception as e:
                last = e
        raise RuntimeError(f"no valid answer for persona {persona} week {week}: {last}")
