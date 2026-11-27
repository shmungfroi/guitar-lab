# R13-2 theory check, batch 1 (0.10 bass)

**Checker:** independent music-theory check (Opus 5.5). Not the builder. Every note was worked out again from the tuning E1 A1 D2 G2 (MIDI 28, 33, 38, 43; string 0 = low E), not taken from the builder's table.
**Branch:** `build-r13`. Not merged. Only data and wording in `instData` were changed. No UI, layout or playback code was touched.

## Results by check

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | String/fret gives the named note; spelling fits the key | PASS | All 15 TABs (122 notes) and 22 `pos` rows sound the named note. No flats anywhere. C♯, F♯ and G♯ in A major, G♯ in A minor, F♯ and C♯ in B minor. The spider is a chromatic drill and is spelt in sharps going up, which is right. |
| 2 | Boogie walk A–C♯–E–F♯ and its D and E moves; 12-bar order | PASS | A: A0 A4 D2 D4. D: D0 D4 G2 G4 (D F♯ A B). E: E0 E4 A2 A4 (E G♯ B C♯). Each is R, M3, P5, M6, and the letters step 1-3-5-6. The up-and-back walk is 33 37 40 42 45 42 40 37 (A2 on G string fret 2 is the octave). 12-bar is A A A A D D A A E D A E (I I I I IV IV I I V IV I V, with a V turnaround). |
| 3 | Root–fifth agrees with `bassPos`; octave shapes | PASS | A: A0 then D2. E: E0 then A2. B: A2 then D4. F♯: E2 then A4. All match `bassPos`. Octaves (G E3→D5, A E5→D7, C A3→G5, E E0→D2) are two strings up and two frets along, +12 each time. |
| 4 | Approach notes a semitone from the target, spelt sensibly | PASS (code FLAG) | B→C, F♯→G, G♯→A, E→F are all +1 semitone and spelt on the letter below the target, so each is a diatonic semitone. The Hallelujah card's G♯→Am and B→C are right too. **FLAG (code, out of scope):** in Invent, when the next root is E1 the approach note is played as D♯2 (`nr+11`), a major seventh above, and then falls to E1. That is the right pitch class but not a semitone approach. A semitone from above (F1 = `nr+1`) is what a bassist would play. This needs a one-line change to the playback code, the `how` text and the X10 assertion in `test_r13.py`, so it is left for the main session. |
| 5 | Walking four: C, E, G, G♯ → A | PASS | C2 E2 G2 is a root-position C triad. G♯2 is a chromatic semitone below the A2 it lands on, and G♯ (not A♭) is the right spelling as the leading note of A minor. "do, mi and so" is right whether you hear it in C or la-based in A minor. **FLAG:** the item opens at stage 6 (Greensleeves, 6/8), but it is a 4/4 pattern. |
| 6 | Bossa bass | **FIXED** | See fix 1. The builder's figure repeated each note just before the next strong beat (R on 1 and the and of 2, 5 on 3 and the and of 4). In the standard figure each short note *anticipates the next* pitch: R on 1, 5 on the and of 2, 5 on 3, R on the and of 4 (dotted crotchet, quaver, twice: tum-ti, tum-ti). **Fifth above or below:** both are common. The fifth below is the more idiomatic, because it puts the lower, heavier note on the surdo's accented second beat (beat 3 in 4/4). The fifth above (D string fret 2) stays in the TAB so that it agrees with `bassPos`, the Root-and-fifth item and Invent's `r+7`. The wording now offers the open E string as the usual alternative. **FLAG for Justin's ear:** whether to make the fifth below the default for the bossa item only. |
| 7 | Tangos roots, binary | PASS | 4 cells: rest on 1, root on 2, 3 and 4, accents [1,2,3] matching the Finish. No 12-count. The roots A G F E (Am–G–F–E, the Andalusian cadence *por arriba*) step down. **FLAG:** the item opens at stage 4 (3/4 waltz), where the Flamenco Finish band plays the 12-beat compás. The item itself is right, but a student may hear a mismatch on that stage. |
| 8 | Rhythm grids per metre; rhythm syllables | PASS | 4 cells: roots, root-fifth, walk, tangos (crotchets in 4/4). 8 cells: octaves, kick-lock, bossa (quavers). 8 cells: mute (two bars of crotchets). 8 cells: gallop (two beats of semiquavers, 1 e & a). Invent: 8 cells in 4/4 straight or swung (the shuffle stage is m=4 with `sw`), 6 in 3/4 (1 & 2 & 3 &), 6 in 6/8 (1–6). Syllables: ta = crotchet, ti-ti = quavers, ti-ti-ti = compound quavers, ti-tika = quaver + two semiquavers (matches the gallop grid), tum-ti = dotted crotchet + quaver (matches bossa). **FLAG:** "tum-ti" is Choksy's syllable. Justin may prefer his own (for example ta-i ti). |
| 9 | Sol-fa: do-based major, la-based minor; E7→Am | PASS + 2 FIXED | `SOLFA` table entries checked from first principles (A, Am, C, Am6, Bm, including Bm E = re and G = fa). "mi to la in this minor key, so to do in a major one" is right. Fix 2: `bs-cross` said "low do, high do" for E in key A, which contradicts the stage-1 card (E is so). Fix 3: the Hallelujah card now names G♯ as si rising to la, and B as ti rising to do. |
| 10 | Theory statements in the cards | PASS + 1 FIXED | Checked and correct: "the root alone doesn't say major or minor; the third decides" (C♯/C), "the fifth is the same in major and minor" (true for every chord in the app, none of which is diminished), stage-6 G (subtonic, gentle) vs E (fifth, pulls home), stage-8 B/F♯ shapes and "F♯ is the fifth of B minor: mi to la", the 3/4 and 6/8 cards, "Where the kick lives" (`drumPat` kick on 1 and 3 in 4/4), the C–G–A–F path (down a 4th, up a tone, down a major 3rd). Fix 4: the am-e7 card said playing C "under the band" makes "the chord turn dark". The band already plays A minor, so the bass C points at the dark note rather than changing the chord. |

