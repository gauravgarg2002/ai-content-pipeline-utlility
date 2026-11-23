"""Voice the full horror pilot with Gemini TTS.

Free-tier limits are tight, so beats are grouped into ~300-word chunks
(about 5 requests per episode), requests are spaced 35 s apart, and
finished chunks are kept: a re-run only voices what's missing. If the
daily quota runs out, the script stops cleanly and says how far it got.
"""
import base64, json, os, re, sys, time, urllib.request, urllib.error, wave

KEY = os.environ["GEMINI_API_KEY"]
CFG = json.load(open("config/voices.json"))["c-horror-hi"]["primary"]
URL = f"https://generativelanguage.googleapis.com/v1beta/{CFG['model']}:generateContent"
SCRIPT = "content/c-horror-hi/2026-11-20-saamne-wali-khidki/script.json"
OUT = "renders/pilot/horror"; os.makedirs(OUT, exist_ok=True)
MAX_WORDS, SPACING_S, RETRIES, BACKOFF_S = 320, 35, 4, 70

class QuotaExhausted(Exception): pass

def tts(text):
    body = {"contents": [{"parts": [{"text": CFG["style"] + "\n\n" + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": CFG["voice"]}}}}}
    for attempt in range(RETRIES + 1):
        req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                     headers={"x-goog-api-key": KEY, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                part = json.load(r)["candidates"][0]["content"]["parts"][0]["inlineData"]
                return base64.b64decode(part["data"]), part.get("mimeType", "")
        except urllib.error.HTTPError as e:
            msg = e.read().decode()
            if e.code == 429 and attempt < RETRIES:
                metric = re.search(r"quota_metric\W+([\w/.-]+)", msg) or re.search(r"Quota exceeded for metric: ([^,\n]+)", msg)
                print(f"429 ({metric.group(1) if metric else 'rate limit'}), waiting {BACKOFF_S} s"); time.sleep(BACKOFF_S); continue
            if e.code == 429: raise QuotaExhausted(msg[:500])
            sys.exit(f"HTTP {e.code}: {msg[:500]}")

beats = json.load(open(SCRIPT))["beats"]
chunks, cur = [], []
for b in beats:
    if cur and sum(len(x["narration"].split()) for x in cur) + len(b["narration"].split()) > MAX_WORDS:
        chunks.append(cur); cur = []
    cur.append(b)
chunks.append(cur)

done = 0
for i, ch in enumerate(chunks, 1):
    path = f"{OUT}/b{i:02d}.wav"
    if os.path.exists(path): done += 1; continue
    text = "\n\n".join(b["narration"] for b in ch)
    try:
        t = time.time(); data, mime = tts(text); gen = time.time() - t
    except QuotaExhausted as e:
        print(f"Daily quota exhausted after {done}/{len(chunks)} chunks. Re-run later to continue.\n{e}")
        break
    if data[:4] == b"RIFF" or "wav" in mime:
        open(path, "wb").write(data)
    else:
        m = re.search(r"rate=(\d+)", mime)
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(int(m.group(1)) if m else 24000); w.writeframes(data)
    with wave.open(path) as w: secs = w.getnframes() / w.getframerate()
    words = len(text.split()); done += 1
    print({"chunk": i, "beats": [b["id"] for b in ch], "words": words, "audio_s": round(secs, 1),
           "words_per_s": round(words / secs, 2), "gen_s": round(gen, 1)})
    if i < len(chunks): time.sleep(SPACING_S)

summary = f"\n### Horror pilot, Gemini {CFG['voice']}\n{done}/{len(chunks)} chunks voiced.\n"
if done == len(chunks):
    open(f"{OUT}/DONE", "w").write("ok")
else:
    summary += "Stopped at the free-tier quota. Re-run this workflow later; finished chunks are kept.\n"
open(os.environ.get("GITHUB_STEP_SUMMARY", "/dev/null"), "a").write(summary)
print(summary)
