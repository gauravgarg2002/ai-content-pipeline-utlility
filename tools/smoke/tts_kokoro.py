"""Spike: Kokoro on a GitHub CPU runner.
v2: Hindi is split into sentences ourselves (Kokoro does not treat the
danda as a sentence end), voiced one sentence at a time, and joined with
explicit pauses."""
import json, os, re, time
import numpy as np, soundfile as sf
from kokoro import KPipeline

SR = 24000
HORROR = "content/c-pilot-horror-hi/2026-11-20-saamne-wali-khidki/script.json"
SENT_PAUSE, PARA_PAUSE = 0.40, 0.80

def sentences(paragraph):
    parts = re.split(r"(?<=[।?!.])\s+", paragraph.strip())
    return [p for p in parts if p.strip()]

def speak(pipe, text, voice, speed):
    chunks = [a for _, _, a in pipe(text, voice=voice, speed=speed)]
    return np.concatenate(chunks) if chunks else np.zeros(0, dtype=np.float32)

def voice_hindi(pipe, text, voice, speed=0.9):
    out = []
    for para in [p for p in text.split("\n\n") if p.strip()]:
        for s in sentences(para):
            out += [speak(pipe, s, voice, speed), np.zeros(int(SENT_PAUSE * SR), dtype=np.float32)]
        out.append(np.zeros(int((PARA_PAUSE - SENT_PAUSE) * SR), dtype=np.float32))
    return np.concatenate(out)

os.makedirs("renders/smoke", exist_ok=True)
text = json.load(open(HORROR))["beats"][0]["narration"]
t = time.time(); pipe = KPipeline(lang_code="h"); load = time.time() - t
rows = []
for voice in ["hf_alpha", "hm_omega"]:
    t = time.time(); wav = voice_hindi(pipe, text, voice); gen = time.time() - t
    secs = len(wav) / SR
    sf.write(f"renders/smoke/kokoro_{voice}_v2.wav", wav, SR)
    rows.append({"model": "kokoro-v2", "voice": voice, "lang": "hi", "words": len(text.split()),
                 "audio_s": round(secs, 1), "gen_s": round(gen, 1), "rtf": round(gen / secs, 2),
                 "words_per_s": round(len(text.split()) / secs, 2), "load_s": round(load, 1)})
json.dump(rows, open("renders/smoke/kokoro_v2.json", "w"), indent=2)
with open(os.environ.get("GITHUB_STEP_SUMMARY", "/dev/null"), "a") as f:
    f.write("\n### Kokoro v2 (Hindi, sentence split)\n| voice | audio s | words/s | generate s | real-time factor |\n|---|---|---|---|---|\n")
    for r in rows: f.write(f"| {r['voice']} | {r['audio_s']} | {r['words_per_s']} | {r['gen_s']} | {r['rtf']} |\n")
print(json.dumps(rows, indent=2))
