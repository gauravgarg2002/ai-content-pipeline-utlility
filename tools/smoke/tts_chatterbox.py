"""Spike: Chatterbox Multilingual (Hindi) on a GitHub CPU runner."""
import json, time, os
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

os.makedirs("renders/smoke", exist_ok=True)
beat = json.load(open("content/c-pilot-horror-hi/2026-11-20-saamne-wali-khidki/script.json"))["beats"][0]["narration"]
text = beat.split("\n\n")[0] + " " + beat.split("\n\n")[1].split("।")[0] + "।"
t = time.time(); model = ChatterboxMultilingualTTS.from_pretrained(device="cpu"); load = time.time() - t
t = time.time(); wav = model.generate(text, language_id="hi"); gen = time.time() - t
secs = wav.shape[-1] / model.sr
ta.save("renders/smoke/chatterbox_hi.wav", wav, model.sr)
row = {"model": "chatterbox-mtl", "lang": "hi", "audio_s": round(secs, 1), "gen_s": round(gen, 1), "rtf": round(gen / secs, 2), "load_s": round(load, 1)}
json.dump([row], open("renders/smoke/chatterbox.json", "w"), indent=2)
with open(os.environ.get("GITHUB_STEP_SUMMARY", "/dev/null"), "a") as f:
    f.write(f"\n### Chatterbox Multilingual\n| lang | audio s | generate s | real-time factor | model load s |\n|---|---|---|---|---|\n| hi | {row['audio_s']} | {row['gen_s']} | {row['rtf']} | {row['load_s']} |\n")
print(row)
