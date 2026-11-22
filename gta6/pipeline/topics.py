"""Stage 1: find what's trending and turn it into ranked topic ideas."""
import sys
from datetime import date, datetime, timedelta, timezone

import requests

from .common import ROOT, channel, env, load_config, log, made_videos, write_json
from .llm import gemini, prompt


def ytdlp_signals(cfg):
    """No-key fallback: newest YouTube uploads per query via yt-dlp search."""
    import json as _json
    from .common import run
    out = []
    from urllib.parse import quote_plus
    for q in cfg["youtube_search_queries"]:
        # YouTube search filtered to videos uploaded this week; plain search as fallback
        targets = [f"https://www.youtube.com/results?search_query={quote_plus(q)}&sp=EgQIAxAB", f"ytsearch20:{q}"]
        raw = ""
        for t in targets:
            try:
                raw = run([sys.executable, "-m", "yt_dlp", t, "--dump-json", "--flat-playlist",
                           "--playlist-end", "20", "--no-warnings"])
                break
            except RuntimeError as e:
                log(f"yt-dlp search failed for {t!r}: {str(e)[-200:]}")
        for line in raw.splitlines():
            r = _json.loads(line)
            views = r.get("view_count")
            out.append(f"YT [{q}] {r.get('title', '')} ({r.get('channel') or r.get('uploader', '')}"
                       + (f", {views:,} views" if views else "") + ")")
    return out


def youtube_signals(cfg):
    key = env("YOUTUBE_API_KEY", required=False)
    if not key:
        log("No YOUTUBE_API_KEY; using yt-dlp search instead")
        return ytdlp_signals(cfg)
    after = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    for q in cfg["youtube_search_queries"]:  # 100 quota units each, 10,000/day free
        r = requests.get("https://www.googleapis.com/youtube/v3/search", timeout=30, params={
            "key": key, "q": q, "part": "snippet", "type": "video", "order": "viewCount",
            "publishedAfter": after, "maxResults": 15, "relevanceLanguage": cfg["relevance_language"]})
        r.raise_for_status()
        for it in r.json().get("items", []):
            out.append(f"YT [{q}] {it['snippet']['title']} ({it['snippet']['channelTitle']})")
    return out


def reddit_signals(cfg):
    out = []
    for sub in cfg["reddit_subs"]:
        out += _reddit_sub(dict(cfg, reddit_sub=sub))
    return out


def _reddit_sub(cfg):
    r = requests.get(f"https://www.reddit.com/r/{cfg['reddit_sub']}/top.json",
                     params={"t": "week", "limit": 40}, timeout=30,
                     headers={"User-Agent": "gta6-topic-finder/0.1"})
    if r.status_code == 200:
        return [f"r/{cfg['reddit_sub']} ({c['data']['score']} pts) {c['data']['title']}"
                for c in r.json()["data"]["children"]]
    # JSON endpoint often 403s without login; the RSS feed usually still works
    import re
    import xml.etree.ElementTree as ET
    r = requests.get(f"https://www.reddit.com/r/{cfg['reddit_sub']}/top/.rss", params={"t": "week", "limit": 40},
                     timeout=30, headers={"User-Agent": "Mozilla/5.0 (Macintosh) gta6-topic-finder/0.1"})
    if r.status_code != 200:
        log(f"Reddit returned {r.status_code} (JSON and RSS), skipping")
        return []
    ns = {"a": "http://www.w3.org/2005/Atom"}
    titles = [e.findtext("a:title", "", ns) for e in ET.fromstring(r.content).findall("a:entry", ns)]
    return [f"r/{cfg['reddit_sub']} top this week: " + re.sub(r"\s+", " ", t) for t in titles if t]


def main(args):
    cfg = load_config()
    signals = youtube_signals(cfg) + reddit_signals(cfg)
    if not signals:
        log("No live trend signals; planning from launch-month search demand instead. Add YOUTUBE_API_KEY for better topics.")
        signals = ["(no live data) GTA 6 launched 19 Nov 2026; launch-month searches: money methods, best cars, "
                   "hidden locations, easter eggs, story explained, map size, PC/console performance, beginner tips"]
    done = [v["title"] for v in made_videos()]
    res = gemini(prompt("topics", signals="\n".join(signals[:120]), formats=", ".join(cfg["formats"]),
                        language=cfg["language"], audience=cfg["audience"], done=", ".join(done) or "none"))
    out = ROOT / "topics" / channel() / f"{date.today().isoformat()}.json"
    write_json(out, {"signals": signals, **res})
    for i, t in enumerate(res["topics"], 1):
        print(f"{i}. [{t['score']}] ({t['format']}) {t['title']}\n   {t['angle']}")
    print(f"\nSaved {out}. Next: python -m pipeline -c {channel()} script --from-topics 3   (or script \"<title>\" --format <f>)")
