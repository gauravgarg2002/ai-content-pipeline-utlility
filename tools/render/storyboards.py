"""Week 1 storyboards in the scene vocabulary of render/src/scenes (v3).

Rewrites each video's scenes.json: one scene per beat, keeping ids and
estimated timings. Run once after editing; prepare.py retimes from audio.
Scene types: geo, number, bars, cards, kinetic, timeline, clocks, ui,
truesize, pack, drag, ruler, tree, atmos.
"""
import glob, json, os

def geo(**p): return ("geo", p)
def number(items, **p): return ("number", {"items": items, **p})
def bars(b, **p): return ("bars", {"bars": b, **p})
def cards(cells, **p): return ("cards", {"cells": cells, **p})
def kinetic(text): return ("kinetic", {"text": text})
def ui(kind, **p): return ("ui", {"kind": kind, **p})
def atmos(scene=None, seq=None): return ("atmos", {"scene": scene or seq[0][0], **({"sequence": seq} if seq else {})})

FR_TERR = ["French Polynesia", "Guadeloupe", "Martinique", "French Guiana", "Saint Pierre and Miquelon", "Reunion", "Mayotte",
           "Kerguelen", "New Caledonia", "Wallis and Futuna", "Marquesas"]
LABELLED = {"French Polynesia", "Reunion", "New Caledonia", "French Guiana"}
LABEL_DX = {"French Polynesia": {"dx": 90}, "New Caledonia": {"dx": -90}}
CIRCLE = {"center": [99.63, 21.65], "radiusKm": 3300}
ASIA_HEAT = ["India", "China", "Bangladesh", "Pakistan", "Indonesia", "Vietnam", "Philippines", "Myanmar", "Thailand", "Nepal"]
WIDE = [-85, -40, 75, 84]

