"""Stage 7: render segments (muted, cropped, moving, with callouts) and mix our audio."""
import random
from pathlib import Path

from .common import channel, ROOT, load_config, log, read_json, run, video_dir

FPS = 30
FALLBACK_FONTS = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


_ENC = None


def encoder():
    """Mac hardware encoder (much faster on Apple Silicon) when ffmpeg has it, else libx264."""
    global _ENC
    if _ENC is None:
        has_vt = "h264_videotoolbox" in run(["ffmpeg", "-hide_banner", "-encoders"])
        _ENC = (["-c:v", "h264_videotoolbox", "-b:v", "10M", "-allow_sw", "1"] if has_vt
                else ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20"])
    return _ENC


def font(cfg):
    for f in [str(ROOT / cfg["font_path"])] + FALLBACK_FONTS:
        if Path(f).exists():
            return f
    return None


def motion(effect, frames):
    n = max(frames, 1)
    centre = "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    if effect == "zoom_in":
        return f"z='1+0.15*on/{n}':{centre}"
    if effect == "zoom_out":
        return f"z='1.15-0.15*on/{n}':{centre}"
    if effect == "pan_left":
        return f"z='1.15':x='(iw-iw/zoom)*(1-on/{n})':y='ih/2-(ih/zoom/2)'"
    return f"z='1.15':x='(iw-iw/zoom)*on/{n}':y='ih/2-(ih/zoom/2)'"


def drawtext(textfile, fnt, extra):
    ff = f":fontfile='{fnt}'" if fnt else ""
    return f"drawtext=textfile='{textfile}'{ff}:{extra}"


def render_segment(i, seg, src_path, cfg, work, fnt):
    out = work / f"seg_{i:04}.mp4"
    if out.exists():
        return out
    k = cfg["crop_keep"]  # trims edges where watermarks and facecams usually sit
    frames = int(round(seg["dur"] * FPS))
    vf = [f"fps={FPS}", f"crop=iw*{k}:ih*{k}",
          "scale=1920:1080:force_original_aspect_ratio=increase", "crop=1920:1080",
          f"zoompan={motion(seg['effect'], frames)}:d=1:s=1920x1080:fps={FPS}", "setsar=1"]
    brand = work / "brand.txt"
    vf.append(drawtext(brand, fnt, "fontsize=30:fontcolor=white@0.85:x=w-tw-40:y=36:shadowcolor=black:shadowx=2:shadowy=2"))
    if seg.get("callout"):
        tf = work / f"callout_{i:04}.txt"
        tf.write_text(seg["callout"].upper())
        vf.append(drawtext(tf, fnt, f"fontsize=76:fontcolor=yellow:box=1:boxcolor=black@0.65:boxborderw=26:"
                                    f"x=90:y=h-260:enable='lt(t,{cfg['callout_sec']})'"))
    run(["ffmpeg", "-y", "-ss", str(seg["start"]), "-i", src_path, "-t", str(seg["dur"]), "-an",
         "-vf", ",".join(vf), "-frames:v", str(frames), "-r", str(FPS),
         *encoder(), "-pix_fmt", "yuv420p", str(out)])
    return out


def main(args):
    vdir = video_dir(args.video)
    cfg = load_config()
    work = vdir / "work"
    (work / "brand.txt").write_text(cfg["channel_name"])
    srcs = {s["id"]: s["path"] for s in read_json(vdir / "sources.json")}
    edl = read_json(vdir / "edl.json")
    fnt = font(cfg)
    if not fnt:
        log("No font file found; put a bold .ttf at gta6/" + cfg["font_path"])
    segs = []
    for i, seg in enumerate(edl):
        if i % 10 == 0:
            log(f"Rendering segment {i + 1}/{len(edl)}")
        segs.append(render_segment(i, seg, srcs[seg["src"]], cfg, work, fnt))
    lst = work / "segments.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in segs))
    silent = work / "video_silent.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)])
    music = sorted(p for p in (ROOT / cfg["music_dir"]).glob("*") if p.suffix.lower() in (".mp3", ".wav", ".m4a"))
    cmd = ["ffmpeg", "-y", "-i", str(silent), "-i", str(vdir / "voice.wav")]
    if music:
        cmd += ["-stream_loop", "-1", "-i", str(random.choice(music)),
                "-filter_complex", f"[2:a]volume={cfg['music_volume']}[m];[1:a][m]amix=inputs=2:duration=first:normalize=0[a]",
                "-map", "0:v", "-map", "[a]"]
    else:
        log("No music in assets/music; voice only")
        cmd += ["-map", "0:v", "-map", "1:a"]
    out = vdir / "final.mp4"
    run(cmd + ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)])
    print(f"Rendered {out.name}. Next: python -m pipeline -c {channel()} thumbnail {vdir.name}")
