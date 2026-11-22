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


def fetch(url, path):
    """Plain HTTP download (official Rockstar CDN files)."""
    import requests
    if path.exists() and path.stat().st_size > 0:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    log(f"Downloading {url}")
    with requests.get(url, stream=True, timeout=120, headers={"User-Agent": "Mozilla/5.0"}) as r:
        r.raise_for_status()
        tmp = path.with_suffix(path.suffix + ".part")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
        tmp.rename(path)
    return path


def stills_video(zip_url, n, secs):
    """Official screenshots -> one video of slow-panning stills (one scene per still)."""
    import zipfile
    out = CACHE / "sources" / "rockstar_screens.mp4"
    if out.exists():
        return out
    z = fetch(zip_url, CACHE / "downloads" / "screens.zip")
    d = CACHE / "screens"
    d.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(z) as zf:
        names = sorted(x for x in zf.namelist() if x.lower().endswith((".jpg", ".jpeg", ".png")))
        step = max(1, len(names) // n)
        names = names[::step][:n]
        for i, nm in enumerate(names):
            (d / f"{i:03}.jpg").write_bytes(zf.read(nm))
    clips = []
    fr = int(secs * 30)
    for i, img in enumerate(sorted(d.glob("*.jpg"))):
        c = d / f"{i:03}.mp4"
        zoom = "1+0.12*on/%d" % fr if i % 2 == 0 else "1.12-0.12*on/%d" % fr
        if not c.exists():
            run(["ffmpeg", "-y", "-loop", "1", "-i", str(img), "-vf",
                 f"scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
                 f"zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1280x720:fps=30",
                 "-frames:v", str(fr), "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(c)])
        clips.append(c)
    lst = d / "list.txt"
    lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    return out


def transcode_url(url, path):
    """Stream an official 4K master straight into a 720p working copy (the 4K file never
    touches disk: the Extended Look master alone is 14 GB)."""
    if path.exists() and path.stat().st_size > 0:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".part.mp4")
    log(f"Streaming + converting to 720p: {url}")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-reconnect", "1", "-reconnect_streamed", "1",
         "-reconnect_delay_max", "10", "-i", url, "-an", "-vf", "scale=-2:720,fps=30",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", str(tmp)])
    tmp.rename(path)
    return path


def official(vdir, cfg):
    picked = []
    for src in cfg["official_sources"]:
        path = transcode_url(src["url"], CACHE / "sources" / f"{src['id']}.mp4")
        picked.append({**src, "url": src.get("page", src["url"]), "download": src["url"],
                       "channel": "Rockstar Games", "path": str(path)})
    st = cfg.get("official_stills")
    if st:
        path = stills_video(st["zip"], st["count"], st["seconds"])
        picked.append({"id": "rockstar_screens", "title": "Official GTA VI screenshots", "channel": "Rockstar Games",
                       "url": st["page"], "path": str(path)})
    write_json(vdir / "sources.json", picked)
    print(f"{len(picked)} official Rockstar sources. Next: python -m pipeline -c {channel()} index {vdir.name}")


def main(args):
    vdir = video_dir(args.video)
    require(vdir, "approved_script", "Script")
    cfg = load_config()
    if cfg.get("footage_mode") == "official":  # Rockstar CDN; no YouTube requests at all
        return official(vdir, cfg)
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
