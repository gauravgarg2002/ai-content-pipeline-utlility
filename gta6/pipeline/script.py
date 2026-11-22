"""Stage 2: write the script. Produces script.json + script.md for review."""
from .common import ROOT, channel, load_config, log, new_video_dir, made_videos, read_json, set_status, write_json
from .llm import gemini, prompt


def to_markdown(s):
    lines = [f"# {s['title']}", "", f"Alternatives: {' | '.join(s.get('title_alternatives', []))}",
             f"Thumbnail text: **{s['thumbnail_text']}**", "", s["description_summary"], ""]
    for b in s["beats"]:
        if b.get("chapter"):
            lines += [f"## {b['chapter']}", ""]
        cite = f" [{', '.join(map(str, b['sources']))}]" if b.get("sources") else ""
        lines.append(f"**{b['id']}.** {b['caption']}{cite}")
        lines.append(f"   _visual: {b['visual_need']}_" + (f" · callout: **{b['onscreen']}**" if b.get("onscreen") else ""))
        lines.append("")
    words = sum(len(b["caption"].split()) for b in s["beats"])
    unsourced = sum(1 for b in s["beats"] if not b.get("sources"))
    lines.append(f"---\n{len(s['beats'])} beats, {words} words, about {words / 150:.1f} min. "
                 f"{unsourced} beats cite no source (should be opinion/general only).")
    if s.get("research"):
        lines += ["", "Sources used for game facts:"] + [f"{r['n']}. {r['title']} ({r['channel']}) {r['url']}" for r in s["research"]]
    return "\n".join(lines)


TTS_RULES = {
    "devanagari": "In 'tts', write Hindi words in Devanagari and English/game terms in Latin script; 'caption' stays Roman Hinglish.",
    "latin": "'tts' is identical to 'caption'.",
}


def write_one(cfg, topic, fmt, search_query, note=""):
    from .research import gather
    wpm = cfg["words_per_minute"]
    lo, hi = cfg["target_minutes"]
    notes, research = gather(search_query or topic)
    if not research:
        raise SystemExit(f"No caption sources found for {topic!r}; skipping it rather than writing an unsourced script.")
    s = gemini(prompt("script", topic=topic, format=fmt, search_query=search_query or topic, notes=notes,
                      language=cfg["language"], audience=cfg["audience"], tts_rule=TTS_RULES[cfg["tts_script"]],
                      words_min=str(lo * wpm), words_max=str(hi * wpm))
               + (f"\n\nEditor feedback on the previous draft, apply it: {note}" if note else ""))
    for i, b in enumerate(s["beats"], 1):
        b["id"] = i
    vdir = new_video_dir(s["title"])
    write_json(vdir / "script.json", {"topic": topic, "format": fmt, "search_query": search_query,
                                      "research": research, **s})
    s["research"] = research
    (vdir / "script.md").write_text(to_markdown(s))
    set_status(vdir, approved_script=False, approved_final=False)
    words = sum(len(b["caption"].split()) for b in s["beats"])
    if words < lo * wpm * 0.85:
        log(f"Script is short ({words} words). Consider regenerating.")
    print(f"Wrote {vdir.name}/script.md ({words} words)")
    return vdir


def main(args):
    cfg = load_config()
    if args.from_topics:
        files = sorted((ROOT / "topics" / channel()).glob("*.json"))
        if not files:
            raise SystemExit("No topics yet. Run: python -m pipeline topics")
        done = {v.get("topic") for v in made_videos()}
        dirs = []
        for t in [t for t in read_json(files[-1])["topics"] if t["title"] not in done]:
            if len(dirs) >= args.from_topics:
                break
            try:
                dirs.append(write_one(cfg, t["title"], t["format"], t.get("search_query", "")))
            except SystemExit as e:
                if "No caption sources" not in str(e):
                    raise
                log(f"{e} Trying the next topic.")
    elif args.topic:
        dirs = [write_one(cfg, args.topic, args.format, args.search_query)]
    else:
        raise SystemExit("Give a topic, or --from-topics N")
    print("\nReview each script.md, then: python -m pipeline -c " + channel() + " approve <folder> script")
    for d in dirs:
        print("  " + d.name)
