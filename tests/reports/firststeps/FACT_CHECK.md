# The Guitar Lab 0.11 "First Steps": music and guitar fact check

Independent check, 28 Nov 2026, of branch `firststeps` (builder's last commit `c56cc9a`). I did not build First Steps. I checked every taught statement in `index.html` (FSTEPS, FPART, FSV steps 1 to 7, the question builders `qPart`, `qStr`, `qDia`, `qTab`, the ear check `EARG`, the lesson data `FS_TAB`, `FS_EFG`, `QT`, and the chord data `CH`) against standard guitar teaching practice and the relayed terms from Justin's "Rockin' the Guitar" booklet. I used the builder's fact list as a checklist only; each item was worked out again from the code.

Result: **one text fix**, no data fixes, two flags for Justin. Tests: `tests/test_firststeps.py` 59 passed (51 before plus 8 new `test_FS_facts_*`).

## 1. Parts, posture, pick grip, fretting, finger numbers, picking signs

| Item | Result |
|---|---|
| 14 part names match the booklet: headstock (head), machine heads (tuning pegs), nut, neck, fingerboard (fretboard), frets, position markers, body, sound hole, pickguard, saddle, bridge, strings, pickups | PASS |
| Each part's description (headstock, machine heads tighten or loosen one string, nut grooves, fingerboard, frets "press just behind one", body hollow on an acoustic, sound hole, pickguard protects from the pick, saddle set into the bridge, bridge holds the strings, strings over the nut to the bridge, pickup like a microphone with a magnet sensing steel strings) | PASS |
| Position markers | **FIXED.** Before: "On most guitars they sit at frets 3, 5, 7 and 9, with two dots at fret 12." After: "... with two dots at fret 12. Above fret 12 the pattern starts again." The old line implied there were no markers above 12; the app's own drawing shows them at 15 and 17 (acoustic) and 15 to 21 (electric) |
| Fretting hand left, strumming hand right (right-handers); left-hander card | PASS |
| Sitting: front of chair, back tall, waist on the right leg, neck slightly up never down | PASS (standard casual/classroom position) |
| Pick: between pad of thumb and side of first finger, tip showing, strum from the wrist | PASS |
| Fretting: fingertips just behind the fret wire, thumb behind the neck pointing up, arched fingers, short nails | PASS |
| Finger numbers T 1 2 3 4 = thumb, index, middle, ring, little; hand sketch labels T on the left for a left hand palm towards you | PASS |
| Picking signs: square arch (⊓) = downstroke towards the floor, V = upstroke; down on the beat, up on the "&" | PASS (sketch draws an open-bottom arch and a V correctly) |

## 2. String names, numbers, orientation, one finger per fret

| Item | Result |
|---|---|
| String 6 thickest, lowest, low E; string 1 thinnest, highest, high E, closest to the floor when held | PASS |
| Order 6 to 1 E A D G B E; `SNAME`, `SLET`, `sOpen` and the quiz option labels | PASS |
| String quiz answer keys (lit string, number to name, name to number) and the "count from string 6" hint | PASS |
| One finger per fret at frets 1 to 3 | PASS |
| Flat-on-the-lap figure with string 6 at the bottom, string 1 at the top, matching TAB | PASS |

## 3. Reference tones and ear check

| Item | Result |
|---|---|
| Reference tones as played: one triangle oscillator per tap, start frequency read from the WebAudio oscillator in Chromium: 6 = 82.41, 5 = 110.00, 4 = 146.83, 3 = 196.00, 2 = 246.94, 1 = 329.63 Hz (MIDI 40 45 50 55 59 64) | PASS (measured, `test_FS_facts_open_string_pitches_and_reference_tones` and the builder's F6) |
| Ear pairs: E2/E4 (24 semitones), A2/B3 (14, an octave and a tone), D3/G3 (5, a perfect fourth), G3/G♯3 (1); all gaps at least a semitone | PASS |
| Answer key: "Higher" is right exactly when the second note is higher; order within a pair random | PASS |
| "Guitar music is written an octave higher than it sounds, so that it fits on the treble clef" | PASS |
| Class rule: teacher tunes the class guitars, leave the machine heads alone; tuning only in the "Your own guitar at home" box; tune up to the note from below | PASS |

## 4. Chord diagrams

| Item | Result |
|---|---|
| Diagram conventions: neck standing up, head at top, string 6 on the left, thick top line = nut, dot number = finger, T = thumb, o = open, × = not played | PASS |
| A box `x02220`, fingers `001230`: × on 6, open 5 and 1, fingers 1 2 3 at fret 2 on strings 4 3 2; lesson text matches | PASS |
| D check `xx0232`, fingers `000132`: finger 1 on G (fret 2), 3 on B (fret 3), 2 on high E (fret 2); D open; 6 and 5 not played. Answer keys for finger, fret, open and not-played questions all match | PASS |
| Make-up chords Am `x02210`/`002310` and C `x32010`/`032010`: standard fingerings; keys match | PASS |
| Fret hint "count the spaces down from the nut; the first space is fret 1" | PASS |

## 5. TAB

| Item | Result |
|---|---|
| Orientation stated in step 6 text, step 6 caption, the TAB quiz hint and the old Path "Reading TAB" card: top line string 1 (high E), bottom string 6 | PASS everywhere. `mkTab` prints e B G D A E top to bottom |
| Numbers = frets, 0 = open, counted from the nut (0) towards the bridge, left to right, stacked = chord, no rhythm shown | PASS |
| Lesson TAB: string 6 fret 3 = G (G2), string 2 fret 1 = C (middle C), string 3 open = G (G3), then Em stacked `022000`; play-back pitches 43, 60, 55, then 40 47 52 55 59 64 | PASS |
| Check lines and their "That note is ..." names: (5/2 B, 3/0 G, 1/3 G); (6/0 E, 4/2 E, 2/3 D); (1/1 F, 5/3 C, 3/2 A) | PASS |
| Distractors: the mirrored string (7 − n) tests the orientation; the wrong fret is open/2 | PASS |

## 6. Step 7

| Item | Result |
|---|---|
| Em: finger 2 on string 5 (A) fret 2, finger 3 on string 4 (D) fret 2, other four open; same as the app's Em box `022000`/`023000` | PASS |
| E F G on string 1: open, fret 1 (finger 1), fret 3 (finger 3); pitches E4 F4 G4 (64 65 67) | PASS |
| "mi, fa and so in C major" (E, F, G are degrees 3, 4, 5 of C) | PASS |
| Count-in "1, 2, then 1 2 3 4": `playSeq` clicks beats 1 and 3, then four beats, in 4/4 | PASS |

## 7. Placement quiz

| Item | Result |
|---|---|
| Eight questions built by the same `qPart`, `qStr`, `qDia('D',…)` and `qTab` builders, so the keys are the ones checked above | PASS |

## 8. Existing stage 1 Path cards (`KNOW`, left unchanged)

| Card | Disagreement with First Steps | Result |
|---|---|---|
| "The six strings" | Uses "Eddie Ate Dynamite, Good Bye Eddie". First Steps asks students to make their own line and offers "Emus And Dingoes Go Bush Early". Both are correct (E A D G B E); they just differ | FLAG for Justin: pick one, or have the card point to the student's own line |
| "Parts of the guitar" | Says "tuners" where First Steps (and the booklet) say "machine heads (tuning pegs)"; says "fretboard" where First Steps says "fingerboard (fretboard)"; spells "soundhole" where First Steps says "sound hole"; does not name position markers or the pickguard | FLAG for Justin: align the card to the booklet terms |
| "Reading TAB" | Agrees on orientation. Says rhythm comes from "the strum grid"; First Steps says "by listening, or from the staff printed above". Different sources, not a contradiction | Note only |
| "Reading a chord box" | Agrees (thick E on the left, finger numbers, o and ×) | PASS |

## 9. Memory line "Emus And Dingoes Go Bush Early"

| Item | Result |
|---|---|
| Initials E A D G B E | PASS |
| Published already? Two web searches (exact phrase, and "Emus and Dingoes" with guitar/EADGBE) found no match. Common published lines are ones like "Eddie Ate Dynamite, Good Bye Eddie" | Not found; fine to use |

## 10. Spelling and terms

| Item | Result |
|---|---|
| British/Australian spelling in all First Steps text (no -ize, center, color in taught text); quavers/bars terms; "fingerboard (fretboard)", "machine heads (tuning pegs)" | PASS |

## Tests added

`tests/test_firststeps.py`, 8 data tests that read the app's own tables and question builders through `appdata`'s hook and compare them with an answer key written in the test:

- `test_FS_facts_open_string_pitches_and_reference_tones` (MIDI numbers, and the oscillator frequency each step 4 button actually starts)
- `test_FS_facts_string_order_and_names` (also checks the memory line's initials)
- `test_FS_facts_ear_pairs`
- `test_FS_facts_chord_shapes_are_standard` (A, D, Em, Am, C frets and fingers)
- `test_FS_facts_diagram_answer_keys`
- `test_FS_facts_tab_orientation_answer_keys_and_pitches`
- `test_FS_facts_step_7_em_and_efg`
- `test_FS_facts_parts_and_technique_words`

`python3 -m pytest tests/test_firststeps.py -q -p no:cacheprovider`: 59 passed. The guitar drawing was not touched.
