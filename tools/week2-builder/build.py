import json, os, re, sys, shutil
sys.path.insert(0, os.path.dirname(__file__))
import content_a, content_b, content_c

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # repo root
DATE = "2026-11-30"
WPS = {"en": 2.6, "hi-Latn": 2.6, "hi": 2.2}  # narration words per second
PAD_MS = 350
TARGET = {  # seconds
    ("short", "a-maps-data"): (25, 55), ("short", "b-ai-hinglish"): (25, 55),
    ("long", "a-maps-data"): (360, 540), ("long", "c-horror-hi"): (600, 900),
    ("long", "d-epics-en"): (360, 600),
}

def words(t): return len(t.replace("\n", " ").split())

def build(v, channel):
    vid = f"{DATE}-{v['slug']}"
    d = os.path.join(OUT, "content", channel, vid)
    os.makedirs(d, exist_ok=True)
    beats = []
    for i, b in enumerate(v["beats"], 1):
        bb = {"id": f"b{i:02d}", "narration": b["n"], "onScreen": b.get("s")}
        if b.get("c"): bb["claim"] = b["c"]; bb["sourceUrl"] = b["u"]
        beats.append(bb)
    srcs = sorted({b["u"] for b in v["beats"] if b.get("u")})
    w, h = (1080, 1920) if v["format"] == "short" else (1920, 1080)
    t, scenes = 0, []
    for i, b in enumerate(v["beats"], 1):
        dur = int(words(b["n"]) / WPS[v["lang"]] * 1000) + PAD_MS
        typ, props = b["v"]
        scenes.append({"id": f"s{i:02d}", "type": typ, "beatId": f"b{i:02d}", "startMs": t, "endMs": t + dur, "props": props})
        t += dur
    total_s = t / 1000
    lo, hi = TARGET[(v["format"], channel)]
    brief = {"id": vid, "channel": channel, "topic": v["topic"], "angle": v["angle"], "cluster": v["cluster"],
             "hookPattern": v["hookPattern"], "lengthBucket": f"{lo}-{hi}s", "format": v["format"], "sources": srcs}
    for k in ("publishBy", "storyMeta", "versionFollowed", "chapters"):
        if k in v: brief[k] = v[k]
    script = {"hook": v["beats"][0]["n"], "beats": beats, "title": v["title"], "description": v["description"], "tags": v["tags"]}
    fc = {"checkedOn": DATE, "checkedBy": "Claude (manual fact gate, week 2)", "beats": []}
    for i, b in enumerate(v["beats"], 1):
        if b.get("c"):
            ev = b["c"] + (" [computed from the cited figures]" if b.get("computed") else "")
            fc["beats"].append({"id": f"b{i:02d}", "verdict": "supported", "evidence": ev, "source": b["u"]})
        else:
            fc["beats"].append({"id": f"b{i:02d}", "verdict": "no-claim", "evidence": "Framing, opinion, instruction or story; no factual claim."})
    status = {"state": "draft", "reviewNote": None, "publishAt": None, "platformIds": {}}
    for name, obj in [("brief", brief), ("script", script), ("factcheck", fc), ("scenes", {"fps": 30, "width": w, "height": h, "scenes": scenes}), ("status", status)]:
        with open(os.path.join(d, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
    # human-readable review copy
    md = [f"# {v['title']}", "", f"Channel: `{channel}` · Format: {v['format']} · Est. length: {fmt(total_s)} (target {fmt(lo)} to {fmt(hi)})", ""]
    if v.get("publishBy"): md += [f"**Publish by {v['publishBy']}**, after that re-check the facts.", ""]
    if v.get("versionFollowed"): md += [f"Version followed: {v['versionFollowed']}", ""]
    md += ["## Script", ""]
    for i, b in enumerate(v["beats"], 1):
        md.append(f"**{i}.** {b['n']}")
        if b.get("s"): md.append(f"> On screen: {b['s']}")
        md.append(f"> Visual: `{b['v'][0]}`")
        if b.get("u"): md.append(f"> Source: {b['u']}")
        md.append("")
    md += ["## Post copy", "", f"Title: {v['title']}", "", f"Description: {v['description']}", "", "Tags: " + ", ".join(v["tags"]), ""]
    with open(os.path.join(d, "script.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    return {"channel": channel, "id": vid, "title": v["title"], "format": v["format"], "seconds": total_s, "range": (lo, hi),
            "hookWords": words(re.split(r"(?<=[.?!।])\s", v["beats"][0]["n"].strip())[0]), "beats": len(beats),
            "claims": sum(1 for b in v["beats"] if b.get("c")), "words": sum(words(b["n"]) for b in v["beats"]), "publishBy": v.get("publishBy")}

def fmt(s): return f"{int(s//60)}:{int(s%60):02d}"

if __name__ == "__main__":
    rows = []
    rows += [build(v, "a-maps-data") for v in content_a.VIDEOS + [content_a.LONG]]
    rows += [build(v, "b-ai-hinglish") for v in content_b.VIDEOS]
    for ep in (content_c.HORROR, content_c.EPICS):
        rows.append(build(ep, ep["channel"]))
    with open(os.path.join(OUT, "week2-index.json"), "w") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    for r in rows:
        print(f"{r['channel']:20} {r['format']:5} {fmt(r['seconds']):>6} target {fmt(r['range'][0])}-{fmt(r['range'][1])} hook {r['hookWords']:2}w claims {r['claims']:2}/{r['beats']:2} {r['id']}")
