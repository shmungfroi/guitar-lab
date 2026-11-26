# Independent check: build 0.6 against SPEC_06

Date: 26 Nov 2026. Checker did not build this and did not read BUILD_REPORT.md, TEST_BASELINE.md or the test files.
Inputs: SPEC_06.md and /home/claude/guitar/index.html (110,455 bytes), loaded over file:// in headless Chromium (Python Playwright) at 360, 390 and 1280 px, light and dark.
Method: UI driven through the DOM; Web Audio calls intercepted so every scheduled note (pitch, time, part) could be compared with what the screen shows. index.html and tests were not edited.

## Overall

No Musts found. All five Must items pass. 12 of 15 Should items pass, 2 partial (S11, S12). 8 of 9 Could items pass, 1 partial (C8). Seven new findings: 4 Should, 3 Could (listed at the end).

Sweep: 5 instruments x 8 stages x 7 tabs, 390 and 1280 px, light and dark: 0 console errors or warnings, 0 page errors, 0 horizontal page overflow.

## Must

| ID | Verdict | Evidence |
|---|---|---|
| M1 | PASS | One name typed on Guitarist only: all four phases read "Guitar: Mia Nguyen", headed "same roles". Three names (guitar, bass, drums): phase 1 "roles as entered"; phases 2 to 4 rotate among those three roles only, back to the start in phase 4. Keys and vocals never appear. Rotation off: same roles every phase. Two bands: the one-singer band stays "Vocals: Lee". |
| M2 | PASS | Lit white keys fill rgb(122,92,18) against unlit rgb(236,226,200), label rgb(255,250,240) bold, about 6:1 on the key. Lit black keys gold with dark label. Each lit key carries its note name; a dot marks the root. Fills are fixed, so identical in light and dark; screenshots at 390 px read clearly in both. See new finding N7 (minor). |
| M3 | PASS | See the table below. Bass and keys panels, keyboard highlights and the audio all agree at capo 0, 1, 2, 4 on an A-shape and a C-shape stage, with correct spelling. Also spot-checked: Beyond capo 4 = E♭ minor (C♭ and A♭m spelt correctly), Hallelujah capo 4 = E major with G♯7 spelt G♯ B♯ D♯ F♯. |
| M4 | PASS | At 360 and 390 px, drum grid wrapper has overflow-x:auto, scrollWidth equals clientWidth (328 and 358), last column's right edge at 284 px for the 8-column grid, inside the wrapper. All beats visible without scrolling. Page overflow 0. |
| M5 | PASS | Typed "Mia Nguyen" and "The Wombats 7B" one key at a time (30 ms apart): full value kept, focus stayed on the same field, the input DOM node is the same object afterwards, run sheet updated live. Clearing and retyping a field also keeps focus. Values survive reload. |

### M3 detail (panel text, lit keys and scheduled audio)

| Stage | Capo | Sounding key shown | Bass panel | Keys panel | Band audio (bass root; keys) |
|---|---|---|---|---|---|
| A and E | 0 | A major | A: A string open, fifth E D-string fret 2. E: E string open, fifth B A-string 2 | A C♯ E; E G♯ B | A; A C♯ E |
| A and E | 1 | B♭ major | B♭: A string fret 1, fifth F D-string 3. F: E string 1, fifth C A-string 3 | B♭ D F; F A C | B♭; B♭ D F |
| A and E | 2 | B major | B: A string 2, fifth F♯ D-string 4. F♯: E string 2, fifth C♯ A-string 4 | B D♯ F♯; F♯ A♯ C♯ | B; B D♯ F♯ |
| A and E | 4 | D♭ major | D♭: A string 4, fifth A♭ D-string 6. A♭: E string 4, fifth E♭ A-string 6 | D♭ F A♭; A♭ C E♭ | D♭; D♭ F A♭ |
| C, G, F | 0 | C major | C: A string 3. G: E string 3. F: E string 1 | C E G; G B D; F A C; Fmaj7 F A C E | C; C E G |
| C, G, F | 1 | D♭ major | D♭: A string 4. A♭: E string 4. G♭: E string 2 | D♭ F A♭; A♭ C E♭; G♭ B♭ D♭; G♭maj7 G♭ B♭ D♭ F | D♭; D♭ F A♭ |
| C, G, F | 2 | D major | D: A string 5 (or open D, fifth A on G string 2). A: A open. G: E string 3 | D F♯ A; A C♯ E; G B D; Gmaj7 G B D F♯ | D; D F♯ A |
| C, G, F | 4 | E major | E: E open. B: A string 2. A: A open | E G♯ B; B D♯ F♯; A C♯ E; Amaj7 A C♯ E G♯ | E; E G♯ B |

