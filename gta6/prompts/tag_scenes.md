You are indexing GTA 6 gameplay footage. Each image is one frame from a scene; they are numbered in order, starting at 0.

For each image return: a short English description of what is shown (place, action, vehicles, characters, time of day, weather), 3-8 search tags, whether a streamer facecam or webcam is visible, whether large text overlays/watermarks/subscribe graphics are visible, whether it is a menu/loading screen/title card/non-gameplay, whether it shows intimate, sexual or suggestive content (say so plainly in the description), and visual quality 1-5.

Return JSON: {"frames": [{"i": 0, "desc": "...", "tags": ["..."], "facecam": false, "overlay": false, "non_gameplay": false, "quality": 4}]}
