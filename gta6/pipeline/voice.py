"""Stage 3: narration with Edge TTS (free), beat timings and captions."""
import asyncio

import edge_tts

from .common import channel, duration, load_config, read_json, require, run, write_json, log


async def _tts(text, path, voice, rate):
    await edge_tts.Communicate(text, voice, rate=rate).save(str(path))


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def captions(beats, timing, chunk_words=8):
    out, n = [], 1
    for b, t in zip(beats, timing):
        words = b["caption"].split()
        chunks = [words[i:i + chunk_words] for i in range(0, len(words), chunk_words)]
        span = t["end"] - t["start"]
        total = max(len(words), 1)
        cursor = t["start"]
        for c in chunks:
            d = span * len(c) / total
            out.append(f"{n}\n{srt_time(cursor)} --> {srt_time(cursor + d)}\n{' '.join(c)}\n")
            cursor += d
            n += 1
    return "\n".join(out)


def main(args):
    from .common import video_dir
    vdir = video_dir(args.video)
    require(vdir, "approved_script", "Script")
    cfg = load_config()
    s = read_json(vdir / "script.json")
    work = vdir / "work"
    gap = cfg["beat_gap_sec"]
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(gap), str(work / "gap.wav")])
    parts, timing, t = [], [], 0.0
    for b in s["beats"]:
        mp3 = work / f"beat_{b['id']:03}.mp3"
        wav = work / f"beat_{b['id']:03}.wav"
        if not wav.exists():
            log(f"TTS beat {b['id']}/{len(s['beats'])}")
            asyncio.run(_tts(b["tts"], mp3, cfg["tts_voice"], cfg["tts_rate"]))
            run(["ffmpeg", "-y", "-i", str(mp3), "-ar", "48000", "-ac", "1", str(wav)])
        d = duration(wav)
        timing.append({"beat": b["id"], "start": round(t, 3), "end": round(t + d, 3)})
        parts += [wav, work / "gap.wav"]
        t += d + gap
    lst = work / "voice_list.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(vdir / "voice.wav")])
    # beat durations include the trailing gap so video and audio line up exactly
    for i, tm in enumerate(timing):
        tm["video_dur"] = round((timing[i + 1]["start"] if i + 1 < len(timing) else t) - tm["start"], 3)
    write_json(vdir / "timing.json", timing)
    (vdir / "captions.srt").write_text(captions(s["beats"], timing))
    print(f"Voice: {t / 60:.1f} min. Next: python -m pipeline -c {channel()} source {vdir.name}")