BOARDS = {
    "greenland-vs-africa-14x": [
        geo(fills=["Greenland", "Africa"], view="atlantic"),
        bars([["Greenland", 2.166], ["Africa", 30.37]], unit="M km²"),
        ("pack", {"container": "Africa", "pieces": ["USA", "China", "India"]}),
        kinetic("MERCATOR · 1569"),
        geo(view="atlantic", tissot={"lats": [0, 25, 45, 60, 70]}),
        geo(view="atlantic", fills=["Greenland", "Africa"], tissot={"lats": [0, 25, 45, 60, 70]}),
        ("drag", {"shape": "Greenland", "to_lat": 0, "land_on": "Africa"}),
    ],
    "france-most-time-zones": [
        geo(view="world", fills=["Russia"], strike="Russia", strikeAt=0.5),
        number([["Russia", 11], ["USA", 11]]),
        number([["France", 12]], accent=True),
        geo(view="world", fills=[{"name": "France", "label": "France"}],
            pins=[{"place": n, "label": n if n in LABELLED else "", **LABEL_DX.get(n, {})} for n in FR_TERR]),
        geo(view=[30, -60, 230, 40], pins=[{"place": "Tahiti", "label": "Tahiti", "dx": -60}, {"place": "Reunion", "label": "Réunion", "dx": 60}], lines=[{"places": ["Tahiti", "Reunion"], "at": 0.15}]),
        geo(view="world", fills=[{"name": "France", "label": "France"}], pins=[{"place": "Adelie Land", "label": "Adélie Land", "dy": 50}]),
        ("clocks", {"left": ["Paris", "00:00"], "right": ["Tahiti", "13:00"]}),
    ],
    "canada-coastline-27-years": [
        geo(view="canada", fills=[{"name": "Canada", "label": False}]),
        number([["km of coastline", 202080]]),
        bars([["Canada", 202080], ["Indonesia", 54716]], unit="km"),
        geo(view={"from": "canada", "to": "arctic_canada"}, fills=[{"name": "Canada", "label": False}]),
        ("ruler", {"from_value": 202080, "label_end": 265523}),
        ("ruler", {"counter": False, "strides": [40, 10, 3, 1]}),
        geo(view="canada", fills=[{"name": "Canada", "label": False}]),
    ],
    "half-of-humanity-one-circle": [
        geo(projection="ortho", center=[99.63, 21.65], circles=[{**CIRCLE, "at": 0}]),
        geo(projection="ortho", center=[99.63, 21.65], circles=[{**CIRCLE, "at": 0}], pins=[{"coords": [99.63, 21.65], "label": "Centre"}]),
        geo(projection="ortho", center=[99.63, 21.65], circles=[{**CIRCLE, "at": 0.05}]),
        geo(projection="ortho", center=[99.63, 21.65], circles=[{**CIRCLE, "at": 0}],
            pins=[{"place": n} for n in ["Delhi", "Mumbai", "Beijing", "Manila", "Jakarta"]]),
        geo(projection="ortho", center=[112, 25], circles=[{**CIRCLE, "at": 0}], pins=[{"place": "Tokyo", "color": "#FF5A5F"}]),
        geo(projection="ortho", center=[99.63, 21.65], circles=[{**CIRCLE, "at": 0}], heat=ASIA_HEAT),
        geo(projection="ortho", center=[60, 15], spin=True, circles=[{**CIRCLE, "at": 0}]),
    ],
    "alaska-easternmost-state": [
        geo(view="usa_alaska", fills=[{"name": "USA (48 states)", "label": "USA"}, {"name": "Alaska"}], pins=[{"place": "Maine", "label": "Maine?"}]),
        geo(view={"from": "usa", "to": "alaska"}, fills=[{"name": "Alaska"}]),
        geo(view="aleutians", fills=[{"name": "Alaska", "label": False}], meridian=180),
        geo(view="aleutians", fills=[{"name": "Alaska", "label": False}], meridian=180, pins=[{"place": "Semisopochnoi", "label": "East"}]),
        geo(view="aleutians", fills=[{"name": "Alaska", "label": False}], meridian=180,
            pins=[{"place": "Semisopochnoi", "label": "East", "at": 0}, {"place": "Amatignak", "label": "West"}]),
        geo(view="aleutians", fills=[{"name": "Alaska", "label": False}], measure={"a": "Amatignak", "b": "Semisopochnoi", "label": "71 mi"},
            pins=[{"place": "Semisopochnoi", "label": "", "at": 0}, {"place": "Amatignak", "label": "", "at": 0}]),
        geo(view="usa_alaska", fills=[{"name": "Alaska", "label": "Alaska: N · W · E"}]),
    ],
    "why-every-map-is-wrong": [
        number([["countries voted for 'Correct the Map'", 164]]),
        geo(view=WIDE, fills=["Greenland", "Africa"]),
        bars([["Africa", 30.37], ["Russia", 17.1]], unit="M km²"),
        ("truesize", {"shapes": ["Greenland", "DR Congo"]}),
        geo(projection="ortho", center=[10, 20], morph={"from": "ortho", "to": "mercator"}, view="world"),
        cards(["Shape", "Area", "Distance", "Direction"], cross_out_after=2),
        ("timeline", {"events": [[1569, "Mercator's world map"]]}),
        geo(view=[-60, -25, 15, 50], pins=[{"place": "Lisbon"}, {"place": "Salvador"}], lines=[{"places": ["Lisbon", "Salvador"], "straight": True, "at": 0.15}]),
        kinetic("THE COST: AREA"),
        geo(view="world", tissot={"lats": [0, 30, 60, 75], "lons": [-120, -60, 0, 60, 120]}),
        geo(view=WIDE, fills=["Greenland"], tissot={"lats": [0, 72], "lons": [-40, 20], "radius": 5}),
        geo(view=WIDE, tissot={"lats": [0, 45, 60], "lons": [-40, 20]}, pins=[{"place": n} for n in ["Milan", "Montreal", "Oslo", "Anchorage"]]),
        ("truesize", {"shapes": ["Greenland", "Australia", "Saudi Arabia"]}),
        geo(view=[-100, -15, 110, 84], fills=["Greenland", "India"]),
        geo(view=[-180, 30, 180, 86], tissot={"lats": [60, 75, 82], "lons": [-120, -60, 0, 60, 120], "radius": 3}),
        geo(view="world", fills=["Africa", "Europe", "North America"]),
        ("pack", {"container": "Africa", "pieces": ["USA", "China", "India"], "show_remainder": True}),
        geo(view="world", morph={"from": "mercator", "to": "gall_peters"}),
        geo(view="world", projection="gall_peters", fills=["Africa", "South America"]),
        geo(view="world", morph={"from": "gall_peters", "to": "equal_earth"}),
        geo(view="world", projection="equal_earth"),
        kinetic("NASA GISS"),
        ("timeline", {"events": [[1569, "Mercator"], [2017, "Boston adopts Gall-Peters"], [2018, "Equal Earth"]]}),
        kinetic("CORRECT THE MAP"),
        bars([["For", 164], ["Against", 1], ["Abstain", 6]]),
        cards(["Governments", "Schools", "Tech companies"], stamp="Encouraged, not forced"),
        cards([["Supporters", "Old map shrinks Africa"], ["United States", "“Ideological agenda”"]]),
        cards(["Mercator", "Gall-Peters", "Equal Earth"]),
        geo(view=[-60, -25, 15, 50], pins=[{"place": "Lisbon"}, {"place": "Salvador"}], lines=[{"places": ["Lisbon", "Salvador"], "straight": True, "at": 0.1}]),
        cards([["Navigate", "Mercator"], ["Compare size", "Equal-area"], ["Both", "Globe"]]),
        kinetic("A SAILOR'S TOOL"),
        geo(view=WIDE, fills=["Greenland", "Africa"]),
    ],
    "chatgpt-free-2026-catch": [
        kinetic("UNLIMITED*"),
        ui("chat", app="ChatGPT", highlight="composer"),
        kinetic("GPT-5.6 · LUNA"),
        ui("chat", app="ChatGPT", highlight="think_button", prompt="Ye problem step by step samjhao"),
        cards(["Images", "Files", "Voice", "Deep Research"], stamp="WEEKLY LIMIT"),
        ui("chat", app="ChatGPT", highlight="sponsored_section"),
        cards([["Daily text", "Free is enough"], ["Heavy images & files", "Then think paid"]]),
    ],
    "chatgpt-training-setting-off": [
        kinetic("YOUR CHATS → AI"),
        ui("toggle", state="on"),
        ui("flow", **{"from": "Your chats", "to": "Next model"}),
        ui("settings", path_steps=["Settings", "Data Controls"], state="on"),
        ui("settings", path_steps=["Settings", "Data Controls"], state="off"),
        cards(["Office code", "Documents", "Personal"]),
        ui("toggle", state="off"),
    ],
    "deepmind-free-56-hour-course": [
        number([["hours of AI training", 56]], stamp="FREE"),
        kinetic("AI RESEARCH · FOUNDATIONS"),
        cards(["Build LLMs", "Fine-tune", "AI research"]),
        ui("course"),
        cards([["IISc Bangalore", "already using it"], ["NASSCOM", "Future Skills Prime"]]),
        kinetic("LINK · IN DESCRIPTION"),
        number([["hours", 56]], stamp="FREE"),
    ],
    "gemini-books-your-ride-india": [
        ui("phone", sequence=["Voice prompt", "App opens", "Ride booked"]),
        geo(view="world", fills=["India", "Japan", "United Kingdom"]),
        cards(["Grocery", "Ride", "Food", "Table booking"]),
        ui("devices", devices=["Pixel 10", "Motorola Signature 27", "Samsung Galaxy (select)"]),
        ui("phone", sequence=["Voice prompt: storage clear karo", "Settings result"]),
        cards(["Age", "Language", "Subscription"], stamp="CONDITIONS APPLY"),
        ui("phone", sequence=["Ride booked"]),
    ],
    "gemini-live-bhojpuri": [
        kinetic("भोजपुरी"),
        number([["Indian languages & dialects", 25]], suffix="+"),
        cards(["Voice", "Text"]),
        cards(["संस्कृत", "भोजपुरी", "मैथिली"]),
        ui("bubbles"),
        ui("phone", sequence=["Open Gemini", "Live mode", "Speak"]),
        kinetic("AAPKI · BHASHA?"),
    ],
    "saamne-wali-khidki": [
        atmos("narrow_lane_night"),
        atmos(seq=[["room_interior_fan", 0], ["phone_clock", 0.62], ["opposite_window_silhouette_combing", 0.85]]),
        atmos("opposite_window_silhouette_combing"),
        atmos("morning_shop_shutter"),
        atmos("opposite_window_silhouette_wave"),
        atmos(seq=[["opposite_window_silhouette_wave", 0], ["narrow_lane_night", 0.12], ["room_chair_turned_to_window", 0.3], ["fogged_glass", 0.7]]),
        atmos("tea_stall_dusk"),
        atmos(seq=[["opposite_window_figure_pointing", 0], ["room_plain", 0.6], ["narrow_lane_night", 0.8]]),
        atmos("abandoned_stairwell_torch"),
        atmos("empty_dusty_room"),
        atmos("pov_through_dusty_glass_to_own_room"),
        atmos("own_room_empty_bed"),
        atmos("opposite_window_shows_narrator_with_figure_behind"),
        atmos("narrow_lane_night"),
    ],
}

