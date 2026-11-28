# The Guitar Lab 0.11 "First Steps": build report (self-check)

This is the builder's own check. It is not the independent check: that needs a separate agent given only the spec, the design skill and the output.

- Branch `firststeps`, not merged. Spec: `SPEC_FS.md` (approved 28 Nov), plus the two sets of amendments below.
- Code commits: stage A `f2a70d6`, stage B `79e008c`, stage C `424d197`, finish `4626acb`. This report is the commit after `4626acb`.
- Full suites, run once on `4626acb`: **434 passed, 0 failed** in 4 min 25 s (`python3 -m pytest tests -q -p no:cacheprovider`). That is the 383 from 0.9 plus 51 new in `tests/test_firststeps.py`.
- Design checker on `index.html --lab guitar`: 35 PASS, 1 FAIL, 5 WARN. The FAIL and all five WARNs are the same lines 0.9 gets (see "Design checker").
- `index.html` is 174 KB (126 KB at 0.9). Still one file plus `fonts/`.

## Amendments from Justin's booklet (relayed by the main session, 28 Nov)

The main session relayed guidance from Justin's Year 8 booklet "Rockin' the Guitar" while the build was running. I have not seen the booklet; I worked from the relayed points only, and wrote every sentence fresh. Nothing of its text, images, layout or colours is in the app.

| # | Amendment | Done |
|---|---|---|
| 1 | Step 1 uses the booklet's terms: machine heads ("tuning pegs" said once), headstock/head, nut, neck, fingerboard (fretboard), frets, position markers, body, sound hole, pickguard, saddle, bridge, strings; pickups on the electric. Acoustic and electric side by side with numbered tags on leader lines; one line on pickups | Yes. 14 parts, numbered 1 to 14. Six tags lead to both guitars |
| 2 | Step 2 "Get ready": three cards (sit tall, hold the pick, fret it cleanly), finger numbers T 1 2 3 4, picking signs | Yes, as two rows of three cards; the sixth card is the left-hander note from the spec |
| 3 | Step 3: string 6 thickest and lowest, string 1 thinnest, highest and closest to the floor; students make their own memory line, saved in `fs`; one finger per fret | Yes. `fs.line`, optional, up to 80 characters |
| 4 | Step 4 becomes "Hear the open strings": no instruction to turn pegs for class students; sing on "loo", hum while plucking; ear quiz stays; separate "Your own guitar at home" box; tick reads "I can hear and match all six open strings"; octave note | Yes. Test `test_step_4_no_tuning_instruction_outside_the_home_box` |
| 5 | Step 5 as specified, with the finger numbers from step 2 | Yes |
| 6 | Step 6: top line string 1, bottom line string 6; stacked numbers are a chord; frets counted from the nut; rhythm by listening or from the staff above; the booklet's three notes | Yes. The three notes are the lesson example; the check uses other lines |
| 7 | "Sing it first" callout in steps 4 and 7 | Yes |
| 8 | Step 7: Em kept; the TAB line is E, F, G on string 1 | Yes |
| — | Structure cues: small label above the title, one-line subtitle, rows of three cards, numbered labels, callouts | Yes, in family style. The label reads "First Steps · step 2 of 7" in sentence case, not "// step 02": the design skill rules out zine-style eyebrows. No pink, yellow or teal from the booklet |

## Second relay: the guitar drawing is now a separate design job

The main session then relayed that Justin wants a much better guitar illustration, to be drawn by a design agent and approved by him. So:

