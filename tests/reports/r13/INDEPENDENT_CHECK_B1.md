# The Guitar Lab 0.10 (R13 batch 1): independent check

Label: **independent check**. Done by a checker that did not build this batch.
Date: 27 Nov 2026. Branch `build-r13` at `fe91466`. Baseline: `90719f9` (0.9).

Inputs used: `SPEC_R13.md`, `R13_Framework.md` (sections 2.1, 2.2, 4, 5), `index.html`, `fonts/`.
Not read: `BUILD_REPORT_B1.md`, `THEORY_CHECK_B1.md`, the builder's tests. Only `tests/conftest.py` and `tests/uihelp.py` were looked at, for how to open the page.
The existing suites were not run (as instructed).

My scripts are in `tests/reports/r13/check_b1/` (Playwright, Python, headless Chromium):
`lib.py`, `c1_unchanged.py`, `c2_bass.py`, `c3_sweep.py`, `c4_shots.py`, `c5_words.py`, `c6_misc.py`, and seven screenshots in `shots/`.

## Verdict

No Must findings. Every hard constraint in the spec held under test.
One Should finding is worth fixing before bass goes to students: with a capo set on a stage, the bass Invent cards name one set of notes and the band plays another (S1).

## Results

| # | Check | Result | Measured evidence |
|---|---|---|---|
| 1 | Guitar unchanged from 0.9 | PASS | 31 rendered blocks compared as `innerHTML` in two save states (fresh, and all 8 stages passed): 8 side panels, 8 stage panels, 8 stage TABs, Warm-up, Rudiments, Technique, Invent (before and after a roll, same random seed), Gig, Record. 0 of 62 differ. Only the title and header differ: "0.9" to "0.10". |
| 2 | Drums, keys, vocals unchanged from 0.9 | PASS | Same 31 blocks, two states, each instrument: 0 of 186 differ. No console messages. |
| 3a | Bass sees only bass items on Rudiments | PASS | 8 cards, in data order, every id `bs-…`, keys `r:bs-…@bass`. Two names are the same as guitar's ("Pulse on one string", "The spider (1-2-3-4)") but with their own ids and bass text. |
| 3b | Finish filter: core + rock + current Finish | PASS | Headings per Finish: Rock = Core, Rock and roll. Flamenco = Core, Flamenco, Rock and roll. Bossa = Core, Bossa, Rock and roll. Hair metal = Core, Hair metal, Rock and roll. Item sets match the data each time. 0 guitar technique names. |
| 3c | Flamenco group marked optional | PASS | "Tangos roots" carries an "Optional" tag; it is the only flamenco bass item. |
| 3d | Tangos binary | PASS | Text: "Tangos is counted in four. Beat 1 is light…". Grid: `count 1 2 3 4 / play – R R R`. No 12-count. |
| 3e | Bass cards on all 8 stages | PASS | Bass cards per stage: 3, 3, 2, 2, 1, 2, 1, 2, all rendered, followed by the shared theory cards. No guitar-only card (strings, parts, chord boxes, TAB, minor, barre) on any stage. |
| 3f | Stage 2 shows a four-line TAB | PASS | One TAB, 4 lines, labelled G D A E top to bottom, three bars (A, D, E). Guitar still gets its six-line TAB (check 1). |
| 3g | No guitar-only words in bass content | PASS (bass content) / PARTIAL (whole bass Path) | Rudiments, Technique, Invent, bass stage cards, stage-2 note, Invent prompts, saved journal line: 0 hits for palm muting, rasgueado, golpe, chord box, pendulum, strum, six-line, Guitar Book, plectrum, barre, voicing. Outside R13's scope, text carried over from 0.9 is still shown to a bass player on the Path: see S2. |
| 4 | Gates per instrument | PASS | Passing stage 1 on bass through the level buttons: bass locked rudiments 4 to 3, locked techniques 8 to 5; `gates` = `a-e@bass` only. Guitar still "0 of 5 steps done" with 5 locked rudiments (same as a fresh guitar); drums 5 locked. |
| 5a | Old stray keys: load, hidden, not deleted | PASS | Seeded a 0.9 save with `r:pulse@bass`, `r:spider@bass`, `t:power@bass`, `t:boogie@bass`, `r:cross@drums`, `best["r:pulse@bass"]`. On bass: 0 Done tags, every level "Not started", no best tempo shown, Record says "None yet." and "None logged yet." After a level change on bass, all 7 old level keys and both best-tempo keys were still in storage. Guitar's own `r:pulse` still shows Done. |
| 5b | Save key and shape | PASS | `localStorage` keys: `shredder` only. Setting a bass level and a best tempo added `r:bs-pulse@bass`, `t:bs-roots@bass` and `best["r:bs-pulse@bass"]`; the 18 top-level keys did not change. |
| 5c | 0.7, 0.8, 0.9 backups and bare state import | PASS | All four imported through the Backup card (paste, Import, Replace): levels, best tempos and journal equal to the source. A `format: 2` backup is refused with the "newer version … (0.10)" message. |
| 5d | Version 0.10 everywhere | PASS | Title, header, backup `version` field (read from a Copy backup), and the newer-version message all say 0.10. "0.9" remains only in two code comments. |
| 6a | Bass Invent: roll, tap cells, play | PASS | Tested on stages 1, 2, 4, 6, 8. Cells: 8 in 4/4, 6 in 3/4 and 6/8. Last cell cycles R, 5, 8, approach, empty; other cells R, 5, 8, empty. Real oscillator starts were read: 21 to 48 bass notes per run. In every whole bar the first note was the chord's root and the approach note was one semitone from the next root: below it everywhere except into open E, where it was F above (MIDI 29 into 28), 9 such bars measured, never D♯. No note below low E. |
| 6b | Invent save | PASS | Journal entry: `inst: bass`, `tag: Invent`, "Loop: A – E – A – E · bar of bass: root on 1, root on 3, approach note on &". No guitar wording. Record shows it with Bass and Invent tags. 6 prompts, none with guitar wording. |
| 6c | Invent with a capo set | PARTIAL | Works, but names and sound disagree: see S1. |
| 7a | No alert/confirm/prompt | PASS | No call in the source; 0 calls across the sweep (all three were trapped). |
| 7b | No network | PASS | Only `index.html` and the three font files were requested. The one web address in the file is the recording search link. No script, style or font from outside. |
| 7c | British terms, no lyrics, no method names | PASS | Bass content: 0 hits for eighth/quarter/half/whole note, measure, half/whole step, color, center; 0 hits for 20 method and program names. No quoted lyric lines. Song mentions are titles with a search link only. |
| 7d | On-brand, not AI-looking | PASS | Judged from 7 screenshots covering 360 and 1280, light and dark (Rudiments, Technique, Invent, stage-2 TAB, stage cards). Same cards, type, tags, colours and level controls as guitar; TAB and count grids use the existing mono block; nothing generic. One density note: S3. |
| 8 | Sweep | PASS | 308 views: 5 instruments × 360 and 1280 × light and dark × (Path at all 8 stages, the 6 other tabs, Invent after a roll; bass also Invent built and in 6/8). 0 console errors or warnings, 0 page overflow, 0 dialogs. |
| extra | Instrument switch | PASS | A rolled bass loop is dropped on switching to guitar, and guitar's on switching back. Record lists bass items for bass and nothing for guitar. |

