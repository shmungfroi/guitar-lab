# The Guitar Lab 0.11: First Steps — approved spec

Approved by Justin, 28 Nov 2026: "approved" (First Steps framework, all recommendations).
Source of the request (Justin, 28 Nov): "it's too complicated. When the Guitar Lab first opens I want it to reflect sequenced learning... anatomy of the guitar with checks to get to the next stage, which is learning the strings and tuning, then basic chords and basic chord language such as chord diagrams, fingering numbers and tab... consistent and scaffolded, like the Shmung Machine has basic instructions, a process to complexity."
Baseline: `main` 90719f9 (0.9), 383/383. Branch `firststeps`. (Bass/R13 work is on `build-r13`, NOT in this build; it will be rebased onto this later.)

## Decisions (approved as recommended)
1. **Gate:** First Steps must be finished before the Path opens, unless the student passes the "I already play" placement quiz.
2. **Tabs appear as needed:** at the start only First Steps (then Path + Record). Rudiments and Warm-up appear after stage 1 is passed; Technique, Invent and Gig after stage 2. Teacher mode shows all tabs always.
3. **First chord in step 7:** E minor (2 fingers), then the Path opens at A·E.
4. **Tuning:** reference tones in the app + clip-on tuner advice. No microphone tuner yet.
5. **Left-handed flip:** later batch (not now). Step 2 has a short left-hander note.
6. **Order:** guitar First Steps + tabs-as-needed now; the pattern goes into the program framework and design skill after; bass etc. later with R13.
7. **Look:** illustrated, warm, hand-drawn in the family style (shmungfroi-design skill), never a generic quiz look.

## The seven steps (guitar)
| # | Title | Teaches | Check to pass |
|---|---|---|---|
| 1 | Meet the guitar | Original labelled SVG drawing of an acoustic guitar (and a small note on electric: pickups instead of soundhole): headstock, tuning pegs (machine heads), nut, neck, frets, fret markers (dots), body, soundhole, bridge, saddle, strings | Tap-the-part quiz on the drawing: 5 parts named in turn, all correct; wrong tap gently says what it was |
| 2 | Sit and hold | Seated posture (waist of the guitar on the right leg for right-handers), neck slightly up, fretting hand (left) and strumming hand (right), thumb behind the neck, holding a pick; left-hander note: mirror everything, many play a left-handed guitar | Honour tick: "I can sit and hold it comfortably" |
| 3 | The strings | Names low to high E A D G B E; numbers 6 (thickest, low E) to 1 (thinnest, high E); a memory line in our own words (e.g. "Eat All Day, Get Big Easily"); the drawing's strings highlight | Quiz: 5 questions — a highlighted string → its name; a number → its name; mixed |
| 4 | Tuning | Play each open string's reference note (E2 A2 D3 G3 B3 E4) with the app's guitar voice, looped on tap; how to tune by ear (turn the peg, match, go up to the note from below); clip-on tuner how-to | Ear quiz: 4 items, two tones, "higher or lower?" (difference ≥ a semitone, starting with big gaps); then honour tick "My guitar is in tune" |
| 5 | Chord diagrams | Reading a chord box: strings run down (low E on the left), frets across, the thick line is the nut, dots are where fingers go, numbers in dots are fingers (1 index, 2 middle, 3 ring, 4 little; thumb T), o above = play open, x = don't play | Quiz: 4 questions on a diagram (which finger on which string and fret; which strings open; which not played) |
| 6 | TAB | Six lines; the bottom line is the low E (thickest) string; numbers are frets, 0 = open; read left to right; TAB doesn't show rhythm on its own | Quiz: read 3 notes from a short TAB (string + fret); play-back button sounds them |
| 7 | First sound | E minor from its diagram (2 fingers: 2nd fret A string finger 2, 2nd fret D string finger 3 — or 1 and 2 if that's what the app's existing Em box uses; match the app), strum all six; then a 3-note TAB line on the open strings | Honour tick with the band playing an Em drone/strum along; then "Start the Path" |

After step 7: First Steps marked complete; the Path opens at stage 1 (A·E) exactly as today.

