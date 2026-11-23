# Storyboard rules (learned from review)

1. **One title per frame.** A scene shows either its own title (`props.label`, kinetic text) or the
   on-screen overlay, never both. Enforced in `tools/render/prepare.py` (drops the overlay when the
   scene has a label; `scenes.json` onScreen overrides the script's, `null` = none) and in
   `render/src/Short.tsx`. Mahabharata ep. 1 shipped with both stacked (fixed 24 Nov 2026).
2. **Pictures follow the narration.** Long beats (horror, epics) change scene at phrases in the
   narration (`sequence` anchored by text offset), not one image per paragraph.
3. **Characters, not charts, for mythology.** Epics use the shadow-puppet stage; maps only for routes.
4. **Check the contact sheet before delivery** for overlapping text, clipped labels and empty frames.
5. **Text must fit its box.** Puppet scene labels size their box to the text; names under figures
   stagger to a second line when two figures stand closer than 190 px.
