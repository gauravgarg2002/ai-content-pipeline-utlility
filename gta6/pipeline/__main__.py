"""CLI: python -m pipeline [-c hi|en] <stage> ...  (run from the gta6/ folder)"""
import argparse
import importlib
import os

STAGES_AFTER_SCRIPT = ["voice", "source", "index", "match", "assemble", "thumbnail"]


def main():
    p = argparse.ArgumentParser(prog="python -m pipeline")
    p.add_argument("-c", "--channel", default="hi", help="hi = Hinglish channel, en = English channel")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("models", help="list Gemini model IDs your key can use")
    sub.add_parser("topics", help="trending topic ideas")
    sub.add_parser("daily", help="topics + scripts for today's videos (videos_per_day)")
    sub.add_parser("auto", help="one tick of the fully automated loop (run by the schedule)")
    sc = sub.add_parser("script", help="write scripts")
    sc.add_argument("topic", nargs="?")
    sc.add_argument("--format", default="explainer")
    sc.add_argument("--search-query", default="")
    sc.add_argument("--from-topics", type=int, default=0, help="write scripts for the top N new topics")
    ap = sub.add_parser("approve", help="approve the script or the final video")
    ap.add_argument("video")
    ap.add_argument("what", choices=["script", "final"])
    for st in STAGES_AFTER_SCRIPT + ["build"]:
        sub.add_parser(st).add_argument("video")
    pub = sub.add_parser("publish")
    pub.add_argument("video")
    pub.add_argument("--publish-at", default="", help="RFC3339 UTC time to schedule, e.g. 2026-11-23T13:30:00Z")
    args = p.parse_args()
    os.environ["GTA6_CHANNEL"] = args.channel  # read by common.load_config / paths

    from .common import load_config, set_status, video_dir
    if args.cmd == "models":
        from .llm import list_models
        list_models()
    elif args.cmd == "approve":
        set_status(video_dir(args.video), **{f"approved_{args.what}": True})
        print(f"Approved {args.what}.")
    elif args.cmd == "build":  # everything between script approval and final review
        for st in STAGES_AFTER_SCRIPT:
            importlib.import_module(f".{st}", __package__).main(args)
    elif args.cmd == "daily":
        importlib.import_module(".topics", __package__).main(args)
        args.topic, args.from_topics = None, load_config()["videos_per_day"]
        importlib.import_module(".script", __package__).main(args)
    else:
        importlib.import_module(f".{args.cmd}", __package__).main(args)


if __name__ == "__main__":
    main()
