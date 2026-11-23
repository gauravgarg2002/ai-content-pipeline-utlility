"""Gemini (Google AI Studio free tier) over REST. No SDK needed.

Each model has its own free daily quota, so we try a list of models in order
(config: text_models, vision_models) and move to the next when one is used up.
"""
import base64
import json
import time

import requests

from .common import env, load_config, log

API = "https://generativelanguage.googleapis.com/v1beta"
_exhausted = set()  # models whose daily quota ran out during this run


def _call(model, body, retries):
    wait = 10
    for _ in range(retries):
        try:
            r = requests.post(f"{API}/models/{model}:generateContent",
                              params={"key": env("GEMINI_API_KEY")}, json=body, timeout=300)
        except (requests.Timeout, requests.ConnectionError) as e:  # slow/flaky API: retry, then next model
            log(f"{model} network error ({type(e).__name__}), retrying in {wait}s")
            time.sleep(wait)
            wait = min(wait * 2, 120)
            continue
        if r.status_code == 404:
            return "skip", f"{model} not available to this key"
        if r.status_code == 400:
            return "skip", f"{model} rejected the request: {r.text[:200]}"
        if r.status_code == 429 and "PerDay" in r.text:
            return "skip", f"{model} daily free quota used up"
        if r.status_code in (429, 500, 502, 503):
            log(f"{model} {r.status_code}, retrying in {wait}s")
            time.sleep(wait)
            wait = min(wait * 2, 120)
            continue
        r.raise_for_status()
        return "ok", r.json()["candidates"][0]["content"]["parts"][0]["text"]
    return "skip", f"{model} kept failing"


def gemini(prompt, images=None, as_json=True, temperature=0.7, retries=5):
    cfg = load_config()
    parts = [{"text": prompt}]
    for img in images or []:
        parts.append({"inline_data": {"mime_type": "image/jpeg",
                                      "data": base64.b64encode(img.read_bytes()).decode()}})
    body = {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"temperature": temperature}}
    if as_json:
        body["generationConfig"]["responseMimeType"] = "application/json"
    models = cfg["vision_models"] if images else cfg["text_models"]
    for model in models:
        if model in _exhausted:
            continue
        for attempt in range(3):  # a malformed/truncated JSON reply is retried, then the next model
            status, out = _call(model, body, retries)
            if status != "ok":
                break
            if not as_json:
                return out
            try:
                return json.loads(out)
            except json.JSONDecodeError as e:
                log(f"{model} returned invalid JSON ({e}); retry {attempt + 1}")
                status, out = "skip", f"{model} kept returning invalid JSON"
        log(f"{out}; trying next model")
        if "invalid JSON" not in out:
            _exhausted.add(model)
    raise SystemExit("All configured Gemini models are out of free quota for today. Quotas reset at "
                     "1:30 pm IST; re-run the same command then (finished work is cached).")


def gemini_video(prompt_text, youtube_url, max_minutes=15):
    """Gemini watches a public YouTube video itself (Google fetches it, not this Mac).
    Low media resolution + first N minutes keeps it inside free-tier token limits."""
    cfg = load_config()
    body = {"contents": [{"role": "user", "parts": [
                {"file_data": {"file_uri": youtube_url},
                 "video_metadata": {"start_offset": "0s", "end_offset": f"{max_minutes * 60}s"}},
                {"text": prompt_text}]}],
            "generationConfig": {"temperature": 0.2, "mediaResolution": "MEDIA_RESOLUTION_LOW"}}
    for model in cfg["text_models"]:
        if model in _exhausted:
            continue
        status, out = _call(model, body, retries=3)
        if status == "ok":
            return out
        log(f"{out}; trying next model")
        if "quota" in out or "not available" in out:
            _exhausted.add(model)
    raise SystemExit("All configured Gemini models are out of free quota for today. Quotas reset at "
                     "1:30 pm IST; re-run the same command then (finished work is cached).")


def list_models():
    r = requests.get(f"{API}/models", params={"key": env("GEMINI_API_KEY"), "pageSize": 200}, timeout=30)
    r.raise_for_status()
    for m in r.json().get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            print(m["name"].removeprefix("models/"))


def prompt(name, **kw):
    from .common import ROOT
    text = (ROOT / "prompts" / f"{name}.md").read_text()
    for k, v in kw.items():
        text = text.replace("{{" + k + "}}", v if isinstance(v, str) else json.dumps(v, ensure_ascii=False))
    return text
