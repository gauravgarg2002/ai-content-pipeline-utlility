"""Turn one video folder into render inputs: voiced audio + props for Remotion.

Usage: python tools/render/prepare.py content/<channel>/<video-id>
Writes render/public/<video-id>/audio.wav and props.json.

Voice engine comes from config/voices.json for the channel:
- kokoro: one call per beat; word timings from Kokoro's token timestamps.
- gemini: whole Short in one request (long videos in ~300-word chunks).
  Audio is cached in .voice-cache/ by a hash of the text and voice, so
  re-runs never spend quota twice. Beat boundaries are snapped to real
  pauses found with ffmpeg; word timings are spread by length inside a beat.
Scene timing always follows the real audio, not the estimates in scenes.json.
"""
import base64, hashlib, json, os, re, subprocess, sys, time, urllib.error, urllib.request, wave
import numpy as np, soundfile as sf

vdir = sys.argv[1].rstrip("/")
vid, channel = os.path.basename(vdir), os.path.basename(os.path.dirname(vdir))
script = json.load(open(f"{vdir}/script.json")); board = json.load(open(f"{vdir}/scenes.json")); brief = json.load(open(f"{vdir}/brief.json"))
CFG = json.load(open("config/voices.json")); vc = CFG[channel]["primary"]
LONG = brief["format"] == "long"
FPS = vc.get("fps", 30) if LONG else 30
CAPTIONS = not LONG
CACHE = ".voice-cache"; os.makedirs(CACHE, exist_ok=True)
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]")
PUNCT = set(".,!?;:—–-…\"'()।")
SR = 24000


def clean(s):
    if not s:
        return None
    s = EMOJI.sub("", s).strip(" ·")
    return s or None


def frames(s):
    return int(round(s * FPS))


def kokoro_voice(beats):
    from kokoro import KPipeline
    pipe = KPipeline(lang_code=vc["lang_code"])
    audio, words, bounds, t = [], [], [], 0.0
    gap = vc.get("beat_pause_s", 0.5 if LONG else 0.15)
    for b in beats:
        start = t
        for res in pipe(b["narration"].replace("\n", " "), voice=vc["voice"], speed=vc.get("speed", 1.0)):
            a = res.audio
            a = a.detach().cpu().numpy() if hasattr(a, "detach") else np.asarray(a)
            dur = len(a) / SR
            toks = [tk for tk in (getattr(res, "tokens", None) or []) if tk.text.strip() and not all(ch in PUNCT for ch in tk.text)
                    and tk.start_ts is not None and tk.end_ts is not None]
            if toks:
                words += [{"text": tk.text, "startMs": int((t + tk.start_ts) * 1000), "endMs": int((t + tk.end_ts) * 1000)} for tk in toks]
            else:
                ws = res.graphemes.split()
                words += [{"text": w, "startMs": int((t + dur * i / len(ws)) * 1000), "endMs": int((t + dur * (i + 1) / len(ws)) * 1000)}
                          for i, w in enumerate(ws)]
            audio.append(a.astype(np.float32)); t += dur
        audio.append(np.zeros(int(gap * SR), np.float32)); t += gap
        bounds.append((start, t))
    return np.concatenate(audio), words, bounds


