# The Guitar Lab 0.7: independent check

**Independent check** of `index.html` on branch `build-0.7` (HEAD 3d29c67) against `SPEC_07.md`.
The checker did not build 0.7, did not read `BUILD_REPORT.md` or commit messages, and did not use the repo test suite as evidence (it was run once, for R12 only). Every result below comes from throwaway Playwright scripts (Chromium, headless) kept outside the repo in `/tmp/check07/`, driving the page through its buttons, the DOM and `localStorage` only.

Date: 27 Nov 2026.

## Verdict

All twelve register items meet the spec as written. No Must findings. One Should finding (dark-mode lit black key, the R10 problem left in the other theme) and four Could findings.

| ID | Verdict | Evidence in one line |
|---|---|---|
| R1 Backup | PASS | Download, copy, blocked-clipboard fallback, file import, paste import, in-page confirm, cancel, bad input, lossless round trip, 0.6 save, sandboxed iframe: all behave as specified. No pop-ups. |
| R2 Gig feel | PASS | Path set to Flamenco (Tangos) feel: Gig boogie still plays swung; Gig switch changes Gig only; Path switch changes Path only. |
| R3 Present mode | PASS | Headings and chart clearly larger at 360/768/1280; no page overflow in light or dark. |
| R4 "eighths" | PASS | 0 occurrences of "eighth" in 936 text snapshots (visible text, aria-labels, SVG text). |
| R5 Capo redraw | PASS | Bass and keys: one-minute card renames at each capo step, up and down. |
| R6 Greensleeves | PASS | Bar 3 = Am in chart, band playback, bass/keys/vocals panels. Musically sound. |
| R7 Subtonic colour | PASS | G (VII) uses the subtonic colour; E/E7/F♯ stay dominant; dominant hex values unchanged. |
| R8 Drum wording | PASS | Drum panel uses hats, snare, kick. (See C3 for the metronome label.) |
| R9 Slips | PASS | No plain "F#" anywhere; La Bamba note now refers to its four-bar loop; label reads "bpm (dotted crotchet)". |
| R10 Light-mode lit black key | PASS | Light: #a47510 on cream, 3.17:1 (was #f0d48a). See S1 for dark mode. |
| R11 Spelling note | PASS | "Not a misprint…" note shown in exactly the 13 crawled views that contain C♭/E♯/B♯, and nowhere else. |
| R12 M3 test | PASS (single run) | `pytest tests/test_ui.py -k M3`: 7 passed, 5.66 s. The "3 consecutive full runs" criterion was not run. |

## What was run, and what was seen

### R1 Backup (Record tab)
- **Findable:** Backup card at the foot of the Record column; the page footer links to it ("keep a backup from the Record tab").
- **Download:** file `guitar-lab-backup-2026-11-27.json`; wrapper `{app, format:1, version:"0.7", saved, state}`; `state` equals `localStorage.shredder` exactly.
- **Copy:** clipboard text parses and its `state` equals the saved state.
- **Clipboard blocked** (writeText rejected and execCommand false): read-only textarea appears, filled and fully selected, with the message "Copying is blocked here. The backup is in the box above, already selected…".
- **Import by paste and by file:** both show the in-page box "Replace your progress with this backup?" with counts for the backup and for what is in the browser now; focus lands on Cancel. Cancel leaves `localStorage` byte-identical and says so. Confirm replaces, saves and re-renders (instrument, tempo and record all updated); state survives a reload.
- **Lossless round trip:** export, change progress, import: resulting state deep-equals the exported state (paste and file).
- **Bad input (9 cases):** empty, `{not json`, `[1,2]`, `"x"`, `null`, `{"foo":1}`, `{"lv":[1]}`, `{"changes":[1]}`, a `format:2` wrapper, and a bad file. Each gave a specific plain-English message ending "Nothing has been changed", showed no confirm box, and left storage untouched.
- **0.6 save:** a save made by actually using the 0.6 app from `main` (levels on two instruments, feel, capo, one-minute log, warm-up, gig names and songs, journal) loads in 0.7 with every field intact. The only differences after 0.7 re-saves: `gig.useFin:false` added (new default) and `teacher` reset to false (0.6 does the same on load). A raw unwrapped 0.6 state also imports through the paste box.
- **Pop-ups:** `alert`, `confirm`, `prompt` were replaced with spies in every script: never called.
- **Sandboxed iframe** (`sandbox="allow-scripts"`, and again with `allow-downloads`): page renders with `localStorage` throwing SecurityError; copy falls back to the textarea; bad JSON, cancel, confirm, file import and an in-sandbox round trip all work; all tabs open. With `allow-downloads` the file downloads; without it nothing downloads and the message tells the user to use Copy backup if no file appeared.
- **Viewer downloads capability:** with a stand-in `window.claude.use('downloads')` the app calls `save({filename, data})`, reports success, reports "Download cancelled" on a `declined` error, and falls back to the blob link on other errors. This is a stand-in written by the checker, not the real claude.ai viewer.
- **Hostile backup:** band names and journal text containing `<img onerror>` / `<script>` are shown as text; nothing executed.
- **Design:** screenshots in dark 1280 and light 360. The card uses the same card, button, note and gold-bordered "gate" styles as the rest of the app; error text uses the dominant-red left rule. It does not look generic. The paste box uses a monospace system font, which is reasonable for JSON.

