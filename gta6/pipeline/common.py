"""Shared helpers: paths, config, env, json, subprocess, durations."""
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # the gta6/ folder
CACHE = ROOT / "cache"


def log(msg):
    print(f"[gta6] {msg}", file=sys.stderr, flush=True)


def channel():
    return os.environ.get("GTA6_CHANNEL", "hi")


def load_config():
    """Base config.json merged with channels/<channel>.json (hi = Hinglish, en = English)."""
    cfg = json.loads((ROOT / "config.json").read_text())
    ch = ROOT / "channels" / f"{channel()}.json"
    if not ch.exists():
        raise SystemExit(f"Unknown channel {channel()}; add channels/{channel()}.json")
    cfg.update(json.loads(ch.read_text()))
    cfg["formats"] = [f for f in cfg["formats"] if f not in cfg.get("excluded_formats", [])]
    return cfg


def load_env():
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def env(name, required=True):
    load_env()
    val = os.environ.get(name, "")
    if required and not val:
        raise SystemExit(f"Missing {name}. Put it in gta6/.env (see .env.example).")
    return val


def read_json(path, default=None):
    p = Path(path)
    if not p.exists():
        if default is not None:
            return default
        raise SystemExit(f"Missing {p}")
    return json.loads(p.read_text())


def write_json(path, data):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def slugify(text, max_len=50):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len].strip("-") or "video"


def new_video_dir(title):
    d = ROOT / "content" / channel() / f"{date.today().isoformat()}-{slugify(title)}"
    (d / "work").mkdir(parents=True, exist_ok=True)
    return d


def video_dir(arg):
    p = Path(arg)
    if not p.is_absolute() and not p.exists():
        p = ROOT / "content" / channel() / arg
    if not p.exists():
        raise SystemExit(f"No video folder {arg}")
    (p / "work").mkdir(exist_ok=True)
    return p


def run(cmd, quiet=True):
    res = subprocess.run(cmd, capture_output=quiet, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(map(str, cmd))}\n{(res.stderr or '')[-2000:]}")
    return res.stdout


def duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=nw=1:nk=1", str(path)])
    return float(out.strip())


def status(vdir):
    return read_json(vdir / "status.json", {"approved_script": False, "approved_final": False})


def set_status(vdir, **kw):
    s = status(vdir)
    s.update(kw)
    write_json(vdir / "status.json", s)


def require(vdir, key, what):
    if not status(vdir).get(key):
        raise SystemExit(f"{what} not approved yet. Review it, then run: python -m pipeline -c {channel()} approve {vdir.name} "
                         f"{'script' if key == 'approved_script' else 'final'}")


def made_videos():
    """script.json of every video already made on the current channel."""
    base = ROOT / "content" / channel()
    return [json.loads(f.read_text()) for f in sorted(base.glob("*/script.json"))] if base.exists() else []
