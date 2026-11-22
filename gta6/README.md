# GTA 6 commentary pipeline (Hinglish + English channels)

Self-contained pipeline for long-form (8-12 min) GTA 6 commentary and guide videos, for two channels: `hi` (GTA 6 Hindi, Hinglish) and `en` (GTA 6 Decoded, English, for higher-RPM global viewers). Channel settings live in `channels/hi.json` and `channels/en.json`. Shares no code with the other channels in `content-engine/`. Full spec: section 12a of the plan doc "Automated Content Pipeline: Plan and Execution Spec".

## Setup (once, all free)

```bash
cd gta6
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
brew install ffmpeg            # if missing
cp .env.example .env           # add GEMINI_API_KEY (and YOUTUBE_API_KEY for topic search)
```

- Font: put a bold `.ttf` at `assets/fonts/Inter-Bold.ttf` (Inter is free on Google Fonts). Without it, a system font is used.
- Music (optional): drop royalty-free tracks into `assets/music/` (YouTube Audio Library is free).
- Publishing: one Google account per channel. On each, create a Google Cloud project, enable YouTube Data API v3, create an OAuth "Desktop app" client and save it as `.secrets/hi/client_secret.json` or `.secrets/en/client_secret.json`. First publish opens a browser to sign in.
- Affiliate links: join Amazon Associates (free), paste your links into `affiliate_links` in each channel file. Empty URLs are skipped.

## Fully automated mode (default)

Same flow as the other pipelines: you only tap buttons on Telegram.

1. Every morning after 7 am (`daily_script_hour`), each channel picks trending topics and writes `videos_per_day` scripts. Each script arrives on Telegram as `script.md` with **Approve / Reject / Redo**. Redo asks for a note and rewrites the script with it.
2. Approved scripts are built one at a time (voice, footage, render, thumbnail). The final arrives as a 480p preview + thumbnail + description, with the same three buttons. Redo here re-picks footage using your note.
3. Approved finals: while `publish_mode` is `handoff`, Telegram tells you the file path and Finder opens it; upload in YouTube Studio (about 3 min). After the YouTube API audit passes, set `publish_mode` to `api` and uploads are scheduled automatically at each channel's `publish_time_utc`.
4. Failures and quota stops send one Telegram alert, never a loop.

Setup: add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to `.env` (the same bot as the other pipelines works), then:

```bash
bash scripts/install_mac_schedule.sh      # runs `python -m pipeline auto` every 20 min
tail -f logs/auto.log                      # watch it
```

The Mac must be on (lid open or plugged into a display) for ticks to run; missed ticks run when it wakes.

## Make a video by hand

Every command takes `-c hi` (default) or `-c en`.

```bash
python -m pipeline -c hi daily                              # trending topics + today's script(s)
# or: python -m pipeline -c hi script "GTA 6 money kaise kamaye" --format money_method
# read content/hi/<date>-<slug>/script.md, edit script.json if needed
python -m pipeline -c hi approve <folder> script
python -m pipeline -c hi build <folder>                     # voice, source, index, match, assemble, thumbnail
# watch final.mp4, check thumbnail.jpg and metadata.json
python -m pipeline -c hi approve <folder> final
python -m pipeline -c hi publish <folder> --publish-at 2026-11-23T13:30:00Z
```

Daily routine (about 30 min of your time): `daily` for both channels, read the 2 scripts, approve, `build` overnight, watch both renders next morning, approve, publish.

Each stage can also run alone (`voice`, `source`, `index`, `match`, `assemble`, `thumbnail`). Stages cache their work, so a failed run resumes where it stopped. Delete `content/<folder>/work/seg_*.mp4` to force a re-render.

## Footage rules (enforced in `pipeline/rules.py`, tune in `config.json`)

| Rule | Setting |
| --- | --- |
| Source audio muted; our voice + music only | always |
| Max continuous clip from one source | `max_segment_sec` 15 |
| Minimum distinct sources per video | `min_sources` 4 |
| Max share of runtime from one source | `max_source_share` 0.30 |
| Edge crop (removes corner watermarks) | `crop_keep` 0.86 |
| Scenes with facecams, menus, or quality < 3 dropped | always |
| Every source credited in the description | always |

`sources.json` in each video folder logs every clip used. To stop using a creator, add their channel name to `blocked_source_channels`.

## Layout

```
gta6/
  config.json  channels/hi.json  channels/en.json  requirements.txt  .env.example
  prompts/     topics, script, tag_scenes, match
  pipeline/    one module per stage + rules.py + common.py + llm.py
  assets/      fonts/ music/
  topics/      <hi|en>/<date>.json
  content/<hi|en>/<date>-<slug>/  script.json script.md status.json voice.wav timing.json captions.srt
                          sources.json edl.json final.mp4 thumbnail.jpg metadata.json work/
  cache/       downloaded sources, scene indexes, frames (shared across videos, not committed)
```

## Free-tier limits

- Gemini free tier: scene tagging is the heaviest step (one call per 10 scenes). Scene indexes are cached per source, so reused sources cost nothing.
- YouTube Data API: 10,000 units/day. Topic search ~400, one upload ~1,600 with thumbnail and captions.
- Edge TTS: free, no key. Voice `hi-IN-MadhurNeural`; set `tts_voice` to `hi-IN-SwaraNeural` for a female voice.