### R2 Gig feel
Oscillator and buffer start times were recorded during playback at 120 bpm.
- Path: Flamenco + feel on (metronome label "Tangos…"). Gig opens with "Song's own feel" pressed, label "Boogie shuffle, swung", and onsets in long–short swing pairs. La Bamba: "Straight quavers" at 140.
- Gig switch on: label and playback become Tangos (onsets on the beat only). Path switch stays as it was.
- Path feel off: Gig switch stays on. Gig own + Path on: Gig still swung. Setting survives reload.

### R3 Present mode
| Width | Phase heading | Run-sheet cell | Chart bar width | Song title |
|---|---|---|---|---|
| 360 | 16 → 22 px | 14 → 20 px | 55 → 90 px | 30 → 34 px |
| 768 | 16 → 22 px | 14 → 20 px | 76 → 141 px | 30 → 34.6 px |
| 1280 | 16 → 33 px | 14 → 31 px | 127 → 246 px | 30 → 57.6 px |

No document overflow at any width, light or dark, across two songs and five instruments. Setup cards are hidden. Screenshots reviewed at 1280 dark and 360 light. See C1.

### R4, R9, R11 and terms (text crawl)
936 snapshots: 5 instruments × 8 stages (with 4 feels and capo 1–7 in the full pass) plus Warm-up, Rudiments, Technique, Invent, Gig (6 songs), Record, NSW and Teacher modes; dark 1280, light 1280, dark 360, light 768.
- "eighth", "sixteenth", "quarter note", "measure": 0. American spellings checked (color, center, practiced, etc.): 0.
- Plain `[A-G]#`: 0, including Invent with all stages learned (pool in B minor shows F♯).
- "(bpm (": 0. Label is "bpm (dotted crotchet)".
- La Bamba: "Recordings vary in key; the loop is the same four bars all the way through: listen and adjust." The "bars 10 and 12" wording remains only on the 12-bar songs, where it belongs.
- Spelling note appears if and only if C♭/F♭/E♯/B♯ is on screen (0 mismatches). The spellings themselves are correct (e.g. G♯7 = G♯ B♯ D♯ F♯ in C♯ minor; C♭ as IV of G♭ major).

### R5 Capo
Stage 1 on bass and on keys, light and dark: A ↔ E → B♭ ↔ F → B ↔ F♯ → C ↔ G, and back down to A ↔ E, each immediately after the click.

### R6 Greensleeves
- Chart: Verse Am | G | Am | E | Am | G | Am E | Am; Refrain C | G | Am | E | C | G | Am E | Am.
- Playback (bass oscillator pitches by bar): A, G, A, E, A, G, A/E, A, then C, G, A… Keys in bar 3: A C E.
- Bass panel lists Am, G, E, C (no F). Vocals cue sheet: la | so | la | mi | la | so | la mi | la.
- Function card: Tonic Am, C · Subtonic G · Dominant E.
- Musical judgement: sound. The bar-3 melody circles A with a G♯ lower neighbour, which sits in Am and rubs against an F chord. Am–G–Am–E is a standard classroom harmonisation, and the "G or E in A minor?" card explains the subtonic/dominant contrast correctly.