def gemini_request(text):
    key = os.environ["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/{vc['model']}:generateContent"
    body = {"contents": [{"parts": [{"text": vc["style"] + "\n\n" + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": vc["voice"]}}}}}
    for attempt in range(5):
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"x-goog-api-key": key, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                part = json.load(r)["candidates"][0]["content"]["parts"][0]["inlineData"]
                return base64.b64decode(part["data"]), part.get("mimeType", "")
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:800]
            if e.code == 429 and ("PerDay" in msg or "free_tier_requests" in msg and "limit: 10," in msg):
                print(f"::error::Gemini free-tier daily limit reached (10 TTS requests a day). Cached audio is kept; re-run after the reset.")
                sys.exit(76)
            if e.code in (429, 500, 503) and attempt < 4:
                print(f"HTTP {e.code}, waiting 70 s ({attempt + 1}/4)", flush=True); time.sleep(70); continue
            print(f"::error::Gemini TTS HTTP {e.code}. A 429 here means the free daily quota is used up; re-run later and cached chunks are reused.\n{msg}")
            sys.exit(75)


def load_wav(path):
    with wave.open(path) as w:
        sr, n, sw = w.getframerate(), w.getnframes(), w.getsampwidth()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768 if sw == 2 else np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2**31
    if sr != SR:
        a = np.interp(np.linspace(0, len(a), int(len(a) * SR / sr), endpoint=False), np.arange(len(a)), a).astype(np.float32)
    return a


def silences(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "silencedetect=n=-35dB:d=0.25", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return [(a + b) / 2 for a, b in zip(st, en)]


def gemini_voice(beats):
    limit = vc.get("chunk_words", 320) if LONG else 10_000
    chunks, cur = [], []
    for b in beats:
        if cur and sum(len(x["narration"].split()) for x in cur) + len(b["narration"].split()) > limit:
            chunks.append(cur); cur = []
        cur.append(b)
    chunks.append(cur)
    audio, words, bounds, t, last_req = [], [], [], 0.0, 0.0
    for ci, ch in enumerate(chunks):
        text = "\n\n".join(b["narration"] for b in ch)
        key = hashlib.sha1(f"{vc['model']}|{vc['voice']}|{vc['style']}|{text}".encode()).hexdigest()[:16]
        path = f"{CACHE}/{key}.wav"
        if not os.path.exists(path):
            wait = 35 - (time.time() - last_req)
            if last_req and wait > 0:
                time.sleep(wait)
            data, mime = gemini_request(text); last_req = time.time()
            if data[:4] == b"RIFF" or "wav" in mime:
                open(path, "wb").write(data)
            else:
                m = re.search(r"rate=(\d+)", mime)
                with wave.open(path, "wb") as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(int(m.group(1)) if m else 24000); w.writeframes(data)
            print(f"chunk {ci + 1}/{len(chunks)} voiced", flush=True)
        else:
            print(f"chunk {ci + 1}/{len(chunks)} from cache", flush=True)
        a = load_wav(path); dur = len(a) / SR; mids = silences(path)
        weights = [max(1, len(re.sub(r"\s", "", b["narration"]))) for b in ch]; tot = sum(weights)
        cuts, acc, prev = [], 0, 0.0
        for w_ in weights[:-1]:
            acc += w_; exp = dur * acc / tot
            near = [m for m in mids if abs(m - exp) < 2.0 and m > prev + 0.5]
            cut = min(near, key=lambda m: abs(m - exp)) if near else exp
            cuts.append(cut); prev = cut
        edges = [0.0] + cuts + [dur]
        for b, (s0, s1) in zip(ch, zip(edges[:-1], edges[1:])):
            bounds.append((t + s0, t + s1))
            ws = b["narration"].split(); lens = [len(w) + 1 for w in ws]; L = sum(lens)
            span = max(s1 - s0 - 0.2, 0.1); pos = s0 + 0.1
            for w_, l in zip(ws, lens):
                d = span * l / L
                words.append({"text": w_, "startMs": int((t + pos) * 1000), "endMs": int((t + pos + d * 0.92) * 1000)}); pos += d
        gap = 0.6 if LONG and ci < len(chunks) - 1 else 0.0
        audio += [a, np.zeros(int(gap * SR), np.float32)]; t += dur + gap
    return np.concatenate(audio), words, bounds


beats = script["beats"]
audio, words, bounds = (gemini_voice if vc["engine"] == "gemini" else kokoro_voice)(beats)
tail = 1.5 if LONG else 0.8
audio = np.concatenate([audio, np.zeros(int(tail * SR), np.float32)]); total = len(audio) / SR

scenes = []
for i, (beat, sc) in enumerate(zip(beats, board["scenes"])):
    start = bounds[i][0]; end = bounds[i + 1][0] if i + 1 < len(bounds) else total
    scenes.append({"id": sc["id"], "type": sc["type"], "props": sc["props"], "onScreen": clean(beat.get("onScreen")),
                   "from": frames(start), "durationInFrames": max(1, frames(end) - frames(start))})
scenes[0]["durationInFrames"] += scenes[0]["from"]; scenes[0]["from"] = 0

out = f"render/public/{vid}"; os.makedirs(out, exist_ok=True)
sf.write(f"{out}/raw.wav", audio, SR)
lufs = -16 if LONG else -14
if vc.get("ambience"):
    fc = (f"[1]lowpass=f=320,volume=0.10[n];[2]volume=0.025,tremolo=f=0.15:d=0.6[s];"
          f"[0][n][s]amix=inputs=3:duration=first:normalize=0,loudnorm=I={lufs}:TP=-1.5:LRA=11")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", f"{out}/raw.wav", "-f", "lavfi", "-i", f"anoisesrc=color=brown:amplitude=0.25:d={total:.2f}",
           "-f", "lavfi", "-i", f"sine=f=55:d={total:.2f}", "-filter_complex", fc, "-ar", "48000", f"{out}/audio.wav"]
else:
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", f"{out}/raw.wav", "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=11", "-ar", "48000", f"{out}/audio.wav"]
subprocess.run(cmd, check=True); os.remove(f"{out}/raw.wav")
props = {"id": vid, "channel": channel, "fps": FPS, "width": board["width"], "height": board["height"], "captions": CAPTIONS,
         "theme": vc.get("theme", "default"), "durationInFrames": frames(total), "audio": f"{vid}/audio.wav", "scenes": scenes,
         "words": words if CAPTIONS else []}
json.dump(props, open(f"{out}/props.json", "w"), ensure_ascii=False, indent=1)
print(f"{vid}: {total:.1f} s, {len(scenes)} scenes, {len(words)} words, {FPS} fps")