## New findings

### Must
None.

### Should

**S1. Bass Invent with a capo: the cards say one thing, the band plays another.**
Stage 1 with capo 2, on bass: the Invent page says "in B major" and the cards read "B: A string, fret 2" and "F♯: E string, fret 2". The band (and the student's own bar) sounded A and E (MIDI 33 and 28), the same as with no capo. A student who follows the cards plays a tone above the band.
Cause: the names are worked out with the stage capo, but the sound only follows the capo on the Path.
Fix (either): make the band sound at the stage's capo in Invent for instruments with their own Invent; or show the bass Invent names without the capo. The first keeps Invent in step with the Path.
Only bites when a capo is set on that stage. Guitar is not affected by the wording (its Invent shows shapes).

**S2. Guitar wording from 0.9 still shown to a bass player on the Path.**
Outside R13's listed scope (song notes, stage titles, metronome), but a bass student reads it:
- Stage 8 song note: "Bm and F♯ are your first barre chords. The rest you already know."
- Stage 7 song note: "Add a capo to suit your voice: the shapes stay the same."
- Stage 8 title: "Beyond: barre chords" (also in Record and the gate message).
- Stage 4 metronome pattern name: "Bass, strum, strum"; and the standing note "The letters are the guitar's strum…" (this one is deliberate in 0.9).
Fix: give `instData` an optional per-stage song note for bass (as was done for "Also try"), starting with stages 7 and 8. Leave the stage title; it is the shared spine.

**S3. The Bossa bass card is too long for its reader.**
114 words, against 39 to 78 for every other bass item. On a 360-wide phone the text alone fills the screen before the TAB appears.
Fix: keep the rhythm description and the A example; move "Many bossa players take the fifth below the root…" out, or cut it.

### Could

**C1.** The Invent bar summary says "approach note on &" (in the saved journal line and the screen-reader label). It does not say which "and". Fix: name the beat, "the and of 4" (and "the and of 3" in 3/4).

**C2.** "In this band the kick drum plays on beats 1 and 3" (Technique: Locking with the kick) is shown on every stage. It is true on the 4/4 stages; on the 3/4 and 6/8 stages the band's kick is on beat 1 only. Fix: "In four-four, this band's kick…".

**C3.** At 360 the bass spider TAB is 12 px wider than its box (302 in 290) and scrolls inside it. Guitar's spider does the same. No page overflow.

**C4.** The string mnemonic "Eddie Ate Dynamite, Good." is a cut-down common saying, not method text. It reads oddly ending on "Good." Justin may want his own.

**C5.** For Justin's musical review, two places where the build differs from the framework table, both sensible: "Locking with the kick" pushes on the and of 4 (framework said the and of 3); the gallop is "Galloping root", with no palm muting. I found no wrong note, fret or string in my own read-through of every bass item, card and TAB.

## Not tested

- How it sounds by ear, and tuning by ear. Pitches were read from oscillator frequencies only.
- Real devices and other browsers (Safari, Firefox, a school Chromebook). Headless Chromium only.
- A sandboxed frame on the bass tabs. The harness cannot change tabs inside a `file://` sandboxed frame (the same on 0.9), so bass could not be reached there. Storage-blocked behaviour was therefore not rechecked for 0.10.
- Widths other than 360 and 1280.
- NSW syllabus mode and Teacher mode switched on during the 0.9 comparison.
- Guitar, drums, keys and vocals sound against 0.9 (rendered output only was compared).
- Screen reader and keyboard-only use.
- The builder's suites, the build report and the theory report (left unread by instruction).
- Every page in every theme and width by eye: the quality verdict rests on 7 screenshots; the other combinations were checked by script only.
