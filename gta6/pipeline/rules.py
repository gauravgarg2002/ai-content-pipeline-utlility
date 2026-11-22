"""Footage rules, enforced in code. Turns LLM picks into an edit decision list (EDL).

1. no segment longer than max_segment_sec from one source clip
2. at least min_sources distinct sources in the video
3. no source more than max_source_share of the runtime
4. no scene used twice
"""
from collections import defaultdict

EFFECTS = ["zoom_in", "zoom_out", "pan_left", "pan_right"]


class RuleError(Exception):
    pass


def build_edl(beats, timing, picks, catalog, cfg):
    scenes = {s["id"]: s for s in catalog}
    by_beat = {p["beat"]: p["scenes"] for p in picks}
    runtime = sum(t["video_dur"] for t in timing)
    cap = cfg["max_source_share"] * runtime
    max_seg, min_seg = cfg["max_segment_sec"], cfg["min_segment_sec"]
    used, share, edl = set(), defaultdict(float), []
    fx = 0

    def take(sid, need):
        s = scenes.get(sid)
        if not s or sid in used:
            return 0.0
        room = cap - share[s["src"]]
        length = min(s["end"] - s["start"], max_seg, need, room)
        if length < min(min_seg, need):
            return 0.0
        used.add(sid)
        share[s["src"]] += length
        return length

    for b, t in zip(beats, timing):
        need = t["video_dur"]
        segs = []
        candidates = list(by_beat.get(b["id"], []))
        # fallback: unused scenes from the least-used sources
        fallback = sorted((s for s in catalog if s["id"] not in used),
                          key=lambda s: (share[s["src"]], -(s.get("quality") or 0)))
        for sid in candidates + [s["id"] for s in fallback]:
            if need <= 0.05:
                break
            got = take(sid, need)
            if got:
                s = scenes[sid]
                segs.append({"beat": b["id"], "scene": sid, "src": s["src"], "start": s["start"],
                             "dur": round(got, 3), "effect": EFFECTS[fx % len(EFFECTS)]})
                fx += 1
                need -= got
        if need > 0.05:
            raise RuleError(f"Beat {b['id']}: not enough footage under the rules ({need:.1f}s short). "
                            "Add sources (python -m pipeline source) or lower max_source_share.")
        if b.get("onscreen"):
            segs[0]["callout"] = b["onscreen"]
        edl += segs
    validate(edl, runtime, cfg)
    return edl


def validate(edl, runtime, cfg):
    srcs = defaultdict(float)
    for e in edl:
        if e["dur"] > cfg["max_segment_sec"] + 1e-6:
            raise RuleError(f"Segment {e['scene']} is {e['dur']}s (> {cfg['max_segment_sec']}s)")
        srcs[e["src"]] += e["dur"]
    if len(srcs) < cfg["min_sources"]:
        raise RuleError(f"Only {len(srcs)} sources used; need {cfg['min_sources']}.")
    worst = max(srcs.values()) / runtime
    if worst > cfg["max_source_share"] + 0.01:
        raise RuleError(f"One source is {worst:.0%} of runtime (max {cfg['max_source_share']:.0%}).")
    scenes = [e["scene"] for e in edl]
    if len(scenes) != len(set(scenes)):
        raise RuleError("A scene is used twice.")
    return {s: round(d / runtime, 3) for s, d in srcs.items()}