Every lit key sits on the correct physical key and its printed label matches the spelling (for example the A♯/B♭ key is labelled B♭ in B♭ major and A♯ in B major). Bass fret positions are all correct for a four-string in standard tuning. All 18 guitar shapes in the data were also checked: fretted notes match the stated spelling and the lowest sounding string is the root in every case.

## Should

| ID | Verdict | Evidence |
|---|---|---|
| S1 | PASS | For all 8 stages on the stage pattern, and all 8 x 4 Finish feels, the dots in the drum grid were compared with the hi-hat, snare, rim and kick hits the band actually schedules in bar 1: 40 of 40 match. Four-downs stage shows four hats and the band plays four. Shuffle hats are swung (2/3, 1/3) and the note says so. 3/4 shows kick on 1 and rim clicks on 2 and 3. 6/8 shows six hats, kick on 1, snare on 4. |
| S2 | PASS | Synchronous double click, a real double click and three clicks 60 ms apart: only one band sounds (one hi-hat stream with even 0.5 s gaps at 120 bpm, one count-in). The earlier run is cancelled. |
| S3 | PASS | Six damaged saved states (unknown song ids, 7 songs, duplicates, non-string names, unknown roles, 200-character names, block -3 and 9999, bpm "fast", gig as array or string, broken JSON): page loads with 0 errors, falls back to defaults, trims to 4 songs and 40 characters, HTML in names is escaped, chart still plays. |
| S4 | PASS | "View" on all six songs, including the two unchosen (Hound Dog, Blue Suede Shoes), opens title, credit, year, backstory and chart without changing which songs are ticked. |
| S5 | PASS | Stage 2 link reads "Hear a 12-bar in A: Rock Around the Clock" and searches for Bill Haley. Johnny B. Goode is now under Also try as "the same 12-bar form, recorded in B♭". |
| S6 | PASS | Vocal steps reworded (hum along, sing roots in sol-fa, entries on cue, leave the whole band on). Cue sheet has a "Roots in sol-fa" line plus the chart in sol-fa. Checked every stage: A major do/fa/so; A minor la/mi (E7 root = mi); C major do/fa/so/la, E7 = mi; Greensleeves la so fa mi and do so la mi; B minor la mi so re fa do re mi. All correct, la-based minor throughout. With capo 3 the syllables stay and the letter names move correctly (C major becomes do = E♭, so = B♭, fa = A♭; B minor becomes la = D). |
| S7 | PASS | 4/4: "roots on beat 1, then beats 1 and 3, then root and fifth". 3/4 (Amazing Grace): "one root on beat 1 of every bar, left to ring ... fifth on beat 3". 6/8 (Greensleeves, Hallelujah): "count 1 2 3 4 5 6 ... roots on 1, then on 1 and 4 ... fifth on 4", tempo given as dotted crotchet. Wording, criteria and the band's own bass part agree. |
| S8 | PASS | Seeded pre-0.6 data (levels, sign-offs, best tempo, changes and journal with no instrument): all shows under Guitar. Bass shows 0/5, no changes, no best tempo, 0 sign-offs, rudiments locked. Logged a bass change, level, sign-off and tempo: stored with a bass tag, guitar figures unchanged. |
| S9 | PASS | With all four parts switched off on the Path, the gig chart still schedules guitar, bass, keys and drums straight to the main output, bypassing the Path part switches. |
| S10 | PASS | Tapping a timer button plays a tick at once (audio started on the tap). Ran a 20-minute block on a simulated clock: three beeps scheduled at 0:00 and "Time: change over." shown. |
| S11 | PARTIAL | Present hides all three setup blocks and enlarges the timer (140 to 240 px) and run-sheet rows (14 to about 31 px at 1280). But the chart is not really scaled: road map width 1074 to 1102 px, chord letters the same size, and the "Phase 1 · 20 min" headings stay small. Header, tabs and metronome bar stay on screen. |
| S12 | PARTIAL | With the feel switch off: Gig metronome shows "Boogie shuffle, swung" at 120 with swung clicks (0.333/0.167 s) for the 12-bars, and "Straight eighths" at 140 for La Bamba; Path keeps its own tempo. But if "Finish feel" was left on on the Path, the Gig metronome and gig band use the Finish pattern (for example Tangos four-downs on the 12-bar boogie), and there is no switch on the Gig tab to turn it off. |
| S13 | PASS | Keys buttons read "A — A C♯ E", "B♭ — B♭ D F" and so on; aria-label "Play A: A C♯ E". |
| S14 | PASS | Flamenco on a 3/4 or 6/8 song: a note on the chart and metronome card plus a 7-second message, "The band can't follow the Flamenco feel on this song: its count doesn't fit one bar of 3/4 ...". Changing Finish or the feel switch during play stops the band ("Feel changed, so the band has stopped. Press Play again.") with no further notes scheduled; same on the Gig tab. |
| S15 | PASS | Let It Be, Hallelujah and Hotel California show "Listen for the entry: the recording shows where the voice comes in." No pickup claim remains for them. |

