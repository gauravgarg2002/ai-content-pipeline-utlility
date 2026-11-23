"""Thumbnail text + frame choice per video. Writes content/<ch>/<id>/thumb.json.

text: "*word*" is highlighted, "\\n" breaks lines. scene: index into scenes.json; at: 0-1 inside it.
"""
import json, os

T = {
    # Channel A, week 1
    "a-maps-data/2026-11-20-greenland-vs-africa-14x": (2, 0.9, "Greenland\nis *14× smaller*"),
    "a-maps-data/2026-11-20-france-most-time-zones": (0, 0.9, "Most time zones?\nNot *Russia*"),
    "a-maps-data/2026-11-20-canada-coastline-27-years": (4, 0.8, "Walk Canada's coast:\n*27 years*"),
    "a-maps-data/2026-11-20-half-of-humanity-one-circle": (1, 0.9, "*Half* of humanity\nlives in here"),
    "a-maps-data/2026-11-20-alaska-easternmost-state": (2, 0.9, "The most *eastern*\nUS state?"),
    "a-maps-data/2026-11-20-why-every-map-is-wrong": (3, 0.8, "Every map\nis *wrong*"),
    # Channel A, week 2
    "a-maps-data/2026-11-30-russia-vs-pluto": (4, 0.9, "Russia > Pluto?\n*Not anymore*"),
    "a-maps-data/2026-11-30-reno-west-of-los-angeles": (2, 0.9, "Reno is *west*\nof LA"),
    "a-maps-data/2026-11-30-australia-wider-than-moon": (4, 0.9, "Wider than\nthe *Moon*"),
    "a-maps-data/2026-11-30-brazil-borders-almost-everyone": (1, 0.9, "Brazil borders all\n*except 2*"),
    "a-maps-data/2026-11-30-farthest-point-from-the-sea": (2, 0.9, "*2,510 km*\nfrom the sea"),
    "a-maps-data/2026-11-30-time-zones-are-a-mess": (7, 0.8, "Time zones\nmake *no sense*"),
    # Channel B
    "b-ai-hinglish/2026-11-20-chatgpt-free-2026-catch": (1, 0.8, "ChatGPT free\npar *ek catch*"),
    "b-ai-hinglish/2026-11-20-chatgpt-training-setting-off": (2, 0.8, "Ye setting\n*band karo*"),
    "b-ai-hinglish/2026-11-20-deepmind-free-56-hour-course": (3, 0.8, "56 ghante ka\nAI course *free*"),
    "b-ai-hinglish/2026-11-20-gemini-books-your-ride-india": (0, 0.8, "Gemini *ride*\nbook karega"),
    "b-ai-hinglish/2026-11-20-gemini-live-bhojpuri": (4, 0.8, "Gemini ab\n*Bhojpuri* mein"),
    "b-ai-hinglish/2026-11-30-gemini-tasks-free-india": (2, 0.8, "Gemini Tasks\n*free* India mein"),
    "b-ai-hinglish/2026-11-30-chatgpt-go-free-year-ending": (3, 0.8, "*₹399* katne\nse pehle"),
    "b-ai-hinglish/2026-11-30-google-ai-plus-free-students": (4, 0.8, "AI Plus *1 saal free*\n31 Dec tak"),
    "b-ai-hinglish/2026-11-30-chatgpt-plus-free-researchers": (2, 0.8, "ChatGPT Plus\n*12 mahine free*"),
    "b-ai-hinglish/2026-11-30-chatgpt-live-dictation": (1, 0.8, "Bolo, *likha*\nturant"),
    # Channel C
    "c-horror-hi/2026-11-20-saamne-wali-khidki": (12, 0.6, "सामने वाली\n*खिड़की*", "रात 2:10"),
    "c-horror-hi/2026-11-30-naunvi-manzil": (10, 0.85, "*नौवीं* मंज़िल", "रात 3:33 की लिफ़्ट"),
    # Channel D
    "d-epics-en/2026-11-20-mahabharata-family-tree": (21, 0.8, "One family.\n*One war.*", "THE MAHABHARATA FAMILY TREE"),
    "d-epics-en/2026-11-30-rama-route-on-a-map": (15, 0.6, "Ayodhya\nto *Lanka*", "RAMA'S 14-YEAR EXILE"),
}

if __name__ == "__main__":
    for k, v in T.items():
        scene, at, text, *sub = v
        d = os.path.join("content", k)
        assert os.path.isdir(d), d
        json.dump({"scene": scene, "at": at, "text": text, **({"sub": sub[0]} if sub else {})},
                  open(os.path.join(d, "thumb.json"), "w"), ensure_ascii=False, indent=2)
    print(len(T), "thumb.json written")
