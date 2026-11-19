# Wild Waters: Spearfishing Devlog

<!-- Agent read route: read the newest entries; find others by searching `^## ` headings or `Post: not drafted`. -->

## 2026-11-18: Three days of the dive

- Kind: before-after
- What changed: The diver is filmed on a generated Waves coast at normal game speed. They wade out, swim face down with the spear at their side and dive, and their shadow shows on the sea floor among the fish and kelp.
- What was wrong: In the first working version (2026-11-15) the diver simply vanished and popped back up in a square test pond, with a few faint dots for fish. A day later there was a shadow, a ripple and shoals, still on a test pond. The first promo was sped up, on painted ponds, with the zone drawn over the water. The author's words on 2026-11-16: "Show it in 1x speed in the game its way to fast.", "Show it in the natural bodies of water of waves and living water not square ugly ponds" and "First hide the zone, it makes the video look ugly".
- Before: copies of two recorded test runs in `work/devlog/dive/`. First take: `2026-11-15-first-take.mp4` (run `20261115-190706-spearfishing-visuals-s1`, 19:07, five minutes after `f68afab`). Day two: `2026-11-16-day-two.mp4` (run `20261116-114702-spearfishing-visuals-s1`). Stages between: the other `*-spearfishing-visuals-s1` runs from those two days under the shared harness's `work/userdata/spear/SpearfishingTests/`, which its `prune` command can delete, and the four promo takes in `work/ticket-31*/` (2026-11-16).
- After: `work/promo/footage/diver/clip.mp4`, 8.5 to 18.5 s (filmed 2026-11-18 from `622f94c`).
- Asset: `work/discord/dive-before-after.mp4` and `work/discord/dive-before-after.png`
- Post: drafted (`work/discord/dive-before-after.md`)

## 2026-11-16: Shoal fish swim on their own

- Kind: before-after
- What changed: Each fish in a shoal keeps its own position and heading, swims toward its place at a capped speed and faces the way it travels. When a diver comes close, each fish flees on its own jittered line and the shoal fans out, then regroups.
- What was wrong: The first shoals (2026-11-16, `0de74bf`) placed every fish at a fixed slot rotated around the lead fish. When the leader turned, the whole shoal pivoted as one block: fish near the leader looked right, edge fish swept round far too fast and moved sideways. The author's words on 2026-11-16: "The whole scool pivots on an axis."
- Before: test run `20261116-050205-spearfishing-visuals-s1`, 22.5 to 24.4 s (05:02, first shoal code). The recording lives under the shared harness's `work/userdata/spear/SpearfishingTests/`, which its `prune` command can delete; a cropped copy is `work/posts/2026-11-18-shoals/src-050205.mp4`.
- After: test run `20261116-114702-spearfishing-visuals-s1`, 22.5 to 24.4 s (ticket 32's approval run, same seed and pond); cropped copy `work/posts/2026-11-18-shoals/src-114702.mp4`.
- Asset: `work/posts/2026-11-18-shoals/shoal-before-after.mp4` and `shoal-before-after.png` (the scatter at the pond's edge); `shoal-open-water.mp4` and `shoal-open-water.png` (a turn in open water, before 4.8 to 7.6 s, after 2.0 to 5.2 s)
- Post: drafted (`work/posts/2026-11-18-shoals/post.md`)