## Could

| ID | Verdict | Evidence |
|---|---|---|
| C1 | PASS | All 78 CSS class names and every id used in the stylesheet are referenced in the markup or script. |
| C2 | PASS | Each keys card names the voicing shown ("Low to high: C♯ E A · 1st inversion"); maj7 cards show four lit notes and "Right hand can leave the root to the left hand". Inversion names are correct for the keys as drawn. |
| C3 | PASS | D roots show "Or play the open D string, with the fifth (A) on the G string, fret 2." |
| C4 | PASS | "Our own arrangement" appears once. |
| C5 | PASS | "120 bpm is a practice tempo ..." under each gig chart. La Bamba chart reads A D, E D, A D, E D. |
| C6 | PASS | "Whole block: 20 min" timer button follows the block length. Hint: "3 of 4 chosen. Choose 1 more to fill the set; the run sheet works with what you have." |
| C7 | PASS | Drum rows "Hi-hat (closed)", "Snare", "Rim click", "Kick" with a how-to line; run sheet columns "Band / Song to rehearse / Who plays what"; role fields "Guitarist, Bassist, Drummer, Keys player, Singer". |
| C8 | PARTIAL | Warm-up, steps, journal prompts and metronome note are per instrument. Still guitar-only for a drummer or singer: stage 1 knowledge cards ("The six strings", "Parts of the guitar", "Reading a chord box"), Rudiments and Technique (labelled as guitar drills rather than made neutral), and Invent is the same chord loop for every instrument. |
| C9 | PASS | Record is headed per instrument; journal entries carry an instrument tag; the open gig song has an instrument switch with bass, drums, keys and vocal panels. |

## Other checks asked for

- Lyrics and melodies: no copyrighted lyrics or transcribed melodies anywhere in the visible text, labels or placeholders (1,074 unique lines scanned). The only sung syllables are "A-" and "-ma-" in the Amazing Grace pickup note, which is public domain (1779). The boogie riff TAB is a generic pattern, not a song melody.
- Song facts: chord maps for Let It Be, Hallelujah, Greensleeves, Hotel California and the 12-bar are right for the charted keys. Backstory dates and credits are correct.
- Voice: reads as plain teacher language, Australian spelling (crotchet, quaver, practise/practice used correctly). One exception in N3.
- Console: 0 errors or warnings in every run.

## New findings

| # | Class | Finding |
|---|---|---|
| N1 | Should | S12 gap: the Finish feel switch set on the Path carries into the Gig tab (band and metronome), with no way to change it there. A 12-bar boogie can play as Tangos four-downs. |
| N2 | Should | S11 gap: Present mode does not enlarge the chart or the phase headings. |
| N3 | Should | American "eighths" in student text ("Straight eighths", "Backbeat eighths", "Palm-muted eighths", "Strum eighths") beside "quavers" and "crotchet" elsewhere. Should be quavers throughout. |
| N4 | Should | After changing the capo on bass or keys, the One-minute changes card still shows the old chord names (Bm ↔ F♯ at capo 4 on Beyond) until the page is redrawn; after reload it shows E♭m ↔ B♭. The part panel itself is right. |
| N5 | Could | The drum panel describes the groove with guitar strum names ("the part the band's drummer plays: d · du · udu", "bass, strum, strum", "thumb on 1 and 3, chords on the and of 2"). A drummer needs a drum description. |
| N6 | Could | "F#" with a plain hash in the Function card and the Invent pool; ♯ everywhere else. The Function card also keeps guitar shape names under a capo for bass and keys. La Bamba's play note mentions "bars 10 and 12" though its chart is a 4-bar loop. "(bpm (dotted crotchet))" has doubled brackets. Vocal cue sheet says "Lyrics aren't reproduced here" on the instrumental 12-bar boogie. |
| N7 | Could | In light mode a lit black key (pale gold) sits close in tone to the cream white keys. It is still readable because of its outline, label and root dot. |
