"""Telegram review bot (same flow as the other pipelines): approve / reject / redo buttons.

No server: `auto` polls getUpdates on each scheduled tick. Only messages from
TELEGRAM_CHAT_ID are accepted.
"""
import json

import requests

from .common import ROOT, env, read_json, write_json

STATE = ROOT / "state" / "telegram.json"  # update offset, button ids, pending redo prompts


def _api(method, files=None, **data):
    url = f"https://api.telegram.org/bot{env('TELEGRAM_BOT_TOKEN')}/{method}"
    for k, v in list(data.items()):
        if isinstance(v, (dict, list)):
            data[k] = json.dumps(v)
    r = requests.post(url, data=data, files=files, timeout=300)
    body = r.json()
    if not body.get("ok"):
        raise RuntimeError(f"Telegram {method} failed: {body.get('description')}")
    return body["result"]


def _state():
    return read_json(STATE, {"offset": 0, "buttons": {}, "next_id": 1, "redo_prompts": {}})


def _save(st):
    write_json(STATE, st)


def _keyboard(ch, folder, what):
    """callback_data is capped at 64 bytes, so buttons carry a short id mapped in state."""
    st = _state()
    bid = str(st["next_id"])
    st["next_id"] += 1
    st["buttons"][bid] = {"channel": ch, "folder": folder, "what": what}
    _save(st)
    return {"inline_keyboard": [[{"text": "✅ Approve", "callback_data": f"ok:{bid}"},
                                 {"text": "❌ Reject", "callback_data": f"no:{bid}"},
                                 {"text": "✏️ Redo", "callback_data": f"redo:{bid}"}]]}


def chat():
    return env("TELEGRAM_CHAT_ID")


def say(text):
    return _api("sendMessage", chat_id=chat(), text=text[:4000], disable_web_page_preview="true")


def send_review(ch, folder, what, text, document=None, photo=None, video=None):
    """Send something for review with the three buttons on the last message."""
    kb = _keyboard(ch, folder, what)
    if photo:
        with open(photo, "rb") as f:
            _api("sendPhoto", files={"photo": f}, chat_id=chat(), caption="Thumbnail")
    if video:
        with open(video, "rb") as f:
            _api("sendVideo", files={"video": f}, chat_id=chat(), caption="Preview (480p)",
                 supports_streaming="true")
    if document:
        with open(document, "rb") as f:
            return _api("sendDocument", files={"document": f}, chat_id=chat(), caption=text[:1000], reply_markup=kb)
    return _api("sendMessage", chat_id=chat(), text=text[:4000], reply_markup=kb)


def poll():
    """Return decisions since the last poll: [{action, channel, folder, what, note}]."""
    st = _state()
    updates = _api("getUpdates", offset=st["offset"], timeout=0,
                   allowed_updates=["message", "callback_query"])
    decisions = []
    for u in updates:
        st["offset"] = u["update_id"] + 1
        cq = u.get("callback_query")
        if cq and str(cq["message"]["chat"]["id"]) == chat():
            action, bid = cq["data"].split(":", 1)
            target = st["buttons"].pop(bid, None)
            _api("answerCallbackQuery", callback_query_id=cq["id"], text="Got it" if target else "Already handled")
            if not target:
                continue
            _api("editMessageReplyMarkup", chat_id=chat(), message_id=cq["message"]["message_id"],
                 reply_markup={"inline_keyboard": []})
            if action == "redo":
                m = _api("sendMessage", chat_id=chat(), reply_markup={"force_reply": True},
                         text=f"What should change in {target['folder']}? Reply to this message.")
                st["redo_prompts"][str(m["message_id"])] = target
            else:
                decisions.append({"action": "approve" if action == "ok" else "reject", **target, "note": ""})
        msg = u.get("message")
        if msg and str(msg["chat"]["id"]) == chat() and msg.get("reply_to_message"):
            target = st["redo_prompts"].pop(str(msg["reply_to_message"]["message_id"]), None)
            if target:
                decisions.append({"action": "redo", **target, "note": msg.get("text", "")})
    _save(st)
    return decisions