# ---- Mahabharata tree: cumulative state per beat ------------------------------
ALL = ["Ganga", "Shantanu", "Satyavati", "Parashara", "Bhishma", "Chitrangada", "Vichitravirya", "Ambika", "Ambalika", "Vyasa", "Maid",
       "Gandhari", "Dhritarashtra", "Vidura", "Pandu", "Kunti", "Madri", "Vasudeva", "Duryodhana", "Duhshala", "Yuyutsu", "Karna",
       "Yudhishthira", "Bhima", "Arjuna", "Nakula", "Sahadeva", "Krishna", "Adhiratha", "Radha", "Draupadi"]
GROUPS = [{"label": "Kauravas · 100 sons", "ids": ["Duryodhana", "Duhshala"]}, {"label": "Pandavas", "ids": ["Yudhishthira", "Bhima", "Arjuna", "Nakula", "Sahadeva"], "color": "#FFB547"}]
STEPS = [  # (add, highlight, deceased, label/sub changes)
    ("ALL", [], [], {}), None,
    (["Shantanu", "Ganga"], [], [], {"subs": {"Shantanu": "king of Hastinapura", "Ganga": "river goddess"}}),
    (["Bhishma"], [], [], {"labels": {"Bhishma": "Devavrata"}, "subs": {"Bhishma": "eighth son"}}),
    (["Satyavati"], [], [], {"subs": {"Satyavati": "fisher chief's daughter"}}),
    ([], ["Bhishma"], [], {"labels": {"Bhishma": "Bhishma"}, "subs": {"Bhishma": "vow of celibacy"}}),
    (["Parashara", "Vyasa"], ["Vyasa"], [], {"subs": {"Vyasa": "sage"}}),
    (["Chitrangada", "Vichitravirya"], [], ["Chitrangada"], {}),
    (["Ambika", "Ambalika"], [], [], {}),
    ([], ["Vyasa"], ["Vichitravirya"], {}),
    (["Maid", "Dhritarashtra", "Pandu", "Vidura"], [], [], {"subs": {"Dhritarashtra": "born blind", "Pandu": "born pale"}}),
    ([], ["Vyasa", "Dhritarashtra", "Pandu", "Vidura"], [], {}),
    (["Gandhari", "Duryodhana", "Duhshala"], [], [], {}),
    (["Yuyutsu"], ["Gandhari"], [], {"subs": {"Gandhari": "blindfolded", "Yuyutsu": "son of a maid"}}),
    (["Kunti", "Madri"], [], [], {"subs": {"Pandu": "cursed"}}),
    (["Yudhishthira", "Bhima", "Arjuna", "Nakula", "Sahadeva"], [], [],
     {"subs": {"Yudhishthira": "Dharma", "Bhima": "Vayu", "Arjuna": "Indra", "Nakula": "Ashvins", "Sahadeva": "Ashvins"}}),
    ([], [], ["Pandu", "Madri"], {}),
    (["Karna"], ["Karna"], [], {"subs": {"Karna": "son of Surya"}}),
    (["Adhiratha", "Radha"], ["Karna"], [], {}),
    (["Vasudeva", "Krishna"], ["Krishna"], [], {}),
    (["Draupadi"], ["Draupadi"], [], {}),
    ([], ["Bhishma", "Karna"], [], {}),
    ([], ["Vyasa"], [], {"subs": {"Vyasa": "author"}}),
    ("ALL", [], [], {}),
]

