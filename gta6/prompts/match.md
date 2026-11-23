You are editing a GTA 6 commentary video. For each script beat, pick footage scenes from the catalog that best illustrate what the narration says.

Beats (id, seconds of narration, what the footage should show):
{{beats}}

Catalog (scene id | source | seconds | description):
{{catalog}}

Rules:
- Pick enough scenes to cover each beat's seconds, 2-5 scenes per beat, in the order they should play.
- Spread picks across many different sources. Avoid long runs from one source.
- Never reuse a scene in two beats.
- If nothing fits well, pick the closest general atmosphere footage.

Use the short scene ids exactly as given (S1, S2, ...). Return compact JSON with no extra fields: {"picks": [{"beat": 1, "scenes": ["S12", "S40"]}]}
