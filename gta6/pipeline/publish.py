"""Stage 9: upload to the GTA channel's own account via YouTube Data API (private or scheduled)."""
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .common import ROOT, channel, env, load_config, read_json, require, set_status, video_dir, log

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]


def youtube():
    # one Google account per channel: tokens live in .secrets/<channel>/
    TOKEN = ROOT / ".secrets" / channel() / "token.json"
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES) if TOKEN.exists() else None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:  # first run opens a browser: sign in with the GTA channel's Google account
            flow = InstalledAppFlow.from_client_secrets_file(str(ROOT / ".secrets" / channel() / "client_secret.json"), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN.parent.mkdir(parents=True, exist_ok=True)
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def main(args):
    vdir = video_dir(args.video)
    require(vdir, "approved_final", "Final video")
    meta = read_json(vdir / "metadata.json")
    cfg = load_config()
    yt = youtube()
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False}
    if args.publish_at:  # e.g. 2026-11-23T13:30:00Z
        status["publishAt"] = args.publish_at
    body = {"snippet": {"title": meta["title"], "description": meta["description"], "tags": meta["tags"],
                        "categoryId": "20", "defaultLanguage": cfg["video_language"], "defaultAudioLanguage": cfg["video_language"]},
            "status": status}
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(vdir / "final.mp4"), chunksize=8 * 1024 * 1024, resumable=True))
    res = None
    while res is None:
        prog, res = req.next_chunk()
        if prog:
            log(f"Upload {int(prog.progress() * 100)}%")
    vid = res["id"]
    yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(vdir / "thumbnail.jpg"))).execute()
    yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": cfg["caption_language"], "name": cfg["channel_name"]}},
                         media_body=MediaFileUpload(str(vdir / "captions.srt"))).execute()
    set_status(vdir, youtube_id=vid)
    print(f"Uploaded https://youtu.be/{vid} ({'scheduled ' + args.publish_at if args.publish_at else 'private'})")
