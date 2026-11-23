"""Stage 5: split each source into scenes and tag them with Gemini vision. Cached per source."""
from pathlib import Path

from scenedetect import ContentDetector, detect

from .common import channel, CACHE, duration, load_config, log, read_json, run, video_dir, write_json
from .llm import gemini, prompt

BATCH = 10  # frames per vision call; keeps free-tier requests low


def scenes_for(src, cfg):
    out = CACHE / "scenes" / f"{src['id']}.json"
    if out.exists():
        return read_json(out)
    log(f"Detecting scenes in {src['id']}")
    raw = [(a.get_seconds(), b.get_seconds()) for a, b in detect(src["path"], ContentDetector(threshold=27))]
    if not raw:
        raw = [(0.0, duration(src["path"]))]
    scenes = []
    for a, b in raw:
        if b - a < cfg["min_segment_sec"]:
            continue
        step = cfg["max_segment_sec"]
        while a < b - cfg["min_segment_sec"]:  # long scenes become several <=15s scenes
            scenes.append({"start": round(a, 2), "end": round(min(a + step, b), 2)})
            a += step
    cap = cfg.get("max_scenes_per_source", 0)
    if cap and len(scenes) > cap:  # long videos: sample evenly so tagging fits the free quota
        step = len(scenes) / cap
        scenes = [scenes[int(i * step)] for i in range(cap)]
    frames_dir = CACHE / "frames" / src["id"]
    frames_dir.mkdir(parents=True, exist_ok=True)
    for i, sc in enumerate(scenes):
        sc["id"] = f"{src['id']}_{i:04}"
        sc["src"] = src["id"]
        sc["frame"] = str(frames_dir / f"{i:04}.jpg")
        if not Path(sc["frame"]).exists():
            run(["ffmpeg", "-y", "-ss", str((sc["start"] + sc["end"]) / 2), "-i", src["path"],
                 "-frames:v", "1", "-vf", "scale=480:-2", "-q:v", "4", sc["frame"]])
    for i in range(0, len(scenes), BATCH):
        batch = scenes[i:i + BATCH]
        log(f"Tagging {src['id']} scenes {i}-{i + len(batch) - 1} of {len(scenes)}")
        res = gemini(prompt("tag_scenes"), images=[Path(s["frame"]) for s in batch], temperature=0.2)
        for f in res.get("frames", []):
            if 0 <= f["i"] < len(batch):
                batch[f["i"]].update({k: f.get(k) for k in ("desc", "tags", "facecam", "overlay", "non_gameplay", "quality")})
    write_json(out, scenes)
    return scenes


def main(args):
    vdir = video_dir(args.video)
    cfg = load_config()
    catalog = []
    for src in read_json(vdir / "sources.json"):
        catalog += scenes_for(src, cfg)
    from PIL import Image, ImageStat
    def bright(sc):  # mean luma of the scene's sample frame; very dark shots read badly on phones
        try:
            return ImageStat.Stat(Image.open(sc["frame"]).convert("L")).mean[0]
        except Exception:
            return 255
    # advertiser-friendly: no title cards or intimate/sexual shots (Rockstar trailers have both)
    unsafe = ("intimate", "sex", "sexual", "making out", "kissing", "nude", "naked", "topless", "lingerie",
              "strip club", "stripper", "suggestive", "in bed", "lying in bed", "bedroom scene", "twerk",
              "bikini", "swimsuit", "swimwear", "fishnet", "thong", "cleavage", "dancer", "dancing", "pole dance", "revealing",
              "rockstar games presents", "title card", "logo", "text reads", "text reading", "on-screen text", "credits")
    def safe(sc):
        text = (sc.get("desc", "") + " " + " ".join(sc.get("tags") or [])).lower()
        return not any(w in text for w in unsafe) and sc["id"] not in cfg.get("blocked_scenes", [])
    usable = [s for s in catalog if s.get("desc") and not s.get("facecam") and not s.get("non_gameplay")
              and not s.get("overlay") and safe(s)
              and (s.get("quality") or 0) >= 3 and bright(s) >= cfg.get("min_scene_brightness", 40)]
    write_json(vdir / "work" / "catalog.json", usable)
    print(f"{len(usable)} usable scenes of {len(catalog)}. Next: python -m pipeline -c {channel()} match {vdir.name}")
