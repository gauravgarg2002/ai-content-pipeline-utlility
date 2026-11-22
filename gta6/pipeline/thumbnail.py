"""Stage 8: thumbnail (game frame + big text) and YouTube metadata with credits."""
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from .assemble import font
from .common import channel, load_config, read_json, run, video_dir, write_json


def best_frame(vdir, edl, catalog, k):
    q = {c["id"]: c.get("quality") or 0 for c in catalog}
    early = [e for e in edl if e["beat"] <= 5] or edl
    seg = max(early, key=lambda e: q.get(e["scene"], 0))
    src = {s["id"]: s["path"] for s in read_json(vdir / "sources.json")}[seg["src"]]
    out = vdir / "work" / "thumb_base.jpg"
    run(["ffmpeg", "-y", "-ss", str(seg["start"] + min(1.0, seg["dur"] / 2)), "-i", src, "-frames:v", "1",
         "-vf", f"crop=iw*{k}:ih*{k},scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720", str(out)])
    return out


def wrap(text, n=2):
    words = text.split()
    per = max(1, -(-len(words) // n))
    return [" ".join(words[i:i + per]) for i in range(0, len(words), per)]


def make_thumbnail(base, text, out, fnt):
    img = ImageEnhance.Contrast(Image.open(base).convert("RGB")).enhance(1.25)
    shade = Image.new("L", img.size)
    ImageDraw.Draw(shade).rectangle([0, 0, 760, 720], fill=150)
    img.paste(Image.new("RGB", img.size, "black"), mask=shade.point(lambda v: v))
    d = ImageDraw.Draw(img)
    lines = wrap(text.upper())
    size = 150 if max(len(l) for l in lines) <= 9 else 110
    f = ImageFont.truetype(fnt, size) if fnt else ImageFont.load_default(size)
    y = 360 - (len(lines) * (size + 10)) // 2
    for i, line in enumerate(lines):
        d.text((50, y), line, font=f, fill="#FFE600" if i == 0 else "white", stroke_width=8, stroke_fill="black")
        y += size + 10
    img.save(out, quality=92)


def chapters(beats, timing):
    out = []
    for b, t in zip(beats, timing):
        if b.get("chapter") or not out:
            m, s = divmod(int(t["start"]), 60)
            out.append(f"{m}:{s:02} {b.get('chapter') or 'Intro'}")
    if out:
        out[0] = "0:00 " + out[0].split(" ", 1)[1]
    return out


def main(args):
    vdir = video_dir(args.video)
    cfg = load_config()
    s = read_json(vdir / "script.json")
    edl = read_json(vdir / "edl.json")
    timing = read_json(vdir / "timing.json")
    base = best_frame(vdir, edl, read_json(vdir / "work" / "catalog.json"), cfg["crop_keep"])
    make_thumbnail(base, s["thumbnail_text"], vdir / "thumbnail.jpg", font(cfg))
    used = {e["src"] for e in edl}
    credits = list(dict.fromkeys(f"- {x['channel']}: {x['url']}" for x in read_json(vdir / "sources.json") if x["id"] in used))
    links = [f"- {l['label']}: {l['url']}" for l in cfg.get("affiliate_links", []) if l.get("url")]
    aff = ["Links:", *links, cfg["affiliate_disclosure"], ""] if links else []
    desc = "\n".join([s["description_summary"], "", *aff, "Chapters:", *chapters(s["beats"], timing), "",
                      "Footage credits:", *credits, "", cfg["credit_line"]])
    write_json(vdir / "metadata.json", {"title": s["title"], "description": desc, "tags": s["tags"][:15]})
    print(f"Thumbnail + metadata ready. Watch final.mp4, then: python -m pipeline -c {channel()} approve {vdir.name} final")