### R7 Colours
Computed colours, chord boxes and road-map chord names:
- Dark: G (VII · subtonic) `rgb(179,169,143)`; E (V · dominant) `rgb(208,87,75)` = #d0574b.
- Light: G `rgb(94,83,64)`; E `rgb(168,53,43)` = #a8352b.
- Stage 8 (B minor): A (VII) subtonic colour, F♯ (V) dominant red.

### R8 Drums
Drum panel text, e.g. "hats in swung quavers, snare on 2 and 4, kick on 1 and 3" and "hats on all six quavers, snare on 4, kick on 1". No strum terms in the panel on any stage, feel or gig song.

### R10 Keys
- Light: lit black key #a47510; 3.17:1 against the cream white keys, 4.64:1 against unlit black keys and for its own label.
- Dark: unchanged from 0.6 (see S1).

### Hard constraints
- Storage key: only `shredder` is written. Old data loads (above).
- Network: no requests other than the page and its three local font files; no `fetch`, XHR, WebSocket, external script or stylesheet in the source.
- Version: page title "The Guitar Lab 0.7", header "version 0.7".
- Console: zero console errors and zero page errors across all tabs, instruments, stages, feels, capo positions, band playback and metronome, in light and dark, at four viewport sizes.
- No `alert/confirm/prompt` in the source or at run time.

### Regressions
On each of guitar, bass, drums, keys, vocals: raised all five stage-1 steps to Consistent (gate recorded under the right instrument key and shown in Record), logged one-minute changes (where the card exists), raised a rudiment and a technique level, saved a best tempo, ticked a warm-up, opened Invent and pressed every button, played a Path chart and a Gig chart, saved a journal entry (tagged with the instrument). All worked; no errors.

## New findings

### Should
- **S1. Dark mode: lit black key is still close in tone to the cream white keys.** The keyboard is drawn cream in both themes. R10 darkened the lit black key in light mode only; in dark mode it is still #f0d48a against #ece2c8 white keys, 1.12:1, the same problem R10 describes (only a thin dark outline separates them). Seen on Keys, stage 1 (C♯ in A, G♯ in E). Suggest one darker gold for both themes.

### Could
- **C1. Present mode at 360 px, Drums part:** the enlarged drum grid is wider than its box (341 px in a 290 px box) and scrolls sideways inside the card. The page itself does not overflow, so R3 still passes.
- **C2. Sandboxed page wording:** when storage is unavailable (sandboxed iframe), a successful import says "…has been replaced and saved in this browser", but nothing can be saved there. Likewise, Download in a sandbox without download permission says "Backup file made…" before its "If no file appeared…" hint. Both are wording only.
- **C3. Drums and the metronome label:** with Drums selected, the metronome bar and Metronome card still show guitar strum names ("Four downs", "Bass, strum, strum", "Palm-muted quavers"). The card does explain "The letters are the guitar's strum…", and R8 covered the drum panel only, so this is noted, not failed.
- **C4. Blocked clipboard leaves two browser console messages** ("Permissions policy violation: The Clipboard API has been blocked…") in a sandboxed frame. They come from the browser, not the app, and the fallback works.

## Not run, or limits of this check
- R12's "passes in 3 consecutive full runs" was not run; only the single `-k M3` run asked for.
- The real claude.ai artifact viewer and its downloads capability were not available; a stand-in was used.
- One browser only (headless Chromium). No Safari, Firefox or real phone or tablet.
- Sound was checked by scheduled oscillator pitches and onset times, not by ear.
- In the sandboxed-iframe run the fonts failed to load because the checker's local test server sends no CORS header; that is a harness limit, not an app finding, so font rendering inside a sandbox was not assessed.
- Present mode was judged by measured sizes and screenshots, not from the back of a real room.
- Gig songs' chord maps other than La Bamba's note were not re-audited against recordings (out of scope for 0.7).