- The drawing is behind one function: `guitarArt({kind:'acoustic'|'electric', highlight:<part id|null>, strings:<null|1-6>})`, which returns an SVG string (viewBox `0 0 720 280`, head to the left, string 6 at the bottom).
- Part ids, each a `<g data-part="…">`: `headstock, machineHeads, nut, neck, fingerboard, frets, positionMarkers, body, soundHole, pickguard, saddle, bridge, strings, pickups` (the list is `GPARTS`). The electric has no `soundHole` or `pickguard`; the acoustic has no `pickups`.
- Each string is `<path data-string="1…6">`, plus a wide invisible twin (class `gh`) as the tap target.
- `GART.anchor` gives one point per part for the leader lines. A new drawing needs to supply these points too, in its own 720 by 280 space.
- What ships now is a **plain placeholder**, not approved artwork. Its proportions are true (frets placed by the twelfth root of two on a 650 mm scale, 14 frets clear of the acoustic body, saddle at the scale length), but it is not the hand-made drawing the spec's Design section asks for. **That part of the spec is not met until the design job lands.**
- No test reads the drawing's geometry. Tests use `data-part`, `data-string` and `data-ask` only.

## Spec, item by item

### Decisions
| # | Decision | Result |
|---|---|---|
| 1 | First Steps before the Path, unless the placement quiz is passed | Met. F1, F10, F11 |
| 2 | Tabs as needed; teacher mode shows all | Met. F12 |
| 3 | Em in step 7, then the Path at A·E | Met. F9, F10 |
| 4 | Reference tones and clip-on tuner advice; no microphone | Met, as changed by amendment 4 |
| 5 | Left-handed flip later; short note now | Met (step 2 card) |
| 6 | Guitar only now | Met. F15 |
| 7 | Illustrated, warm, hand-drawn | **Partly.** Layout, type, colour and words are in family style. The guitar drawing is a placeholder (see above) |

### The seven steps
| # | Title | What it teaches | Check |
|---|---|---|---|
| 1 | Meet the guitar | Two guitars, 14 numbered parts; tap a number for its name and what it does; pickups line | Tap quiz: five parts right first time. A wrong tap says "You tapped the body. Look again for the sound hole." |
| 2 | Get ready | Sit tall, hold the pick, fret cleanly, finger numbers, picking signs, left-hander note | Honour tick "I can sit and hold it comfortably" |
| 3 | The strings | Numbers 6 to 1, names E A D G B E, own memory line, one finger per fret; tap a string to hear it | Five questions right first time: lit string to name, number to name, name to number |
| 4 | Hear the open strings | Six looping reference notes, sing then hum and pluck, class tuning rule, home tuner box | Ear check, four pairs (higher or lower), then honour tick "I can hear and match all six open strings" |
| 5 | Chord diagrams | The neck standing up beside an A chord box drawn by `box()` | Four questions on a D diagram right first time: finger, fret, open strings, strings not played |
| 6 | TAB | A TAB printed by `mkTab()`, with play-back, beside the strings lying flat | Three notes read (string and fret) right first time; play-back sounds them |
| 7 | First sound | Em from `box()`, tap to hear; E F G on string 1 with play-back | Band plays Em (count-in, eight bars); honour tick; "Start the Path" |

### Behaviour
| Spec line | Result |
|---|---|
| First open: only First Steps, dots 1 to 7, Back/Next, Next disabled until the check passes; header, metronome bar and picker hidden | Met. F1, F2. The header keeps the name and a Teacher mode button |
| "I already play": 8 items from steps 1, 3, 5, 6 | Met. F11. Two from each. All right: complete, `placed:true`. Otherwise the steps with a wrong answer are named and the first opens |
| Revisit from the Path without losing progress | Met. "First Steps" link in the Up next bar (F10) |
| Returning students skip First Steps and keep their tabs | Met. F13 (see judgement call 1) |
| Teacher mode: all tabs, never forced | Met. F12 |
| A new tab is announced once | Met. F12. A "New for you" box at the top of the Path |
| Other instruments: 0.9 behaviour with a one-line note | Met. F15 |
| `fs` saved in `shredder`, default absent; old saves and backups import; backup includes `fs` | Met. F13, F14 |

