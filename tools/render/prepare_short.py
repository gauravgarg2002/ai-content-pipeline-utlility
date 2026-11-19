"""Turn one video folder into render inputs: voiced audio + props for Remotion.

Usage: python tools/render/prepare_short.py content/<channel>/<video-id>
Writes render/public/<video-id>/audio.wav and props.json.
Scene timing comes from the real voice durations, not the estimates in
scenes.json. Word timings for captions come from Kokoro's token timestamps.
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf
from kokoro import KPipeline

SR, FPS = 24000, 30
BEAT_GAP_S, TAIL_S = 0.15, 0.8
PUNCT = set(".,!?;:—–-…\"'()")

vdir = sys.argv[1].rstrip("/")
vid = os.path.basename(vdir)
channel = os.path.basename(os.path.dirname(vdir))
script = json.load(open(f"{vdir}/script.json"))
board = json.load(open(f"{vdir}/scenes.json"))
cfg = json.load(open("config/voices.json"))[channel]["primary"]
pipe = KPipeline(lang_code=cfg["lang_code"])

def frames(s): return int(round(s * FPS))

audio, words, scenes, t = [], [], [], 0.0
for beat, sc in zip(script["beats"], board["scenes"]):
    start = t
    for res in pipe(beat["narration"], voice=cfg["voice"], speed=cfg.get("speed", 1.0)):
        a = res.audio
        a = a.detach().cpu().numpy() if hasattr(a, "detach") else np.asarray(a)
        dur = len(a) / SR
        toks = [tk for tk in (getattr(res, "tokens", None) or [])
                if tk.text.strip() and not all(ch in PUNCT for ch in tk.text)
                and tk.start_ts is not None and tk.end_ts is not None]
        if toks:
            for tk in toks:
                words.append({"text": tk.text, "startMs": int((t + tk.start_ts) * 1000), "endMs": int((t + tk.end_ts) * 1000)})
        else:  # fallback: spread words evenly over the chunk
            ws = res.graphemes.split()
            for i, w in enumerate(ws):
                words.append({"text": w, "startMs": int((t + dur * i / len(ws)) * 1000), "endMs": int((t + dur * (i + 1) / len(ws)) * 1000)})
        audio.append(a.astype(np.float32)); t += dur
    audio.append(np.zeros(int(BEAT_GAP_S * SR), dtype=np.float32)); t += BEAT_GAP_S
    scenes.append({"id": sc["id"], "type": sc["type"], "props": sc["props"], "onScreen": beat.get("onScreen"),
                   "from": frames(start), "durationInFrames": max(1, frames(t) - frames(start))})
audio.append(np.zeros(int(TAIL_S * SR), dtype=np.float32)); t += TAIL_S
scenes[-1]["durationInFrames"] = frames(t) - scenes[-1]["from"]

out = f"render/public/{vid}"; os.makedirs(out, exist_ok=True)
sf.write(f"{out}/raw.wav", np.concatenate(audio), SR)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{out}/raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                "-ar", "48000", f"{out}/audio.wav"], check=True)
os.remove(f"{out}/raw.wav")
props = {"id": vid, "channel": channel, "fps": FPS, "width": board["width"], "height": board["height"],
         "durationInFrames": frames(t), "audio": f"{vid}/audio.wav", "scenes": scenes, "words": words}
json.dump(props, open(f"{out}/props.json", "w"), ensure_ascii=False, indent=1)
print(f"{vid}: {t:.1f} s, {len(scenes)} scenes, {len(words)} caption words")