## Behaviour
- First open (no save): only the First Steps view (one step at a time, progress dots 1–7, Back/Next, Next disabled until the step's check passes). Header, metronome bar and the instrument picker hidden or minimal during First Steps; nothing else on screen competes.
- "I already play" (on step 1): a placement quiz of 8 items drawn from steps 1, 3, 5 and 6; all correct → First Steps complete, Path opens; otherwise it says which steps to visit and opens the first one.
- Students can revisit First Steps any time from the Path (a small "First Steps" link) without losing progress.
- **Returning students with any existing progress** (any level, gate, mark, journal entry or `fs` already set) skip First Steps automatically and keep their current tabs: nobody loses access to anything they already use. Their tabs-as-needed state is computed from their gates.
- Teacher mode: all tabs visible always; First Steps available but never forced.
- Tabs-as-needed (decision 2) for students: Path + Record after First Steps; + Rudiments, Warm-up after stage 1 gate; + Technique, Invent, Gig after stage 2 gate. A newly appearing tab is announced once in plain words ("Rudiments is open: short daily drills for your hands").
- Instruments: this batch is guitar. If a student switches to bass, drums, keys or vocals, they get today's 0.9 behaviour (no First Steps yet, all tabs) with a one-line note "First Steps for <instrument> is coming". The instrument picker itself is only shown after First Steps is done.
- Progress saved in the existing `shredder` state as a new field `fs` (e.g. `{done:[1,2,…], complete:true, placed:false}`), default absent; old saves, 0.7–0.9 backups and bare state still import; backup includes `fs`.

## Design (shmungfroi-design skill)
- Builder reads the skill first: `/root/.claude/skills/synced/f1b3e4ab-b47d-4f75-b27e-08d2e93f882c_202e44b6-919b-40e3-8017-b3049067e2b4/shmungfroi-design/` (SKILL.md, references/tokens.md, lab-identities.md, components.md, not-ai-looking.md, words.md, function-colours.md) and runs `scripts/check_design.py index.html --lab guitar` as part of the self-check; FAILs fixed or explained.
- Drawings: original hand-drawn-feeling SVG line art (ivory/gold line on Garden black; correct proportions; 6 strings; frets narrowing toward the body), no stock clip-art, no emoji icons. Same drawing reused in steps 1–3 with parts/strings highlighted.
- One step per screen at 360 px with the drawing on top; at 1280 drawing beside the text. Calm, generous spacing; one clear button.
- Words: plain, warm, second person, British/Australian terms; short sentences; no jargon before it's taught.

## Hard constraints
- Path, Gig, Record and all existing content unchanged once open (guitar Path snapshot equal to 0.9 apart from version and the "First Steps" link).
- localStorage key `shredder`; save shape only gains `fs`; no `alert`/`confirm`/`prompt`; one `index.html` + `fonts/`; no network or libraries; dominant and function colours unchanged.
- Version 0.11 (title, header, backup `version`, newer-version message).

## Tests (new `tests/test_firststeps.py`)
F1 first open shows only First Steps step 1 · F2 Next blocked until each check passes (each step) · F3 wrong answers don't pass; retry works · F4 step 1 tap-quiz on the SVG parts · F5 strings quiz names/numbers correct (6 = low E) · F6 tuning reference tones are E2 A2 D3 G3 B3 E4 (oscillator freq) and the ear quiz pairs are a semitone or more apart with the right answer · F7 diagram quiz answers match the drawn diagram · F8 TAB quiz: bottom line = low E; play-back pitches correct · F9 Em diagram matches the app's Em box · F10 completing step 7 opens the Path at stage 1 · F11 placement quiz: all correct skips; a wrong answer routes to the right step · F12 tabs-as-needed per gate; teacher mode shows all · F13 returning save with progress skips First Steps and keeps its tabs · F14 `fs` saved, survives reload, in backups; 0.7/0.8/0.9 backups + bare state import · F15 other instruments keep 0.9 behaviour with the note · F16 360/1280 × both themes: no overflow, no console errors · F17 design checker: no FAIL.
Existing suites must still pass (adjust only tests that assume all tabs are visible on a fresh page: they should seed a returning save or teacher mode, and say so).
