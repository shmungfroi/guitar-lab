# Test baseline, spec 0.6

Run 26 Nov 2026, headless Chromium (Playwright 1.63), pytest 9.1. Commands are in `tests/README.md`.

Two builds were tested, because the fix commits landed while the suites were being written:

- **0.5 baseline**: `index.html` at `9d8301a` (spec 0.6 commit, page unchanged from `d6a68c6`), run with `SHREDDER_INDEX`.
- **0.6 build**: `index.html` at `0f53755` ("0.6 build report"; Musts `08567c0`, Shoulds `ea95358`, Coulds `7179de9`).

## Counts

| Suite | 0.5 (`9d8301a`) | 0.6 (`0f53755`) |
|---|---|---|
| test_chords.py | 161 passed, 0 failed | 161 passed, 0 failed |
| test_ui.py | 44 passed, 36 failed | 80 passed, 0 failed |
| test_timing.py | 5 passed, 1 failed | 6 passed, 0 failed |
| **Total** | **210 passed, 37 failed** | **247 passed, 0 failed** |

test_ui.py breaks down as 30 matrix cases (each one covers 8 stages x 7 tabs at one width, scheme and instrument), 9 functional tests and 41 register cases.

## 0.5: which failures are expected

Every 0.5 failure is a register item the spec says to fix. None of them is a separate baseline problem.

| Item | Failing on 0.5 | Why |
|---|---|---|
| M1 | test_M1 | With one student on guitar, the run sheet puts Ann on all five instruments |
| M2 | test_M2 [light], [dark] | Lit keys have no note names. The lit fill #f0d48a is about 1.1:1 against unlit #ece2c8 |
| M3 | bass ×3, keys ×3, every_capo | With a capo the panels still show A/E (or C/G/F) roots and spellings |
| M4 | test_M4_drum_grid_has_headroom | No scroll wrapper. At 320 px the grid runs to 319 px, past its 304 px column |
| M5 | test_M5 | Tab out of the band name re-renders the form and focus drops to the body |
| S1 | a-e (4 hats), twelve-bar + flamenco feel (4 hats) | The grid always draws 8 hats in 4/4 |
| S2 | test_ui S2, test_timing S2 | A double tap schedules 12 count-in clicks (two bands) |
| S3 | test_S3 | Unknown song id crashes the Gig tab (`Cannot read properties of undefined (reading 't')`) |
| S4 | test_S4 | No View buttons |
| S5 | test_S5 | "Hear a 12-bar in A: Johnny B. Goode" |
| S6 | ×4 | No sol-fa roots line on the cue sheet |
| S7 | c-g-f (3/4), six-eight (6/8) | "then on beats 1 and 3" |
| S8 | test_S8 | Bass shows the guitar's changes and sign-off count |
| S9 | test_S9 | Path mutes silence the gig band |
| S10 | test_S10 | Timer tap creates no AudioContext |
| S11 | test_S11 | Setup still shown. Run sheet stays at 14 px |
| S12 | test_S12 | Gig metronome reads "Four downs" at 70 (expected the boogie shuffle at 120) |
| S13 | test_S13 | aria-label is "Play A" |
| S14 | announce, stop ×2 | No message when flamenco can't apply in 3/4. Feel or Finish changes leave the band playing |
| S15 | ×3 | Cue sheet says "Come in after the count-in" |

On 0.5 these register cases already pass. They are controls or can't be reproduced headless:

- **M4 at 360 and 390 px.** Chromium lays the grid out at about 307 px, which fits. The headroom test above covers M4 instead.
- **S1 twelve-bar (8 hats) and six-eight (6 hats).** Already correct.
- **S7 four-chords (4/4).** Control case: "1 and 3" is right in 4/4.

Matrix and functional tests: everything passes on 0.5. There are no console errors in any of the 1,680 stage/tab/instrument/width/scheme combinations, and no page-level overflow.

## 0.6

All 247 pass. The fixes for M1–M5 and S1–S15 behave as the spec describes, as far as these tests can see.

## Musical observations not in the spec (for review)

1. **Greensleeves verse, bar 3 (stage 6).** The map reads `Am G F E Am G "Am E" Am`. The traditional harmonisation is passamezzo antico, `Am G Am E | Am G Am-E Am`. The melody in that bar has a G♯ leading note (A G♯ A), and G♯ clashes with an F chord. The refrain (`C G Am E C G "Am E" Am`, the romanesca) is right. Suggest bar 3 = Am. Then the verse shows i–VII–i–V, and the Andalusian Am–G–F–E stays in Technique.
2. **Minor-key VII is coloured as dominant.** G in A minor (stage 6) and A in B minor (stage 8) carry the `D` function, so they use the dominant red. They are also labelled "subtonic", and the KNOW card says the subtonic is gentle and *not* a true dominant. Many teachers would accept VII as a dominant substitute in rock, but the colour contradicts the app's own explanation. Consider predominant, or a neutral colour.
3. **Standing-rule colour.** The spec gives dominant as #c8473b, but `--dom` is #d0574b in dark (and #a8352b in light). This isn't musical, but the standing rules fix that colour.
4. **0.6 capo spelling in B minor, capo 4.** The panel spells E♭ minor with a C♭ major chord (VI). That is correct, since it avoids the double sharps D♯ minor would need for its V (A♯ C𝄪 E♯). Students may still read C♭ as a typo, so an on-screen note ("C♭ is the same key as B") might help.

Everything else checked out: all 18 shapes, fingerings and barres; the triad inversions on G-B-E; the C scale; key and roman-numeral spellings; the secondary dominant E7 = V7/vi resolving to Am; the Andalusian cadence as i–VII–VI–V (Phrygian iv–III–II–I); the 12-bar form; the I–V–vi–IV labelling; the bossa, flamenco compás and swing patterns; the boogie riff (root–fifth and root–sixth); and capo keys (A +1 = B♭, +2 = B, C +3 = E♭, and flat-side minors).
