"""Fully automated loop, one tick at a time. Scheduled every 20 min on the Mac by launchd
(scripts/install_mac_schedule.sh). Same flow as the other pipelines:

  topics + scripts each morning -> Telegram review (approve / reject / redo)
  -> build approved scripts -> 480p preview + thumbnail on Telegram for final review
  -> approved: hand-off (until the YouTube API audit passes) or scheduled API upload.

Every step is idempotent: state lives in each video's status.json, so a crashed or
interrupted tick just picks up on the next one.
"""
import argparse
import fcntl
import json
import os
import shutil
import subprocess
import sys
import traceback
from datetime import date, datetime, timedelta, timezone

from . import telegram as tg
from .common import ROOT, duration, load_config, log, read_json, run, set_status, status

STAGES = ["voice", "source", "index", "match", "assemble", "thumbnail"]
AUTO_STATE = ROOT / "state" / "auto.json"
BUILDING = {}  # the video the current tick is building, for error reporting


class QuotaOut(Exception):
    pass


def base_cfg():
    return json.loads((ROOT / "config.json").read_text())


def use(ch):
    os.environ["GTA6_CHANNEL"] = ch


def videos(ch):
    base = ROOT / "content" / ch
    return sorted(p for p in base.glob("*") if (p / "script.json").exists()) if base.exists() else []


def ns(vdir, **kw):
    return argparse.Namespace(video=str(vdir), **kw)


def guarded(fn, *a, **kw):
    """Run a stage; turn the 'all models out of quota' exit into QuotaOut."""
    try:
        return fn(*a, **kw)
    except SystemExit as e:
        if "out of free quota" in str(e) or "quota" in str(e).lower():
            raise QuotaOut(str(e))
        raise RuntimeError(str(e))


# ---------- 1. apply your Telegram decisions ----------

def apply(d):
    from . import script
    use(d["channel"])
    vdir = ROOT / "content" / d["channel"] / d["folder"]
    if not vdir.exists():
        return
    what, action = d["what"], d["action"]
    if action == "reject":
        set_status(vdir, rejected=True)
        tg.say(f"Rejected: {d['folder']}")
    elif action == "approve" and what == "script":
        set_status(vdir, approved_script=True)
        tg.say(f"Script approved. Building {d['folder']} (about 30-40 min).")
    elif action == "approve" and what == "final":
        set_status(vdir, approved_final=True)
    elif action == "redo" and what == "script":
        s = read_json(vdir / "script.json")
        set_status(vdir, rejected=True)
        new = guarded(script.write_one, load_config(), s["topic"], s["format"], s.get("search_query", ""), d["note"])
        set_status(new, redo_of=vdir.name)
    elif action == "redo" and what == "final":
        # re-pick footage with your note; script and voice stay
        work = vdir / "work"
        for f in list(work.glob("seg_*.mp4")) + [vdir / "edl.json", vdir / "final.mp4"]:
            if f.exists():
                f.unlink()
        set_status(vdir, built=False, final_sent=False, approved_final=False, edit_note=d["note"])
        tg.say(f"Re-editing {d['folder']} with your note.")


# ---------- 2. morning: topics + scripts, sent for review ----------

def daily_scripts(ch, cfg):
    from . import script, topics
    if datetime.now().hour < cfg["daily_script_hour"]:
        return
    today = date.today().isoformat()
    made = [v for v in videos(ch) if v.name.startswith(today) and not status(v).get("redo_of")]
    need = cfg["videos_per_day"] - len(made)
    if need <= 0:
        return
    if not (ROOT / "topics" / ch / f"{today}.json").exists():
        guarded(topics.main, argparse.Namespace())
    guarded(script.main, argparse.Namespace(topic=None, format="", search_query="", from_topics=need))


def send_scripts(ch):
    for v in videos(ch):
        st = status(v)
        if st.get("script_sent") or st.get("rejected"):
            continue
        s = read_json(v / "script.json")
        words = sum(len(b["caption"].split()) for b in s["beats"])
        redo = f"\nRedo of {st['redo_of']}" if st.get("redo_of") else ""
        tg.send_review(ch, v.name, "script", f"[{ch}] SCRIPT: {s['title']}\n{s['format']} · {words} words · "
                       f"~{words / load_config()['words_per_minute']:.0f} min{redo}", document=v / "script.md")
        set_status(v, script_sent=True)


# ---------- 3. build one approved video per tick ----------

