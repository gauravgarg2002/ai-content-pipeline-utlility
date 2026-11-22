"""Ground scripts in real facts: captions of the top YouTube videos on the topic.

Gemini's training predates GTA 6, so without this it would invent game details.
Free: yt-dlp fetches auto-captions only (no video download).
"""
import json
import re
import sys
import tempfile
from pathlib import Path

from .common import CACHE, log, run

MAX_WORDS_PER_SOURCE = 2500


def clean_vtt(text):
    lines, seen = [], set()
    for line in text.splitlines():
        line = re.sub(r"<[^>]+>", "", line).strip()
        if not line or "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:")) or line.isdigit():
            continue
        if line not in seen:  # auto-captions repeat each line several times
            seen.add(line)
            lines.append(line)
    return " ".join(lines)


def search(query, n=8):
    raw = run([sys.executable, "-m", "yt_dlp", f"ytsearch{n}:{query}", "--dump-json", "--flat-playlist", "--no-warnings"])
    return [json.loads(l) for l in raw.splitlines() if l.strip()]


def ytdlp_auth():
    """Optional: use your browser's YouTube login (config ytdlp_cookies_browser, e.g. "chrome")
    if YouTube keeps rate-limiting anonymous requests."""
    from .common import load_config
    b = load_config().get("ytdlp_cookies_browser", "")
    return ["--cookies-from-browser", b] if b else []


def captions(video_id):
    cache = CACHE / "captions" / f"{video_id}.txt"
    if cache.exists():
        return cache.read_text()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            run([sys.executable, "-m", "yt_dlp", f"https://www.youtube.com/watch?v={video_id}", "--skip-download",
                 "--write-auto-subs", "--write-subs", "--sub-langs", "en,en-orig,hi",  # not en.*: that pulls
                 "--sub-format", "vtt", "--sleep-subtitles", "3",                    # dozens of translated tracks
                 "-o", f"{tmp}/%(id)s.%(ext)s", "--no-warnings", *ytdlp_auth()])
        except RuntimeError as e:
            if "429" in str(e):
                raise SystemExit("YouTube is rate-limiting caption downloads (429). Wait 30-60 min, or set "
                                 "ytdlp_cookies_browser to \"chrome\" in config.json to use your logged-in browser.")
            log(f"No captions for {video_id}: {str(e)[-150:]}")
            return ""
        files = sorted(Path(tmp).glob("*.vtt"), key=lambda p: (".en" not in p.name, p.name))
        text = clean_vtt(files[0].read_text(errors="ignore")) if files else ""
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(text)
    return text


NOTES_PROMPT = """Watch this GTA 6 video. Write factual notes of everything the video shows or says about the game:
names of places, missions, characters, vehicles, weapons, prices, money amounts, mechanics, steps, tips,
and story events, with rough timestamps. Separate what is shown on screen from what the creator only
claims or speculates. Plain text, up to 900 words. No opinions of your own."""


def video_notes(video_id):
    """Facts from a video via Gemini (no request from this Mac to YouTube). Cached."""
    from .llm import gemini_video
    cache = CACHE / "notes" / f"{video_id}.txt"
    if cache.exists():
        return cache.read_text()
    text = gemini_video(NOTES_PROMPT, f"https://www.youtube.com/watch?v={video_id}")
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(text)
    return text


def gather(query, max_sources=4):
    """Return (notes_text, sources) for the prompt and script.json."""
    notes, sources = [], []
    try:
        results = search(query)
    except RuntimeError as e:
        log(f"Research search failed: {str(e)[-200:]}")
        return "", []
    for r in results:
        if len(sources) >= max_sources:
            break
        if (r.get("duration") or 0) > 3 * 3600:
            continue  # skip multi-hour livestreams
        from .common import load_config
        if load_config().get("research_mode", "gemini") == "captions":
            text = captions(r["id"])
        else:
            try:
                text = video_notes(r["id"])
            except RuntimeError as e:
                log(f"Gemini could not watch {r['id']}: {str(e)[-150:]}")
                continue
        if len(text.split()) < 150:
            continue
        words = text.split()[:MAX_WORDS_PER_SOURCE]
        n = len(sources) + 1
        sources.append({"n": n, "id": r["id"], "title": r.get("title", ""),
                        "channel": r.get("channel") or r.get("uploader", ""),
                        "url": f"https://www.youtube.com/watch?v={r['id']}"})
        notes.append(f"[Source {n}] {r.get('title', '')} ({sources[-1]['channel']})\n{' '.join(words)}")
    log(f"Research: {len(sources)} caption sources for {query!r}")
    return "\n\n".join(notes), sources