def tree_boards():
    out, nodes, dead, labels, subs = [], [], [], {}, {}
    final_subs = {}
    for st in STEPS:
        if st and st[3]: final_subs.update(st[3].get("subs", {}))
    for st in STEPS:
        if st is None:
            out.append(kinetic("VYASA · ADI PARVA · GANGULI")); continue
        add, hl, de, ch = st
        labels.update(ch.get("labels", {})); subs.update(ch.get("subs", {}))
        dead += [d for d in de if d not in dead]
        if add == "ALL":
            out.append(("tree", {"nodes": ALL, "new": [], "highlight": hl, "deceased": dead if len(out) > 1 else [], "groups": GROUPS,
                                 "labels": {"Bhishma": "Bhishma"}, "subs": final_subs if len(out) > 1 else {}}))
            continue
        nodes += [n for n in add if n not in nodes]
        out.append(("tree", {"nodes": list(nodes), "new": list(add), "highlight": hl, "deceased": list(dead), "groups": GROUPS,
                             "labels": dict(labels), "subs": dict(subs)}))
    return out

# mahabharata-family-tree is now storyboarded in puppet_boards.py (shadow puppets)

if __name__ == "__main__":
    for d in sorted(glob.glob("content/*/*/")):
        slug = os.path.basename(d.rstrip("/"))[11:]
        if slug not in BOARDS: continue
        sc = json.load(open(d + "scenes.json")); beats = json.load(open(d + "script.json"))["beats"]
        board = BOARDS[slug]
        assert len(board) == len(beats) == len(sc["scenes"]), f"{slug}: {len(board)} scenes vs {len(beats)} beats"
        for s, (typ, props) in zip(sc["scenes"], board):
            s["type"], s["props"] = typ, props
        json.dump(sc, open(d + "scenes.json", "w"), ensure_ascii=False, indent=2)
        print(f"{slug}: {len(board)} scenes")