Also checked: stage-1 strings card (an octave below the guitar's four lowest strings is right), hammer-on E→F♯ and slide F♯→G♯, the mute wording, and the `bassPos` panel's alt line for D (open D, fifth A on G string fret 2).

## Fixes (all in the `instData` block of `index.html`)

1. **`bs-bossa`**
   - Before: `ev` A0 A0 D2 D2, `evn` A A E E, grid `R · · R 5 · · 5`, "each one played again softly just before the next".
   - After: `ev` A0 D2 D2 A0, `evn` A E E A, grid `R · · 5 5 · · R`. New wording: "each one arrives a quaver early: the fifth sounds first on the and of 2 and again on beat 3, then the root comes back on the and of 4, leading into the next bar… Many bossa players take the fifth below the root instead: here, the open E string." `say` updated to match.
2. **`bs-cross`**
   - Before: "sing low do, high do."
   - After: "in the key of A, E is so, so sing low so, high so."
3. **Card, Hallelujah, "Walking into a chord"**
   - Before: "G♯ … into A minor, or B … into C."
   - After: "G♯ … into A minor, si rising to la, or B … into C, ti rising to do."
4. **Card, Am and E7, "Major or minor? The third decides"**
   - Before: "Play C (A string, fret 3) under the band and hear the chord turn dark."
   - After: "Play C (A string, fret 3) under the band's A minor: that is the very note that makes the chord dark."

Two existing X11 assertions changed to match fix 1: the bossa hits are now R [0, 7] and 5 [3, 4], and the root-fifth step is 1.

## Flags for Justin

- Invent approach into E plays D♯2 (a major seventh above) instead of a semitone. Suggest F1 from above. This is a code change, so it is out of this check's scope.
- Bossa: make the fifth below (open E) the default for this item?
- "tum-ti" as the syllable for dotted crotchet + quaver.
- Gate placement: the 4/4 walking four opens on the 6/8 stage, and tangos opens on the 3/4 stage, where the Flamenco Finish plays the 12-count.

## New tests: `test_X11b_*` in `tests/test_chords.py` (25 cases)

These are written from first principles with their own tuning, scale and spelling helpers. They do not use the builder's `pc()` or `bs_events`.

- `scales_helper_is_right`
- `every_string_and_fret_is_the_named_note_spelt_for_the_key` (×15 TABs: pitch class, no flats, every name in the item's key, spider semitones)
- `pos_lists_sound_their_names`
- `boogie_walk_and_the_12_bar` (exact frets/strings per chord, R-M3-P5-M6, letter steps, 12-bar order, up-and-back MIDI)
- `root_fifth_and_octave_shapes` (lowest-root rule versus `bassPos` for all 12 pitch classes, +7, +12)
- `approach_notes_semitone_and_spelling` (+1 semitone, letter below)
- `walking_four_C_to_A_minor`
- `bossa_is_the_standard_root_fifth_figure` (R . . 5 5 . . R, long-short-long-short, anticipating pitches)
- `tangos_is_binary`
- `rhythm_grids_fit_the_metre_and_the_syllables` (even subdivisions, Invent 8/6/6 per metre, syllable/grid agreement)
- `solfa_from_first_principles`

## Pass counts

`python3 -m pytest tests/test_chords.py tests/test_r13.py -q -p no:cacheprovider`: **243 passed, 0 failed**. That is `test_chords.py` 210 (185 + 25 new X11b) and `test_r13.py` 33. The full UI suite was not run, as briefed.
