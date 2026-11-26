# The Guitar Lab R13: approved spec (per-instrument content)

Approved by Justin, 27 Nov 2026: "r13 approved as recommended".
Framework (with the inventory, content tables, architecture and tests): `tests/reports/r13/R13_Framework.md`. Where this spec and the framework differ, this spec wins.
Baseline: `main` 90719f9 (0.9), full suites 383/383.

## Decisions (as recommended)
1. **Depth:** full size per instrument (about 8 Rudiments, about 10 Technique, Invent, cards for all 8 stages), shipped one instrument at a time.
2. **Gates:** the same stage gates as guitar (`st` = stage index), per instrument (passing a stage on bass opens nothing for drums).
3. **Drums:** grids and words only; no stave notation now (later via the Composition Lab).
4. **Vocals:** sol-fa first with note names beneath; hand signs described in words (drawings later in the design pass).
5. **Shared:** Warm-up, Function card, one-minute changes, and the theory `KNOW` cards (`func`, `four`, `six`, `vii`, `sec`, `e7`) stay shared, with guitar-only wording removed for non-guitar instruments. Guitar wording stays word for word.
6. **Keys:** sustain pedal only as an optional step; parts written in each stage's key and following the capo (sounding names), as the keys panel already does.
7. **Finish groups:** each non-guitar instrument sees core + rock + the current Finish's group only. (Guitar unchanged.)
8. **Vocal Finishes:** no rock-edge or metal technique taught; those groups are a single "ask your teacher" card.
9. **Bass flamenco:** keep, roots only, marked optional. Tangos is binary (beat 1 light, weight on 2, 3, 4), never the 12-count.
10. **Voice safety:** a short Stage 4 changing-voices note on the vocal Rudiments/Technique pages, with "sing in your own octave" as the default.
11. **Stray guitar ticks** (e.g. `r:cross@drums` from the old shared list): hidden quietly; never shown as progress on the new items; never deleted.
12. **Wording to avoid:** none named. Standing rules apply: our own words, no method-book text, no method-program names, no lyrics.
13. **Order and review:** bass, drums, vocals, keys; Justin reviews each for musical accuracy before it ships to students.

## This batch: R13-1 + R13-2 + R13-3 (plumbing, theory checks, bass)
- **Plumbing (framework §4):** per-instrument content block (JSON `<script type="application/json" id="instData">`), accessors (`rudOf`, `techOf`, `knowOf`, `part2Of`, `inventOf`), `itemCard` generalised not forked, Record reads the instrument's lists, Finish-group filter (decision 7), stray-key hiding (decision 11). Instruments without content yet (drums, vocals, keys) keep exactly today's behaviour until their batch ships.
- **Bass content (framework §2.2, with the main-session corrections):** Rudiments, Technique (core, rock, metal, bossa, flamenco-optional), Invent "build one bar of bass", knowledge cards for all 8 stages, stage-2 four-line boogie-walk TAB.
- **Theory checks (Opus):** verify every bass note, fret and string; boogie walk A–C♯–E–F♯ and its D and E moves; approach notes a semitone from the target root; root-fifth positions agree with `bassPos`; bossa bass pattern is a standard one (root on 1, fifth on 3 with the usual anticipation) and is written so; tangos roots binary. Data tests in `tests/test_chords.py`.

## Hard constraints
- Guitar is unchanged: a snapshot test of guitar's Rudiments, Technique, Invent and all 8 stage side panels must match 0.9 byte for byte (except the version label).
- localStorage key `shredder` and the save shape unchanged; new items use prefixed ids (`bs-…`); old saves and 0.7/0.8/0.9 backups import.
- No `alert`/`confirm`/`prompt`; one `index.html` + `fonts/`; no network or libraries.
- Brand and look unchanged; nothing generic or AI-looking. British/Australian terms. No student names, no lyrics, no copied method text.
- Version label 0.10 ("0.10 · bass" is fine in the header note) for this batch.

## Tests (framework §5, ids X1–X13; this batch covers guitar and bass)
X1 guitar snapshot · X2 bass sees only bass items · X3 guitar-token denylist on bass (allow "fret", "string", "TAB") · X4 bass cards on all 8 stages, no guitar-only cards · X5 stage-2 note: guitar six-line TAB, bass four-line TAB · X6 save key/shape · X7 old saves with stray keys don't mark bass items done · X8 bass gates per instrument · X9 instrument switch changes the tabs · X10 bass Invent save · X11 bass theory data · X12 content policy · X13 render matrix still clean. Drums, vocals, keys: assert unchanged from 0.9 for now.
