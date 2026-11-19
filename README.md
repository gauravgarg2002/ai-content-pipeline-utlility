# Week 1 content: scripts ready for review

Written 20 Nov 2026. 13 videos: 5 Shorts and 1 long-form for channel A, 5 Shorts for channel B, and episode 1 of each slot C pilot.

These are script packages, not rendered videos. Each folder follows the contract in section 11 of the plan, so the pipeline can render them directly once it exists. Every factual line was checked against the source in `factcheck.json`.

## What's in each video folder

| File | What it is |
| --- | --- |
| `script.md` | **Read this one.** The script, on-screen text, visuals and sources in plain text |
| `script.json` | Narration and on-screen text per beat, title, description, tags |
| `factcheck.json` | Verdict and source for every beat |
| `scenes.json` | Storyboard: scene type, timing and props per beat (timings are estimates until voice is generated) |
| `brief.json` | Topic, angle, cluster, hook pattern, sources |
| `status.json` | `draft`; changes to `approved` once you sign off |

## The videos

| Channel | Video | Format | Est. length | Publish by |
| --- | --- | --- | --- | --- |
| A · Maps and data (English) | [The country with the most time zones isn't Russia](content/a-maps-data/2026-11-20-france-most-time-zones/script.md) | short | 0:26 | evergreen |
| A · Maps and data (English) | [Walking Canada's coastline would take 27 years](content/a-maps-data/2026-11-20-canada-coastline-27-years/script.md) | short | 0:33 | evergreen |
| A · Maps and data (English) | [Half of humanity lives inside this circle](content/a-maps-data/2026-11-20-half-of-humanity-one-circle/script.md) | short | 0:32 | evergreen |
| A · Maps and data (English) | [Greenland looks as big as Africa. It's 14 times smaller.](content/a-maps-data/2026-11-20-greenland-vs-africa-14x/script.md) | short | 0:35 | evergreen |
| A · Maps and data (English) | [The easternmost point of the USA is in Alaska](content/a-maps-data/2026-11-20-alaska-easternmost-state/script.md) | short | 0:32 | evergreen |
| A · Maps and data (English) | [Why every world map you know is wrong](content/a-maps-data/2026-11-20-why-every-map-is-wrong/script.md) | long | 6:05 | evergreen |
| B · AI tools (Hinglish) | [ChatGPT free mein unlimited chat, par ek catch hai](content/b-ai-hinglish/2026-11-20-chatgpt-free-2026-catch/script.md) | short | 0:42 | 2027-01-31 |
| B · AI tools (Hinglish) | [Aapki ChatGPT chats se AI seekh raha hai. Ye setting band karo](content/b-ai-hinglish/2026-11-20-chatgpt-training-setting-off/script.md) | short | 0:33 | 2027-02-28 |
| B · AI tools (Hinglish) | [Ab Gemini aapke liye khud ride book karega](content/b-ai-hinglish/2026-11-20-gemini-books-your-ride-india/script.md) | short | 0:42 | 2026-12-15 |
| B · AI tools (Hinglish) | [Gemini se ab Bhojpuri mein baat kar sakte ho](content/b-ai-hinglish/2026-11-20-gemini-live-bhojpuri/script.md) | short | 0:32 | 2027-01-31 |
| B · AI tools (Hinglish) | [Google DeepMind ka 56 ghante ka AI course, bilkul free](content/b-ai-hinglish/2026-11-20-deepmind-free-56-hour-course/script.md) | short | 0:31 | 2027-03-31 |
| C pilot · Horror (Hindi) | [सामने वाली खिड़की | रात 2:10 का राज़ | हिंदी हॉरर कहानी](content/c-pilot-horror-hi/2026-11-20-saamne-wali-khidki/script.md) | long | 10:24 | evergreen |
| C pilot · Epics (English) | [The Mahabharata Family Tree, Explained | Who Is Related to Whom](content/c-pilot-epics-en/2026-11-20-mahabharata-family-tree/script.md) | long | 6:00 | evergreen |

## Your review (about 40 minutes)

1. Read each `script.md`. For each one, decide: approve, cut, or rewrite with a note.
2. Read the two slot C pilots **out loud**, or have someone read them to you. The test for slot C is whether the narration holds you for a full episode.
3. Channel B Shorts have a publish-by date. AI news goes stale; if they aren't live by then, I'll re-check the facts before they ship.
4. Tell me your verdicts in chat, or edit `status.json` to `approved` or `rejected` with a `reviewNote`.

## Notes for the pipeline build

- Channel B narration is Roman Hinglish, as captions should read. The voice stage must transliterate Hindi words to Devanagari before TTS and keep product names in Latin script.
- The epics pilot ships with a pronunciation list: `channels/c-pilot-epics-en/pronunciation.json`. The voice stage must apply it.
- The horror pilot is labelled fiction in its first lines and description. Keep that label.
- Scene types used here are the first draft of the scene library: 
  `annotated_screenshot`, `atmosphere_loop`, `bar_compare`, `camera_pan`, `chat_bubbles`, `city_pins`, `comparison_split`, `count_up`, `density_heat`, `drag_shape`, `family_tree`, `flow_arrow`, `globe_circle`, `grid_reveal`, `grid_stretch`, `kinetic_text`, `line_draw`, `map_highlight`, `map_measure`, `map_pin`, `orange_peel`, `phone_lineup`, `phone_mock`, `projection_morph`, `rhumb_line`, `ruler_fractal`, `scale_zoom`, `shape_pack`, `split_clock`, `timeline`, `toggle_anim`
- Long-form A covers the September 2026 UN vote on map projections. It quotes supporters and the one country that voted against; keep both if you edit it.
