"""Spike: Gemini free-tier text-to-speech for the Hindi horror opening.
Finds a TTS model from the live model list, so no model id is hard-coded.
The key goes in a header, never the URL, so it can't leak into logs."""
import base64, json, os, sys, time, urllib.request, urllib.error, wave

KEY = os.environ["GEMINI_API_KEY"]
BASE = "https://generativelanguage.googleapis.com/v1beta"
HORROR = "content/c-pilot-horror-hi/2026-11-20-saamne-wali-khidki/script.json"
STYLE = ("Read this Hindi horror story aloud like a skilled late-night storyteller. "
         "Speak slowly and calmly, with a quiet, eerie tone. Pause briefly at every full stop (।) "
         "and longer between paragraphs. Do not rush.\n\n")
VOICES = ["Charon", "Kore"]

def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"x-goog-api-key": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)

models = [m["name"] for m in call(f"{BASE}/models?pageSize=1000")["models"]
          if "tts" in m["name"].lower() and "generateContent" in m.get("supportedGenerationMethods", [])]
print("TTS models visible:", models)
if not models:
    sys.exit("No TTS model available on this key's free tier")
model = sorted(models, key=lambda n: ("lite" in n, "preview" in n, n))[0]
text = json.load(open(HORROR))["beats"][0]["narration"]
os.makedirs("renders/smoke", exist_ok=True)
rows = []
for voice in VOICES:
    body = {"contents": [{"parts": [{"text": STYLE + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    t = time.time()
    try:
        res = call(f"{BASE}/{model}:generateContent", body)
    except urllib.error.HTTPError as e:
        rows.append({"model": model, "voice": voice, "error": f"HTTP {e.code}: {e.read().decode()[:300]}"}); continue
    gen = time.time() - t
    part = res["candidates"][0]["content"]["parts"][0]["inlineData"]
    pcm = base64.b64decode(part["data"])
    rate = int(part.get("mimeType", "rate=24000").split("rate=")[-1].split(";")[0] or 24000)
    out = f"renders/smoke/gemini_{voice}.wav"
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm)
    secs = len(pcm) / 2 / rate
    rows.append({"model": model, "voice": voice, "words": len(text.split()), "audio_s": round(secs, 1),
                 "words_per_s": round(len(text.split()) / secs, 2), "gen_s": round(gen, 1)})
    time.sleep(15)  # stay under free-tier per-minute limits
json.dump(rows, open("renders/smoke/gemini.json", "w"), indent=2)
with open(os.environ.get("GITHUB_STEP_SUMMARY", "/dev/null"), "a") as f:
    f.write(f"\n### Gemini TTS ({model})\n| voice | audio s | words/s | generate s | error |\n|---|---|---|---|---|\n")
    for r in rows: f.write(f"| {r['voice']} | {r.get('audio_s','')} | {r.get('words_per_s','')} | {r.get('gen_s','')} | {r.get('error','')} |\n")
print(json.dumps(rows, indent=2))
sys.exit(0 if any("audio_s" in r for r in rows) else 1)