### Hard constraints
| Constraint | Result |
|---|---|
| Path, Gig, Record unchanged once open | Met. `test_path_gig_and_record_are_as_0_9_once_open` compares the HTML of the Up next bar (minus the new link), neck, stage, side column, Gig and Record against 0.9 (`90719f9`) on three stages |
| Key `shredder`; save only gains `fs` | Met. F14, F16 |
| No alert/confirm/prompt; no network or libraries; one file | Met. F16 |
| Dominant and function colours unchanged | Met. F16 checks the five tokens and that First Steps' CSS uses none of them |
| Version 0.11 in title, header, backup, newer-version message | Met |

### The `fs` field
`{done:[1…7], complete:bool, placed:bool}` and, only when they apply: `seen:[tab ids already announced]`, `ear:true` (step 4's ear check passed), `line:"…"` (own memory line), `all:true` (a pre-0.11 student who later passed a First Steps check: keeps every tab).

## Every fact taught (for the theory check)

Parts (step 1):
1. Headstock: the flat end, also called the head; the strings finish there.
2. Machine heads: also called tuning pegs; each tightens or loosens one string.
3. Nut: the thin strip where the head meets the neck; each string sits in a groove.
4. Neck: the long part the fretting hand holds.
5. Fingerboard: the front face of the neck, also called the fretboard.
6. Frets: thin metal strips across the fingerboard; press a string just behind one to change the note.
7. Position markers: dots; on most guitars at frets 3, 5, 7 and 9, with two at fret 12.
8. Body: rests on your leg; an acoustic body is a hollow box that makes the strings louder.
9. Sound hole: the round hole under the strings of an acoustic; lets the sound out.
10. Pickguard: a thin plate beside the sound hole; protects the wood from the pick.
11. Saddle: the thin strip set into the bridge; the strings rest on it.
12. Bridge: holds the strings onto the body.
13. Strings: six, thick to thin; from the machine heads, over the nut, to the bridge.
14. Pickups: on an electric, where the sound hole would be; work like a tiny microphone for the strings; a magnet senses each steel string vibrating.

Get ready (step 2):
- For right-handers the left hand frets and the right hand strums.
- Sit at the front of the chair, back tall; the waist of the guitar on the right leg; neck slightly up, never down.
- Pick between the pad of the thumb and the side of the first finger, only the tip showing; strum from the wrist, not the elbow.
- Fingertips just behind the fret wire; thumb behind the neck, pointing up, never towards the head; fingers arched; short nails help.
- Finger numbers: T thumb, 1 index, 2 middle, 3 ring, 4 little.
- Downstroke sign is a square arch (pick towards the floor); upstroke sign is a V; down on the beat, up on the "&".
- Left-handers mirror everything; many play a left-handed guitar, some play the usual way round.

Strings (step 3):
- String 6 is the thickest and lowest, low E. String 1 is the thinnest and highest, high E, closest to the floor when the guitar is held.
- String 6 to string 1: E A D G B E (so 5 = A, 4 = D, 3 = G, 2 = B).
- One finger per fret at the first three frets: fret 1 finger 1, fret 2 finger 2, fret 3 finger 3.
- The drawing shows the guitar flat on the lap, strings up, with string 6 nearest the player (at the bottom).

Open strings (step 4):
- Reference pitches: string 6 E2 82.41 Hz, 5 A2 110.00, 4 D3 146.83, 3 G3 196.00, 2 B3 246.94, 1 E4 329.63 (MIDI 40 45 50 55 59 64).
- Ear check pairs: E2 and E4 (two octaves), A2 and B3 (14 semitones), D3 and G3 (5), G3 and G♯3 (1). Order within a pair is random.
- Guitar music is written an octave higher than it sounds, to fit the treble clef.
- Home box: clip the tuner on the headstock; check the letter; turn the machine head slowly until the needle is in the middle; if too high, loosen below the note and tune up to it; coming up from below helps the string stay in tune.

Chord diagrams (step 5):
- A diagram is the neck standing up, head at the top. Lines down are strings, string 6 (low E) on the left. Lines across are frets. The thick top line is the nut.
- A dot is a finger; the number in it is the finger; T on some diagrams means thumb. A small circle above a string means open; × means don't play.
- A chord as drawn: string 6 not played; strings 5 and 1 open; fingers 1, 2, 3 at fret 2 on strings 4, 3, 2 (`x02220`, the app's own data).
- Check chord D: `xx0232`, fingers 1 on string 3, 3 on string 2, 2 on string 1; string 4 open; strings 6 and 5 not played. Make-up questions use Am `x02210`, C `x32010`, A.

TAB (step 6):
- TAB is short for tablature. Six lines are six strings: top is string 1 (high E, thinnest), bottom is string 6 (low E, thickest).
- A number is a fret; 0 is open; frets are counted from the nut (0) towards the bridge. Read left to right. Stacked numbers are a chord.
- TAB doesn't show rhythm on its own: learn it by listening or from the staff above.
- Lesson TAB: string 6 fret 3 = G; string 2 fret 1 = C; string 3 open = G; then all six strings stacked = E minor (`022000`).
- Check lines: (string 5 fret 2 = B, string 3 open = G, string 1 fret 3 = G); (string 6 open = E, string 4 fret 2 = E, string 2 fret 3 = D); (string 1 fret 1 = F, string 5 fret 3 = C, string 3 fret 2 = A).

First sound (step 7):
- E minor is written Em and needs two fingers: finger 2 on string 5 (A) at fret 2, finger 3 on string 4 (D) at fret 2; the other four strings are open. This is the app's Em (`f 022000`, `g 023000`).
- Strum all six with one downstroke.
- String 1 open, fret 1, fret 3 are E, F, G: mi, fa, so in C major. Finger 1 for F, finger 3 for G.
- The band counts in "1, 2, then 1 2 3 4" and plays Em for eight bars, four strums a bar, at the Path tempo (70 bpm for a new student).

Memory line offered as an example: "Emus And Dingoes Go Bush Early". I wrote it; I did not search to confirm nobody else has used it.

## Design checker

`python3 <skill>/scripts/check_design.py index.html --lab guitar` gives 35 PASS, 1 FAIL, 5 WARN, line for line what `main` (0.9) gives:

- **FAIL, Number-diamond trace: missing.** Already failing on 0.9. Not fixed: adding the trace restyles every page of the app, which this spec does not cover. F17 allows this one FAIL by name and fails on any other. For Justin to decide.
- WARN, shared layer marker absent; 13 colours outside the family (necks, finishes, keyboards: all from before 0.11); no print rules; the name "shredder" (the storage key); "shouting capitals" false alarm on the footer. All from before 0.11.
- First Steps adds no hex colours of its own: it uses the app's tokens plus two new ones, `--gold` (the skill's value) and `--onfin` (text on the signature colour, 5.4:1 or better on all four Finish colours in both themes by my arithmetic; not checker-verified).

Screenshots: `shots/` has every step, the four quiz checks, the placement result and the opened Path at 360 and 1280 in dark and light (52 files). I looked at a sample of 13 across those, not all 52. Full-page shots at 360 show the sticky tab bar part-way down the page; that is how full-page capture draws a sticky bar, not a layout fault.

## Judgement calls

1. **Returning saves keep every tab.** The spec says both "nobody loses access to anything they already use" and "tabs-as-needed is computed from their gates". These clash for a 0.9 student with a level set but no gate. I took the first: a save with progress and no `fs` skips First Steps and keeps all seven tabs. Nothing is written for it, so a 0.9 save stays byte-for-byte as it was. Tabs-as-needed applies to students who came through First Steps.
2. **What counts as progress:** any level above 0, gate, mark, sign-off, best tempo, warm-up day, journal entry, one-minute log, or a gig band with a name typed in. Settings alone (tempo, Finish, stage) do not.
3. **A half-finished `fs` resumes First Steps** at the first step not passed, rather than skipping it, despite "or `fs` already set" in the spec. Otherwise a reload at step 3 would let a beginner through.
4. **Record opens by name on a first visit** (`#record`, from the "I have a backup to bring back" link on step 1). Without this a student on a new device, or in a viewer that blocks storage, could not import a backup. The tab bar then shows First Steps and Record.
5. **A tab that has opened stays open** if its gate later closes.
6. **Quiz rule:** a check needs N answers right first time. A miss is explained, the question stays until answered, and one more is asked. The placement quiz gives one go per question with no feedback until the end.
7. **Partial placement** ticks off every step without a wrong answer (including 2, 4 and 7) and leaves only the missed ones.
8. **Reference tones use the Warm-up tab's triangle-wave voice, not the plucked voice.** The plucked voice is measurably flat on high notes (about 10 cents at E4 by my calculation), which is wrong for a pitch reference. Strings, TAB play-back and Em use the plucked voice.
9. **The tap quiz is answered on the numbered tags,** not on the part shapes, which overlap.
10. **Existing tests:** `uihelp.open_app` seeds a returning student's save by default, with a comment, rather than editing 90 call sites. Seeds that already hold progress are untouched. Two U1 cases use `returning=False`; `sandbox()` uses Teacher mode for tabs other than Record; six version strings moved to 0.11 and three test names were renamed to match. No assertion was loosened.
11. **Stage 2 gate without stage 1** opens Technique, Invent and Gig but not Rudiments and Warm-up, as the spec's wording has it.

## Gaps and things to know

- **The guitar drawing is a placeholder** awaiting the design job and Justin's approval. The hand, pick and picking-sign sketches are also mine and unapproved.
- **I never saw the booklet.** Vocabulary and conventions follow the relayed points; someone should compare against the booklet itself.
- **Storage-blocked viewers** (such as a sandboxed preview) treat every visit as a first visit, so First Steps shows each time. The placement quiz or a backup import gets past it.
- **Existing Path cards disagree with First Steps in two places** and were left alone under "content unchanged": the stage 1 "six strings" card uses the common "Eddie Ate Dynamite" line, and stage 1's "Parts of the guitar" card says "tuners" and "fretboard".
- **Step 5's quiz diagram is always D** for the first four questions.
- **Accessibility:** tags are keyboard-reachable buttons, and during the check their labels are "Label 3" so names are not given away. A screen-reader user cannot do the tap quiz or read the printed TAB unaided. Tapping a string on the drawing has no keyboard path; the row of string buttons does the same job.
- **Not tested:** real phones, Safari, Firefox. Chromium only, as for the other suites.
- **Two tests skip** on a clone without commit `90719f9` or without the design skill installed. Both ran here.
- Quiz questions are random, so one run does not cover every question; the quiz tests answer whatever is asked.
- The `--onfin` contrast figures and the 10-cent figure are my own sums, not measured by a tool.

## Tests

`tests/test_firststeps.py`, 51 tests: F1 first open · F2 Next gated at every step · F3 wrong answers · F4 tap quiz · F5 strings · F6 tones and ear check · F7 diagram answers read off the drawn diagram · F8 TAB as printed and as heard · F9 Em against the Path's Em box · F10 Start the Path · F11 placement (all right; three wrong-answer routes; quit) · F12 tabs as needed · F13 returning saves · F14 `fs` in saves and backups, 0.7/0.8/0.9/bare imports, odd values · F15 other instruments · F16 layout, tap targets, drawing text size, no pop-ups or network · F17 design checker · plus the step 4 amendment test, the memory line, string taps, and Path/Gig/Record against 0.9.

| Suite | Result on `4626acb` |
|---|---|
| All (`tests`) | 434 passed, 0 failed, 0 skipped |
