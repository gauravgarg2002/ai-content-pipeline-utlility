"""Voice the full epics pilot with Kokoro, one beat at a time."""
import json, os, time
import numpy as np, soundfile as sf
from kokoro import KPipeline

CFG = json.load(open("config/voices.json"))["c-pilot-epics-en"]["primary"]
SCRIPT = "content/c-pilot-epics-en/2026-11-20-mahabharata-family-tree/script.json"
OUT = "renders/pilot/epics"; os.makedirs(OUT, exist_ok=True)
SR = 24000
pipe = KPipeline(lang_code=CFG["lang_code"])
rows = []
for b in json.load(open(SCRIPT))["beats"]:
    t = time.time()
    wav = np.concatenate([a for _, _, a in pipe(b["narration"], voice=CFG["voice"], speed=CFG["speed"])])
    gen = time.time() - t
    sf.write(f"{OUT}/{b['id']}.wav", wav, SR)
    secs = len(wav) / SR; words = len(b["narration"].split())
    rows.append({"beat": b["id"], "words": words, "audio_s": round(secs, 1), "words_per_s": round(words / secs, 2), "gen_s": round(gen, 1)})
    print(rows[-1])
json.dump(rows, open(f"{OUT}/timings.json", "w"), indent=2)
total = sum(r["audio_s"] for r in rows); words = sum(r["words"] for r in rows)
with open(os.environ.get("GITHUB_STEP_SUMMARY", "/dev/null"), "a") as f:
    f.write(f"\n### Epics pilot, Kokoro {CFG['voice']}\n{len(rows)} beats, {words} words, {total/60:.1f} min of speech, {words/total:.2f} words/s\n")
