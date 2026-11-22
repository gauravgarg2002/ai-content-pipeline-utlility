"""Stage 4: find and download source gameplay (video only, 720p) with yt-dlp."""
import sys
import json

from .research import ytdlp_auth
from .common import channel, CACHE, load_config, log, read_json, require, run, video_dir, write_json


def search(query, n=6):
    out = run([sys.executable, "-m", "yt_dlp", f"ytsearch{n}:{query}", "--dump-json", "--flat-playlist", "--no-warnings"])
    return [json.loads(l) for l in out.splitlines() if l.strip()]


def download(vid):
    path = CACHE / "sources" / f"{vid}.mp4"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        log(f"Downloading {vid}")
        run([sys.executable, "-m", "yt_dlp", f"https://www.youtube.com/watch?v={vid}",
             "-f", "bv*[height<=720][ext=mp4]/bv*[height<=720]", "--remux-video", "mp4",
             "-o", str(path), "--no-warnings", "--no-playlist", "--sleep-requests", "1", *ytdlp_auth()])
    return path


def main(args):
    vdir = video_dir(args.video)
    require(vdir, "approved_script", "Script")
    cfg = load_config()
    s = read_json(vdir / "script.json")
    blocked = {c.lower() for c in cfg["blocked_source_channels"]}
    picked, channels = [], set()
    for q in s["source_queries"]:
        for r in search(q):
            ch = (r.get("channel") or r.get("uploader") or "").strip()
            dur = r.get("duration") or 0
            if not ch or ch.lower() in blocked or ch in channels:
                continue  # one video per channel spreads footage across creators
            if dur and (dur < 120 or dur > cfg["max_source_duration_min"] * 60):
                continue
            channels.add(ch)
            picked.append({"id": r["id"], "url": f"https://www.youtube.com/watch?v={r['id']}",
                           "title": r.get("title", ""), "channel": ch, "query": q})
            break
        if len(picked) >= cfg["max_sources_per_video"]:
            break
    if len(picked) < cfg["min_sources"]:
        raise SystemExit(f"Only {len(picked)} distinct sources found; need {cfg['min_sources']}. Add source_queries.")
    for p in picked:
        p["path"] = str(download(p["id"]))
    write_json(vdir / "sources.json", picked)
    print(f"{len(picked)} sources from {len(channels)} channels. Next: python -m pipeline -c {channel()} index {vdir.name}")
