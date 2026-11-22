"""Stage 6: LLM picks footage per beat; rules.py turns picks into a compliant EDL."""
from .common import channel, load_config, read_json, require, status, video_dir, write_json
from .llm import gemini, prompt
from .rules import build_edl, validate


def main(args):
    vdir = video_dir(args.video)
    require(vdir, "approved_script", "Script")
    cfg = load_config()
    s = read_json(vdir / "script.json")
    timing = read_json(vdir / "timing.json")
    catalog = read_json(vdir / "work" / "catalog.json")
    beats_txt = "\n".join(f"{b['id']} | {t['video_dur']:.0f}s | {b['visual_need']}" for b, t in zip(s["beats"], timing))
    cat_txt = "\n".join(f"{c['id']} | {c['src']} | {c['end'] - c['start']:.0f} | {c['desc']}" for c in catalog)
    note = status(vdir).get("edit_note", "")
    extra = f"\n\nEditor note on the previous cut, apply it: {note}" if note else ""
    picks = gemini(prompt("match", beats=beats_txt, catalog=cat_txt) + extra, temperature=0.5 if note else 0.3)["picks"]
    edl = build_edl(s["beats"], timing, picks, catalog, cfg)
    write_json(vdir / "edl.json", edl)
    shares = validate(edl, sum(t["video_dur"] for t in timing), cfg)
    print("Source shares: " + ", ".join(f"{k} {v:.0%}" for k, v in sorted(shares.items(), key=lambda x: -x[1])))
    print(f"{len(edl)} segments. Next: python -m pipeline -c {channel()} assemble {vdir.name}")
