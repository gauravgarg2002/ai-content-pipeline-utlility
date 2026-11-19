"""Voice the full horror pilot with Gemini TTS, one request per beat."""
import base64, json, os, re, sys, time, urllib.request, urllib.error, wave

KEY = os.environ["GEMINI_API_KEY"]
CFG = json.load(open("config/voices.json"))["c-pilot-horror-hi"]["primary"]
URL = f"https://generativelanguage.googleapis.com/v1beta/{CFG['model']}:generateContent"
SCRIPT = "content/c-pilot-horror-hi/2026-11-20-saamne-wali-khidki/script.json"
OUT = "renders/pilot/horror"; os.makedirs(OUT, exist_ok=True)

def tts(text):
    body = {"contents": [{"parts": [{"text": CFG["style"] + "\n\n" + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": CFG["voice"]}}}}}
    for attempt in range(4):
        req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                     headers={"x-goog-api-key": KEY, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                part = json.load(r)["candidates"][0]["content"]["parts"][0]["inlineData"]
                return base64.b64decode(part["data"]), part.get("mimeType", "")
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code in (429, 500, 503) and attempt < 3:
                print(f"HTTP {e.code}, retrying in 60 s: {msg}"); time.sleep(60); continue
            sys.exit(f"HTTP {e.code}: {msg}")

beats = json.load(open(SCRIPT))["beats"]
rows, frames, params = [], [], None
for b in beats:
    t = time.time(); data, mime = tts(b["narration"]); gen = time.time() - t
    path = f"{OUT}/{b['id']}.wav"
    if data[:4] == b"RIFF" or "wav" in mime:
        open(path, "wb").write(data)
    else:
        m = re.search(r"rate=(\d+)", mime)
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(int(m.group(1)) if m else 24000); w.writeframes(data)
    with wave.open(path) as w:
        params = params or w.getparams(); secs = w.getnframes() / w.getframerate()
    words = len(b["narration"].split())
    rows.append({"beat": b["id"], "words": words, "audio_s": round(secs, 1), "words_per_s": round(words / secs, 2), "gen_s": round(gen, 1)})
    print(rows[-1]); time.sleep(10)
json.dump(rows, open(f"{OUT}/timings.json", "w"), indent=2)
total = sum(r["audio_s"] for r in rows); words = sum(r["words"] for r in rows)
with open(os.environ.get("GITHUB_STEP_SUMMARY", "/dev/null"), "a") as f:
    f.write(f"\n### Horror pilot, Gemini {CFG['voice']}\n{len(rows)} beats, {words} words, {total/60:.1f} min of speech, {words/total:.2f} words/s\n")