def preview(vdir):
    out = vdir / "work" / "preview.mp4"
    d = duration(vdir / "final.mp4")
    vbit = max(150_000, int(44 * 8 * 1024 * 1024 / d) - 64_000)  # stays under Telegram's 50 MB bot limit
    run(["ffmpeg", "-y", "-i", str(vdir / "final.mp4"), "-vf", "scale=-2:480", "-c:v", "libx264",
         "-preset", "veryfast", "-b:v", str(vbit), "-maxrate", str(vbit), "-bufsize", str(2 * vbit),
         "-c:a", "aac", "-b:a", "64k", str(out)])
    return out


def build_next(cfg):
    import importlib
    queue = []
    for ch in cfg["channels_enabled"]:
        for v in videos(ch):
            st = status(v)
            if st.get("approved_script") and not st.get("built") and not st.get("rejected") and not st.get("error"):
                queue.append((v.name, ch, v))
    if not queue:
        return
    _, ch, vdir = sorted(queue)[0]
    use(ch)
    BUILDING.update(channel=ch, vdir=vdir)
    log(f"Building {ch}/{vdir.name}")
    for stage in STAGES:
        if stage == "voice" and (vdir / "timing.json").exists():
            continue
        if stage == "source" and (vdir / "sources.json").exists():
            continue
        if stage == "match" and (vdir / "edl.json").exists():
            continue
        if stage == "assemble" and (vdir / "final.mp4").exists():
            continue
        guarded(importlib.import_module(f".{stage}", __package__).main, ns(vdir))
    set_status(vdir, built=True)
    meta = read_json(vdir / "metadata.json")
    mins = duration(vdir / "final.mp4") / 60
    tg.send_review(ch, vdir.name, "final", f"[{ch}] FINAL ({mins:.1f} min): {meta['title']}\n\n{meta['description']}",
                   photo=vdir / "thumbnail.jpg", video=preview(vdir))
    set_status(vdir, final_sent=True)


# ---------- 4. approved finals: hand-off or API upload ----------

def next_slot(hhmm_utc):
    h, m = map(int, hhmm_utc.split(":"))
    now = datetime.now(timezone.utc)
    slot = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if slot < now + timedelta(minutes=30):
        slot += timedelta(days=1)
    return slot.strftime("%Y-%m-%dT%H:%M:%SZ")


def ship(cfg):
    for ch in cfg["channels_enabled"]:
        use(ch)
        ccfg = load_config()
        for v in videos(ch):
            st = status(v)
            if not st.get("approved_final") or st.get("shipped") or st.get("rejected"):
                continue
            if cfg["publish_mode"] == "api":
                from . import publish  # Google libraries only needed in api mode
                guarded(publish.main, ns(v, publish_at=next_slot(ccfg["publish_time_utc"])))
            else:
                meta = read_json(v / "metadata.json")
                tg.say(f"[{ch}] Ready to upload in YouTube Studio ({ccfg['channel_name']} account):\n"
                       f"{v / 'final.mp4'}\nThumbnail: {v / 'thumbnail.jpg'}\n\nTitle:\n{meta['title']}\n\n"
                       f"Tags: {', '.join(meta['tags'])}\n\nDescription is in the final-review message above. "
                       f"Schedule for {ccfg['publish_time_utc']} UTC.")
                if sys.platform == "darwin":
                    subprocess.run(["open", "-R", str(v / "final.mp4")])
            set_status(v, shipped=True)


# ---------- the tick ----------

def main(args):
    (ROOT / "state").mkdir(exist_ok=True)
    lock = open(ROOT / "state" / "auto.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log("Previous tick still running; skipping")
        return
    cfg = base_cfg()
    auto = read_json(AUTO_STATE, {})
    try:
        for d in tg.poll():
            apply(d)
        for ch in cfg["channels_enabled"]:
            use(ch)
            daily_scripts(ch, load_config())
            send_scripts(ch)
        ship(cfg)
        build_next(cfg)
        ship(cfg)
    except QuotaOut as e:
        if auto.get("quota_alert") != date.today().isoformat():
            tg.say(f"Gemini free quota is used up for today; work resumes after 1:30 pm IST.\n{e}")
            auto["quota_alert"] = date.today().isoformat()
    except Exception as e:  # one alert per failure, video marked so it is not retried in a loop
        err = f"{type(e).__name__}: {e}"
        log(traceback.format_exc())
        if BUILDING:
            v = BUILDING["vdir"]
            set_status(v, error=err[:500])  # not retried until you clear it, so no alert loop
            tg.say(f"[{BUILDING['channel']}] Build failed for {v.name}:\n{err[:1500]}\n\n"
                   f"Fix, then remove \"error\" from its status.json to retry.")
        elif auto.get("last_error") != err:  # same failure every 20 min -> one alert
            tg.say(f"Pipeline tick failed:\n{err[:1500]}")
            auto["last_error"] = err
    else:
        auto.pop("last_error", None)
    finally:
        from .common import write_json
        write_json(AUTO_STATE, auto)
