# The Guitar Lab 0.7: approved spec (register 0.6)

Approved by Justin, 27 Nov 2026: "go ahead, greensleeves Am" (all recommended fixes; Q1 = Am).
Baseline: `main` d69419d, full suites 247/247.

## Scope
Fix R1–R12 as recommended below. **Out of scope:** R13 (per-instrument content, needs its own framework) and any new feature or visual redesign.
**Q2 (dominant colour) is still open:** leave the dominant colours exactly as they are (`#d0574b` dark / `#a8352b` light).

## Hard constraints
- Keep the localStorage key `shredder` and the saved-data shape; old saves must load unchanged. Any new fields get defaults.
- No browser pop-ups (`alert`, `confirm`, `prompt`): confirmations are in-page boxes.
- One file (`index.html`) plus `fonts/`. No network calls, no new libraries.
- Brand and design language unchanged (Poiret One + Outfit, Garden black/ivory/gold, function colours). New controls must look like the existing ones, not generic or AI-looking.
- British/Australian spelling and terms (quavers, crotchets).
- No student names anywhere; no lyrics or transcriptions.
- Version label becomes 0.7 (title and wherever 0.6 is shown).

## Register
| ID | Sev | Finding | Required change | Regression test |
|---|---|---|---|---|
| R1 | Must | Progress lives only in one browser; no backup. | Backup panel (Record tab or a clearly findable settings spot): **Download backup** (JSON file of the full saved state; use the viewer's downloads capability when present in a claude.ai artifact, plain `<a download>` blob otherwise), **Copy backup** (JSON to clipboard, with a visible fallback textarea if clipboard is blocked), **Import** by file pick or by pasting JSON. Import validates (object, known shape), shows an in-page "Replace your progress with this backup?" confirm, then replaces state, saves and re-renders. Bad JSON gives a clear in-page message and changes nothing. Round-trip must be lossless. Works when the page is inside a sandboxed iframe. | Export → import round-trip equal; bad JSON rejected with state unchanged; confirm box appears and cancel changes nothing; no `alert/confirm/prompt` called; works in a sandboxed frame |
| R2 | Should | Path Finish feel carries into Gig (boogie can play as Tangos, no switch on Gig). | Gig plays each song in its own feel by default, and the Gig tab has its own feel switch (independent of Path). | Set Path to Tangos → Gig boogie still plays its own feel; Gig switch changes Gig only |
| R3 | Should | Present mode doesn't enlarge chart or phase headings. | In Present mode the chart and phase headings scale up clearly (readable from the back of a room), without horizontal overflow at 360/768/1280. | Chart and heading rendered size larger in Present than not; no overflow |
| R4 | Should | "eighths" appears in student text. | "quavers" throughout student-facing text. | No visible "eighth" in rendered text across tabs |
| R5 | Should | One-minute changes card keeps old chord names after a capo change on bass/keys. | Redraw that card on capo change. | Change capo on bass and keys → card shows sounding names immediately |
| R6 | Should | Greensleeves verse bar 3 is F. | Am (traditional harmony; melody has G♯). Check the chart, band playback and any analysis/roman numerals agree. | Greensleeves map bar 3 = Am; chord suite expectation updated |
| R7 | Should | Minor-key subtonic VII (G in A minor) coloured dominant red. | Neutral/secondary colour (not dominant) for subtonic VII, consistent with its label. | VII in A minor not dominant colour; true dominant E/E7 still dominant |
| R8 | Could | Drum panel describes the groove with strum names. | Drum wording (hats, snare, kick). | No strum terms in drum panel |
| R9 | Could | Slips: plain "F#" (Function card, Invent pool); La Bamba "bars 10 and 12" on a 4-bar loop; "(bpm (dotted crotchet))". | F♯ with the proper sign; correct La Bamba bar reference for its 4-bar loop; tidy the bpm label. | Text checks for each |
| R10 | Could | Light mode: lit black key close in tone to cream white keys. | Darker gold on lit black keys in light mode, clear contrast. | Lit black-key colour differs from white key and meets visible contrast |
| R11 | Could | B minor capo 4 spelled E♭ minor with a C♭ chord: correct but may read as a typo. | One-line on-screen note explaining the spelling when C♭/F♭-type spellings appear. | Note visible in that case only |
| R12 | Should | `test_M3_keys_spelling_every_capo` flaky in the full run. | Make the test wait for the panel to settle (test fix, not an app change unless a real race is found). | Passes in 3 consecutive full runs |
