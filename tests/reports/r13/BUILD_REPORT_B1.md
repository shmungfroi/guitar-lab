# R13 batch 1 build report (0.10): plumbing and bass

**Status: self-check.** Written by the builder against `SPEC_R13.md`. Not an independent check. Not merged.

- Branch `build-r13`. Stage commits: A `9901b56` (plumbing), B `cf039a9` (bass content and tests), C `02c889a` (version 0.10). This report is the commit after C.
- Baseline: `main` 90719f9 (0.9), 383/383.
- Full suites, run once at the end on `02c889a`: **439 passed, 0 failed** (4 min 54 s). `test_chords.py` 185 (163 + 22 new X11), `test_ui.py` 215 (214 + one more version case), `test_timing.py` 6, `test_r13.py` 33 (new). 55 of these are X tests.
- Commits carry the session's own attribution line (Claude Fable 5.2), which is the model that did the work, not the "Opus 5.5" line in the task brief.

## 1. Item by item against the spec

| Spec item | Result | How it was done | Test |
|---|---|---|---|
| Per-instrument content block, JSON `<script type="application/json" id="instData">` | Done | One block after `fretData`: `shared` (theory cards with guitar wording taken out) and `bass`. One item per line. | X11 reads it in Python |
| Accessors `rudOf`, `techOf`, `knowOf`, `part2Of`, `inventOf` | Done | Plus `alsoOf` and `ic()` (the current instrument's block, or null). An instrument with no block falls back to guitar's lists, as on 0.9. | X1, X2, X4 |
| `itemCard` generalised, not forked | Done | Optional `crit`, `opt` (an "Optional" tag), `tab:4` (four-line TAB), `bt` (count line with what to play). Tempo box only where the item has a unit. | X1 (guitar unchanged), X2 |
| Four-line TAB renderer | Done | `mkTab(ev, lines)` takes the string names; `mkTabBass` passes G D A E. `'|'` in the events draws a bar line. Guitar calls are unchanged. | X5, X1 |
| Record reads the instrument's lists | Done | "At Consistent or better" and "Best tempos" use `rudOf()`/`techOf()`. | X6, X7 |
| Finish-group filter (decision 7) | Done for bass | Core, the current Finish, rock and roll. Guitar sees all four. Drums, keys, vocals unchanged until they have content. | X2 (all four Finishes) |
| Stray-key hiding (decision 11) | Done | New ids are `bs-…`, and bass pages read only the bass lists, so `r:pulse@bass` and the like are never shown and never count. Nothing is deleted. | X7 |
| Drums, vocals, keys exactly as 0.9 | Done | No block for them in `instData`. | X1 (drums, keys, vocals) |
| Guitar byte for byte | Done | Snapshot written first, from `git show main:index.html`: Rudiments, Technique, Invent (before and after a pinned roll, two stages), eight side panels, stage song TAB; first-visit and all-gates-passed saves. 42 panels per instrument. | X1 (guitar) |
| Bass Rudiments (8) | Done | Table in section 2. | X2, X11 |
| Bass Technique (10: core 5, rock 2, metal 1, bossa 1, flamenco 1 optional) | Done | Tangos is binary: rest on 1, roots on 2, 3, 4. | X2, X11 |
| Bass Invent "build one bar of bass" | Done | Roll four chords (same roll as guitar), root cards with sol-fa, a bar of quaver cells (8 in 4/4, 6 in 3/4 and 6/8): empty, R, 5, 8, and an approach note in the last cell. The band's bass voice plays the bar under every chord. Saves to the journal in the same entry shape. | X10 |
| Bass cards on all 8 stages, with shared theory cards | Done | 14 bass cards; the stage's shared cards (`e7`, `func`, `four`, `six`, `vii`, `sec`) follow them. | X4 |
| Stage-2 four-line boogie-walk TAB | Done | Three bars: A, D, E. | X5, X11 |
| Guitar wording out of shared theory cards, non-guitar only | Done for bass | Only `func` had any ("The colours on every chord box…" becomes "The colours in the Function card…"). See judgement call 2. | X4 |
| Version 0.10 | Done | Title, header, backup `version`, newer-version message. 0.7, 0.8, 0.9, 0.10 backups and a bare state import. | `test_version_0_10_…` |
| Key `shredder`, save shape, prefixed ids | Held | No new field in the save. Keys written: `r:bs-…@bass`, `t:bs-…@bass`. | X6 |
| No alert/confirm/prompt, no network, one file + fonts | Held | | X12, R1 |
| British terms, no lyrics, no program names, own words | Held | | X12 |

Tests X1–X13: X1 (4), X2 (5), X3 (1), X4 (2), X5 (1), X6 (1), X7 (2), X8 (1), X9 (1), X10 (5), X11 (22, in `test_chords.py`), X12 (2), X13 (8: four widths, light and dark, each over the four Finishes and eight stages).

## 2. Every bass note written (for the theory checker)

Tuning E1 A1 D2 G2 (MIDI 28, 33, 38, 43). In the data, string 0 is the low E. "Named" is the note the wording or the `evn` list gives; "Sounds" is worked out from string and fret. Rows marked (wording) are places the text names that are not in a TAB.

| Where | Bar | String | Fret | Named | Sounds (MIDI) |
|---|---|---|---|---|---|
| Rudiment `bs-pulse` Pulse on one string | 1 | E | 0 | E | E1 (28) |
| Rudiment `bs-pulse` Pulse on one string | 1 | E | 0 | E | E1 (28) |
| Rudiment `bs-pulse` Pulse on one string | 1 | E | 0 | E | E1 (28) |
| Rudiment `bs-pulse` Pulse on one string | 1 | E | 0 | E | E1 (28) |
| Rudiment `bs-alt` Two-finger walk | 1 | A | 0 | A | A1 (33) |
| Rudiment `bs-alt` Two-finger walk | 1 | A | 0 | A | A1 (33) |
| Rudiment `bs-alt` Two-finger walk | 1 | A | 0 | A | A1 (33) |
| Rudiment `bs-alt` Two-finger walk | 1 | A | 0 | A | A1 (33) |
| Rudiment `bs-cross` String crossing and the octave | 1 | E | 0 | E | E1 (28) |
| Rudiment `bs-cross` String crossing and the octave | 1 | D | 2 | E | E2 (40) |
| Rudiment `bs-cross` String crossing and the octave | 1 | E | 0 | E | E1 (28) |
| Rudiment `bs-cross` String crossing and the octave | 1 | D | 2 | E | E2 (40) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | E | 1 | F | F1 (29) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | E | 2 | F♯ | F♯1 (30) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | E | 3 | G | G1 (31) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | E | 4 | G♯ | G♯1 (32) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | A | 1 | A♯ | A♯1 (34) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | A | 2 | B | B1 (35) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | A | 3 | C | C2 (36) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | A | 4 | C♯ | C♯2 (37) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | D | 1 | D♯ | D♯2 (39) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | D | 2 | E | E2 (40) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | D | 3 | F | F2 (41) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | D | 4 | F♯ | F♯2 (42) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | G | 1 | G♯ | G♯2 (44) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | G | 2 | A | A2 (45) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | G | 3 | A♯ | A♯2 (46) |
| Rudiment `bs-spider` The spider (1-2-3-4) | 1 | G | 4 | B | B2 (47) |
| Rudiment `bs-mute` Stopping the ring (wording) | – | A | 0 | A | A1 (33) |
| Rudiment `bs-slide` Hammer-on and slide | 1 | E | 0 | E | E1 (28) |
| Rudiment `bs-slide` Hammer-on and slide | 1 | E | 2 | F♯ | F♯1 (30) |
| Rudiment `bs-slide` Hammer-on and slide | 1 | E | 2 | F♯ | F♯1 (30) |
| Rudiment `bs-slide` Hammer-on and slide | 1 | E | 4 | G♯ | G♯1 (32) |
| Rudiment `bs-slide` Hammer-on and slide | 1 | E | 4 | G♯ | G♯1 (32) |
| Rudiment `bs-slide` Hammer-on and slide | 1 | E | 2 | F♯ | F♯1 (30) |
| Rudiment `bs-oct` Octave shape | 1 | E | 3 | G | G1 (31) |
| Rudiment `bs-oct` Octave shape | 1 | D | 5 | G | G2 (43) |
| Rudiment `bs-oct` Octave shape | 2 | E | 5 | A | A1 (33) |
| Rudiment `bs-oct` Octave shape | 2 | D | 7 | A | A2 (45) |
| Rudiment `bs-oct` Octave shape | 3 | A | 3 | C | C2 (36) |
| Rudiment `bs-oct` Octave shape | 3 | G | 5 | C | C3 (48) |
| Technique `bs-roots` Roots on beat 1 (core) | 1 | A | 0 | A | A1 (33) |
| Technique `bs-roots` Roots on beat 1 (core) | 2 | A | 5 | D | D2 (38) |
| Technique `bs-roots` Roots on beat 1 (core) | 3 | E | 0 | E | E1 (28) |
| Technique `bs-roots` Roots on beat 1 (core) (wording) | – | D | 0 | D | D2 (38) |
| Technique `bs-rootfifth` Root and fifth (core) | 1 | A | 0 | A | A1 (33) |
| Technique `bs-rootfifth` Root and fifth (core) | 1 | D | 2 | E | E2 (40) |
| Technique `bs-rootfifth` Root and fifth (core) | 2 | E | 0 | E | E1 (28) |
| Technique `bs-rootfifth` Root and fifth (core) | 2 | A | 2 | B | B1 (35) |
| Technique `bs-octaves` Root and octave (core) | 1 | A | 3 | C | C2 (36) |
| Technique `bs-octaves` Root and octave (core) | 1 | G | 5 | C | C3 (48) |
| Technique `bs-octaves` Root and octave (core) | 1 | A | 3 | C | C2 (36) |
| Technique `bs-octaves` Root and octave (core) | 1 | G | 5 | C | C3 (48) |
| Technique `bs-approach` Approach notes (core) | 1 | A | 2 | B | B1 (35) |
| Technique `bs-approach` Approach notes (core) | 1 | A | 3 | C | C2 (36) |
| Technique `bs-approach` Approach notes (core) | 2 | E | 2 | F♯ | F♯1 (30) |
| Technique `bs-approach` Approach notes (core) | 2 | E | 3 | G | G1 (31) |
| Technique `bs-approach` Approach notes (core) | 3 | E | 4 | G♯ | G♯1 (32) |
| Technique `bs-approach` Approach notes (core) | 3 | E | 5 | A | A1 (33) |
| Technique `bs-approach` Approach notes (core) | 4 | E | 0 | E | E1 (28) |
| Technique `bs-approach` Approach notes (core) | 4 | E | 1 | F | F1 (29) |
| Technique `bs-walk` Walking four (core) | 1 | A | 3 | C | C2 (36) |
| Technique `bs-walk` Walking four (core) | 1 | D | 2 | E | E2 (40) |
| Technique `bs-walk` Walking four (core) | 1 | D | 5 | G | G2 (43) |
| Technique `bs-walk` Walking four (core) | 1 | D | 6 | G♯ | G♯2 (44) |
| Technique `bs-walk` Walking four (core) | 2 | D | 7 | A | A2 (45) |
| Technique `bs-shuffle` Boogie walk, up and back (rock) | 1 | A | 0 | A | A1 (33) |
| Technique `bs-shuffle` Boogie walk, up and back (rock) | 1 | A | 4 | C♯ | C♯2 (37) |
| Technique `bs-shuffle` Boogie walk, up and back (rock) | 1 | D | 2 | E | E2 (40) |
| Technique `bs-shuffle` Boogie walk, up and back (rock) | 1 | D | 4 | F♯ | F♯2 (42) |
| Technique `bs-shuffle` Boogie walk, up and back (rock) | 2 | G | 2 | A | A2 (45) |
| Technique `bs-shuffle` Boogie walk, up and back (rock) | 2 | D | 4 | F♯ | F♯2 (42) |
| Technique `bs-shuffle` Boogie walk, up and back (rock) | 2 | D | 2 | E | E2 (40) |
| Technique `bs-shuffle` Boogie walk, up and back (rock) | 2 | A | 4 | C♯ | C♯2 (37) |
| Technique `bs-gallop` Galloping root (metal) (wording) | – | E | 0 | E | E1 (28) |
| Technique `bs-bossa` Bossa bass (bossa) | 1 | A | 0 | A | A1 (33) |
| Technique `bs-bossa` Bossa bass (bossa) | 1 | A | 0 | A | A1 (33) |
| Technique `bs-bossa` Bossa bass (bossa) | 1 | D | 2 | E | E2 (40) |
| Technique `bs-bossa` Bossa bass (bossa) | 1 | D | 2 | E | E2 (40) |
| Technique `bs-compas` Tangos roots (flam) | 1 | A | 0 | A | A1 (33) |
| Technique `bs-compas` Tangos roots (flam) | 2 | E | 3 | G | G1 (31) |
| Technique `bs-compas` Tangos roots (flam) | 3 | E | 1 | F | F1 (29) |
| Technique `bs-compas` Tangos roots (flam) | 4 | E | 0 | E | E1 (28) |
| Stage 2 part note (boogie walk: A, D, E) | 1 | A | 0 | A | A1 (33) |
| Stage 2 part note (boogie walk: A, D, E) | 1 | A | 4 | C♯ | C♯2 (37) |
| Stage 2 part note (boogie walk: A, D, E) | 1 | D | 2 | E | E2 (40) |
| Stage 2 part note (boogie walk: A, D, E) | 1 | D | 4 | F♯ | F♯2 (42) |
| Stage 2 part note (boogie walk: A, D, E) | 2 | D | 0 | D | D2 (38) |
| Stage 2 part note (boogie walk: A, D, E) | 2 | D | 4 | F♯ | F♯2 (42) |
| Stage 2 part note (boogie walk: A, D, E) | 2 | G | 2 | A | A2 (45) |
| Stage 2 part note (boogie walk: A, D, E) | 2 | G | 4 | B | B2 (47) |
| Stage 2 part note (boogie walk: A, D, E) | 3 | E | 0 | E | E1 (28) |
| Stage 2 part note (boogie walk: A, D, E) | 3 | E | 4 | G♯ | G♯1 (32) |
| Stage 2 part note (boogie walk: A, D, E) | 3 | A | 2 | B | B1 (35) |
| Stage 2 part note (boogie walk: A, D, E) | 3 | A | 4 | C♯ | C♯2 (37) |
| Card, a-e: The root and the fifth (wording) | – | A | 0 | A | A1 (33) |
| Card, a-e: The root and the fifth (wording) | – | E | 0 | E | E1 (28) |
| Card, a-e: The root and the fifth (wording) | – | D | 2 | E | E2 (40) |
| Card, am-e7: Major or minor? The third decides (wording) | – | A | 3 | C | C2 (36) |
| Card, am-e7: E pulls home to A (wording) | – | E | 0 | E | E1 (28) |
| Card, am-e7: E pulls home to A (wording) | – | A | 0 | A | A1 (33) |
| Card, c-g-f: do, fa and so, down low (wording) | – | A | 3 | C | C2 (36) |
| Card, c-g-f: do, fa and so, down low (wording) | – | E | 1 | F | F1 (29) |
| Card, c-g-f: do, fa and so, down low (wording) | – | E | 3 | G | G1 (31) |
| Card, four-chords: One path through four chords (wording) | – | A | 3 | C | C2 (36) |
| Card, four-chords: One path through four chords (wording) | – | E | 3 | G | G1 (31) |
| Card, four-chords: One path through four chords (wording) | – | A | 0 | A | A1 (33) |
| Card, four-chords: One path through four chords (wording) | – | E | 5 | A | A1 (33) |
| Card, four-chords: One path through four chords (wording) | – | E | 1 | F | F1 (29) |
| Card, six-eight: Step down, or pull home (wording) | – | A | 0 | A | A1 (33) |
| Card, six-eight: Step down, or pull home (wording) | – | E | 3 | G | G1 (31) |
| Card, six-eight: Step down, or pull home (wording) | – | E | 0 | E | E1 (28) |
| Card, hallelujah: Walking into a chord (wording) | – | E | 4 | G♯ | G♯1 (32) |
| Card, hallelujah: Walking into a chord (wording) | – | A | 2 | B | B1 (35) |
| Card, beyond: One shape, any root (wording) | – | A | 2 | B | B1 (35) |
| Card, beyond: One shape, any root (wording) | – | D | 4 | F♯ | F♯2 (42) |
| Card, beyond: One shape, any root (wording) | – | E | 2 | F♯ | F♯1 (30) |
| Card, beyond: One shape, any root (wording) | – | A | 4 | C♯ | C♯2 (37) |
| Card, beyond: A minor key with sharps (wording) | – | E | 1 | F | F1 (29) |
| Card, beyond: A minor key with sharps (wording) | – | E | 2 | F♯ | F♯1 (30) |

| Item | Count | Play |
|---|---|---|
| `bs-mute` Stopping the ring | 1 2 3 4 1 2 3 4 | A A A A – – – – |
| `bs-roots` Roots on beat 1 | 1 2 3 4 | R · · · |
| `bs-rootfifth` Root and fifth | 1 2 3 4 | R · 5 · |
| `bs-octaves` Root and octave | 1 & 2 & 3 & 4 & | R 8 R 8 R 8 R 8 |
| `bs-walk` Walking four | 1 2 3 4 | R 3 5 ↗ |
| `bs-kicklock` Locking with the kick | 1 & 2 & 3 & 4 & | R · · · R · · R |
| `bs-gallop` Galloping root | 1 e & a 2 e & a | E · E E E · E E |
| `bs-bossa` Bossa bass | 1 & 2 & 3 & 4 & | R · · R 5 · · 5 |
| `bs-compas` Tangos roots | 1 2 3 4 | – R R R |

`–` is a rest, `·` an empty cell, `↗` the approach note, R root, 5 fifth, 8 octave, 3 third.

Items with no notes: `bs-lock` (play the stage roots with the kick). Sol-fa named in the wording: A, D, E in A = do, fa, so; A C♯ E F♯ = do, mi, so, la; E to A in A minor = mi to la; C, F, G = do, fa, so; C G A F = do, so, la, fa; F♯ to B in B minor = mi to la. X11 checks these against the app's `SOLFA` table.

Invent playback: root = the band's own bass pitch for the chord (E1 to E♭2); fifth = root + 7 semitones; octave = root + 12; approach = one semitone below the next chord's root, or eleven above it when that would fall below the open E string.

## 3. Judgement calls (please check these, Justin)

1. **Boogie walk rhythm.** The framework gave six notes (root, third, fifth, sixth, fifth, third), which does not fill a bar of four. The stage-2 part is now one note a beat, root-third-fifth-sixth, the same every bar, with the D and E shapes shown. The rock technique item takes it up to the octave and back (root, third, fifth, sixth, octave, sixth, fifth, third): two bars in crotchets, one bar in swung quavers.
2. **Shared theory cards for drums, keys and vocals.** The spec asks for guitar wording to come out for non-guitar instruments, and also for those three to be exactly as 0.9 until their batch. I kept them exactly as 0.9; they pick up the `shared` wording automatically when their block is added.
3. **Locking with the kick.** The framework put the push on the and of 3. The app's kick plays on 1 and 3, so the item is root on 1 and 3 with the kick, then a short root on the and of 4 to push into the next bar.
4. **Bossa bass.** Written as root on 1 and the and of 2, fifth on 3 and the and of 4 (dotted crotchet, quaver: "tum-ti, tum-ti"), starting with 1 and 3 alone. The fifth is above the root (D string, fret 2), to agree with `bassPos`; many players take it below (open E).
5. **Walking four example.** C, E, G, G♯ landing on A (C to A minor), all on the A and D strings.
6. **Gallop.** Named "Galloping root" with no palm-muting wording; rhythm said as "ti-tika".
7. **Two names shared with guitar.** "Pulse on one string" and "The spider (1-2-3-4)". The ids are different (`bs-pulse`, `bs-spider`), so no tick carries over.
8. **Also try.** On bass, the stage 5 Riptide line drops "from your Guitar Book; capo 1" (via `alsoOf`). Not named in the batch list, but it is in the framework's scope.
9. **Rolled loop on instrument switch.** Moving to or from bass clears a rolled Invent loop, so a guitar prompt never shows on bass or the other way round. Guitar to drums, keys or vocals is as before.
10. **String mnemonic.** "Eddie Ate Dynamite, Good." (the first four words of the guitar one). Easy to swap.
11. **Header.** "version 0.10 · a Shmungfroi instrument"; I did not add "· bass".
12. **Rhythm syllables.** ta, ti-ti, ti-ti-ti, ti-tika and tum-ti appear; no method or program is named.

## 4. Gaps and things not done

- The Path's metronome note for bass still says "The letters are the guitar's strum…" and the capo lines speak about the guitar. Both are 0.9 text outside this batch.
- The Warm-up tab has no new line pointing to the bass Rudiments (framework 2.1; not in the spec's batch list).
- Beat grids and TAB are plain text blocks. A screen reader gets a spoken description of each beat grid (`aria-label`), but the TAB blocks have none, the same as guitar's.
- Invent's bar is one bar for all four chords, with no rest symbol (a note rings until the next one or the bar line), and it is kept only until the stage or instrument changes, like guitar's loop.
- The bass Invent swing follows the stage (long-short quavers on stage 2). With a Finish feel on, the cells follow that feel's grid.
- Not checked on a real Chromebook or phone; `index.html` grew from 126 KB to 149 KB.
- Musical accuracy has had only this self-check and the X11 data tests. The Opus theory check and Justin's review are still to come.
