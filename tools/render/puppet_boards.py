"""Shadow-puppet storyboard for the Mahabharata family-tree episode (channel D).

Rewrites content/d-epics-en/2026-11-20-mahabharata-family-tree/scenes.json in the
puppet vocabulary (render/src/scenes/puppet.tsx). Run from the repo root.
"""
import json, os

ID = "content/d-epics-en/2026-11-20-mahabharata-family-tree"


def P(bg, cast, label=None, **kw):
    return {"type": "puppet", "props": {"bg": bg, "cast": cast, **({"label": label} if label else {}), **kw}}


def c(who, x, pose="stand", name=None, **kw):
    return {"who": who, "x": x, "pose": pose, **({"name": name if name is not None else who} if name is not False else {}), **kw}


# children on screen are the same puppets at small scale
def kid(who, x, name=None, **kw):
    return c(who, x, name=name, scale=0.55, **kw)


PANDAVAS = [("Yudhishthira", "Yudhishthira"), ("Bhima", "Bhima"), ("Arjuna", "Arjuna"), ("Nakula", "Nakula"), ("Sahadeva", "Sahadeva")]

BOARD = [
    # 1 hook
    P("kurukshetra", [c("Arjuna", 0.25, "bow", name=False), c("Bhima", 0.38, "fight", name=False),
                      c("Duryodhana", 0.66, "fight", facing="left", name=False), c("Bhishma", 0.8, "bow", facing="left", name=False)], "COUSINS AT WAR"),
    # 2 version note
    P("forest", [c("Vyasa", 0.5, "bless")], "VYASA'S MAHABHARATA"),
    # 3 Shantanu + Ganga
    P("river", [c("Shantanu", 0.35, "namaste"), c("Ganga", 0.65, "bless", facing="left", enter="right", at=0.3)], "HASTINAPURA"),
    # 4 seven sons, eighth saved
    P("river", [c("Shantanu", 0.3, "point"), c("Ganga", 0.62, "carry", facing="left"), kid("Devavrata", 0.48, at=0.75, enter="drop")], "THE EIGHTH SON"),
    # 5 Satyavati
    P("river", [c("Shantanu", 0.28, "namaste"), c("Satyavati", 0.52, facing="left", enter="right", at=0.15), c("Fisherman", 0.74, "point", facing="left", name="Her father", at=0.45)]),
    # 6 Bhishma's vow
    P("palace", [c("Shantanu", 0.3, "bless"), c("Bhishma", 0.62, "namaste", facing="left", name="Devavrata → Bhishma")], "THE TERRIBLE VOW"),
    # 7 Vyasa backstory
    P("forest", [c("Parashara", 0.25, "bless"), c("Satyavati", 0.45), c("Vyasa", 0.72, "bless", facing="left", enter="right", at=0.55)], "REMEMBER VYASA"),
    # 8 two sons
    P("palace", [c("Shantanu", 0.22, "bless", exit="left", exitAt=0.3), c("Satyavati", 0.4), c("Chitrangada", 0.6, "fight", facing="left", exit="right", exitAt=0.45),
                 c("Vichitravirya", 0.78, facing="left"), c("Bhishma", 0.95, "bow", facing="left", enter="right", at=0.75)]),
    # 9 three princesses
    P("court", [c("Bhishma", 0.22, "bow"), c("Amba", 0.48, "plead", facing="left", exit="right", exitAt=0.55), c("Ambika", 0.64, facing="left"), c("Ambalika", 0.8, facing="left")], "THE PRINCESSES OF KASHI"),
    # 10 Vichitravirya dies
    P("palace", [c("Vichitravirya", 0.7, "sad", facing="left", exit="right", exitAt=0.2), c("Satyavati", 0.4, "plead", at=0.3), c("Bhishma", 0.62, "namaste", facing="left", at=0.45)], "NO HEIR"),
    # 11 niyoga
    P("palace", [c("Ambika", 0.18), c("Vyasa", 0.38, "bless"), c("Ambalika", 0.58, facing="left"),
                 kid("Dhritarashtra", 0.72, at=0.3, enter="drop"), kid("Pandu", 0.82, at=0.55, enter="drop"), kid("Vidura", 0.92, at=0.8, enter="drop")]),
    # 12 Vyasa's sons
    P("palace", [c("Vyasa", 0.5, "bless", y=230, scale=0.8, name=False), c("Dhritarashtra", 0.28), c("Pandu", 0.5), c("Vidura", 0.72, facing="left")], "VYASA'S SONS"),
    # 13 Pandu crowned, Kauravas
    P("court", [c("Pandu", 0.5, "bless", name="King Pandu"), c("Dhritarashtra", 0.22), c("Gandhari", 0.34, at=0.3), c("Duryodhana", 0.78, "fight", facing="left", at=0.6)],
      "100 KAURAVAS", crowd=50, crowdAt=0.55),
    # 14 Gandhari blindfold, Yuyutsu
    P("court", [c("Gandhari", 0.35, "sad", name="Gandhari, blindfolded"), c("Dhritarashtra", 0.55, facing="left"), c("Yuyutsu", 0.78, facing="left", at=0.5, exit="right", exitAt=0.85)]),
    # 15 Pandu's curse
    P("forest", [c("Pandu", 0.25, "bow"), c("Deer", 0.62, facing="left", exit="right", exitAt=0.25, name=False), c("Kindama", 0.62, "angry", facing="left", at=0.28, name="Sage Kindama"),
                 c("Kunti", 0.86, facing="left", at=0.72)], "THE CURSE"),
    # 16 five Pandavas
    P("forest", [c("Kunti", 0.12, "bless"), c("Madri", 0.24, at=0.55)] + [kid(w, 0.4 + i * 0.12, name=n, at=0.1 + i * 0.17, enter="drop") for i, (w, n) in enumerate(PANDAVAS)], "THE PANDAVAS"),
    # 17 Pandu dies, return
    P("fire", [c("Pandu", 0.3, "sad", exit="left", exitAt=0.2), c("Madri", 0.45, "sad", exit="left", exitAt=0.45), c("Kunti", 0.62, "walk", walk=True, at=0.5)]
      + [kid(w, 0.72 + i * 0.055, name=False, at=0.55, walk=True) for i, (w, _) in enumerate(PANDAVAS)]),
    # 18 Karna
    P("river", [c("Kunti", 0.35, "sad", name="Young Kunti"), kid("Karna", 0.62, name="Karna", at=0.5, exit="right", exitAt=0.85)], "THE FIRST SON", sun=True),
    # 19 Adhiratha, Radha, Duryodhana
    P("palace", [c("Adhiratha", 0.15, exit="left", exitAt=0.35), c("Radha", 0.28, "bless", exit="left", exitAt=0.35), c("Karna", 0.45, "bow", name="Karna (Radheya)"),
                 c("Duryodhana", 0.68, "give", facing="left", at=0.55)], "FRIENDS"),
    # 20 Krishna
    P("court", [c("Kunti", 0.25), c("Vasudeva", 0.45, name="Vasudeva (her brother)"), c("Krishna", 0.7, "bless", facing="left", at=0.45)], "KRISHNA"),
    # 21 Draupadi
    P("court", [c("Drupada", 0.15, "bless"), c("Arjuna", 0.38, "bow"), c("Draupadi", 0.56, "namaste", facing="left", at=0.3)]
      + [c(w, 0.7 + i * 0.08, name=False, scale=0.85, facing="left", at=0.6) for w in ("Yudhishthira", "Bhima", "Nakula", "Sahadeva") for i in [("Yudhishthira", "Bhima", "Nakula", "Sahadeva").index(w)]], "DRAUPADI"),
    # 22 the whole tree
    P("kurukshetra", [c("Krishna", 0.08, name=False, scale=0.85)] + [c(w, 0.16 + i * 0.075, name=n, scale=0.8) for i, (w, n) in enumerate(PANDAVAS)]
      + [c("Karna", 0.62, "bow", facing="left", scale=0.85), c("Duryodhana", 0.76, "fight", facing="left", scale=0.85), c("Bhishma", 0.9, "bow", facing="left", scale=0.85)], "ONE FAMILY"),
    # 23 Vyasa at the top
    P("palace", [c("Vyasa", 0.5, "bless", y=250, name=False)] + [c(w, 0.1 + i * 0.08, name=False, scale=0.7) for i, (w, _) in enumerate(PANDAVAS)]
      + [c("Duryodhana", 0.72, facing="left", scale=0.7, name=False), c("Dhritarashtra", 0.82, facing="left", scale=0.7, name=False), c("Gandhari", 0.92, facing="left", scale=0.7, name=False)],
      "GRANDFATHER OF BOTH SIDES"),
    # 24 close
    P("kurukshetra", [c("Vyasa", 0.5, "sad", y=260, scale=0.85, name=False), c("Arjuna", 0.2, "bow", name=False), c("Bhima", 0.32, "fight", name=False),
                      c("Duryodhana", 0.7, "fight", facing="left", name=False), c("Karna", 0.83, "bow", facing="left", name=False)], "KURUKSHETRA"),
]


def main():
    path = os.path.join(ID, "scenes.json")
    d = json.load(open(path))
    assert len(d["scenes"]) == len(BOARD), (len(d["scenes"]), len(BOARD))
    for sc, b in zip(d["scenes"], BOARD):
        sc["type"], sc["props"], sc["onScreen"] = b["type"], b["props"], None
    json.dump(d, open(path, "w"), ensure_ascii=False, indent=2)
    print("rewrote", path, len(BOARD), "puppet scenes")


if __name__ == "__main__":
    main()
