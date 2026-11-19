"""Spike: Kokoro speed and quality on a GitHub CPU runner.
Reads the first beats of week 1 scripts; writes wavs and timings."""
import json, time, os, soundfile as sf
from kokoro import KPipeline

SAMPLES = [
    ("en", "a", "af_heart", "content/a-maps-data/2026-11-20-greenland-vs-africa-14x/script.json", 3),
    ("en", "a", "am_michael", "content/c-pilot-epics-en/2026-11-20-mahabharata-family-tree/script.json", 2),
    ("hi", "h", "hf_alpha", "content/c-pilot-horror-hi/2026-11-20-saamne-wali-khidki/script.json", 1),
    ("hi", "h", "hm_omega", "content/c-pilot-horror-hi/2026-11-20-saamne-wali-khidki/script.json", 1),
]
os.makedirs("renders/smoke", exist_ok=True)
rows, pipes = [], {}
for lang, code, voice, path, n in SAMPLES:
    beats = json.load(open(path))["beats"][:n]
    text = " ".join(b["narration"].replace("\n", " ") for b in beats)
    if code not in pipes:
        t = time.time(); pipes[code] = KPipeline(lang_code=code); load = time.time() - t
    else:
        load = 0.0
    t = time.time()
    audio = [a for _, _, a in pipes[code](text, voice=voice)]
    import numpy as np
    wav = np.concatenate(audio); gen = time.time() - t
    secs = len(wav) / 24000
    out = f"renders/smoke/kokoro_{voice}.wav"; sf.write(out, wav, 24000)
    rows.append({"model": "kokoro", "voice": voice, "lang": lang, "audio_s": round(secs, 1), "gen_s": round(gen, 1), "rtf": round(gen / secs, 2), "load_s": round(load, 1)})
json.dump(rows, open("renders/smoke/kokoro.json", "w"), indent=2)
with open(os.environ.get("GITHUB_STEP_SUMMARY", "/dev/null"), "a") as f:
    f.write("\n### Kokoro\n| voice | lang | audio s | generate s | real-time factor |\n|---|---|---|---|---|\n")
    for r in rows: f.write(f"| {r['voice']} | {r['lang']} | {r['audio_s']} | {r['gen_s']} | {r['rtf']} |\n")
print(json.dumps(rows, indent=2))
