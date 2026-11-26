# Build report — The Shredder 0.6

Built against `SPEC_06.md`. Only `index.html` was edited. Three commits: Musts `08567c0`, Shoulds `ea95358`, Coulds `7179de9`.

Verification was done with throwaway Python Playwright scripts (headless Chromium, `file://`), not with the test suite in `tests/`, which another agent was writing in parallel and which I have not run. "Checked" below means I ran the behaviour in the browser and read the result.

Smoke check after the last commit: 5 instruments × 8 stages × 7 tabs at 360, 390, 768 and 1280 px — no console errors, no page errors, no horizontal page overflow. Dark and light schemes loaded without errors.

## Note on commit grouping

The bass, drums, keys and vocals panels share one function (`partPanel`). I rewrote it once, in its final form, in the Musts commit. So S1, S13, S15, C2, C3 and the cue-sheet half of S6 are physically in the Musts commit, not the commit their group name suggests.

## Must

| ID | Status | What changed | How verified |
|---|---|---|---|
| M1 | Done | `runSheet`: builds the list of roles that have a name and rotates only among those. Phase 1 is as entered. | One student on guitar stays on guitar in all four phases. Three players (guitar, drums, vocals) cycle through those three roles only; phase 1 as typed. Rotation off: same roles every phase. |
| M2 | Done | `kbd`: lit white keys dark gold `#7a5c12` with ivory note name; lit black keys light gold `#f0d48a` with dark note name. Unlit keys unchanged (ivory / black). Root marked with a dot. Keys carry class `k-on` / `k-off`. | Screenshots in dark and light: lit keys and names read clearly in both. Keyboard colours are fixed, so they do not change with theme. |
| M3 | Done | New `pcN`, `trN`, `keyAt`, `spellAt`, `nameAt`, `capoOf`; `sounds` now uses them. `partPanel(s,cp)` transposes chord names, note spellings, bass positions and keyboard highlights. `bassPos` now takes a pitch class. | Printed every capo 0–7 for stages 1, 3, 6, 7, 8 on bass, keys and vocals. A shapes: capo 1 = B♭ (B♭ D F), capo 2 = B (B D♯ F♯), capo 4 = D♭. See judgment calls below. |
| M4 | Done | `.dgw` wrapper with `overflow-x:auto`; smaller cells under 480 px. | At 360 and 390 px the widest grid (8 columns) ends at 285 px inside a 344/374 px wrapper. I did not reproduce the original clipping before fixing it, so I can only confirm the after state. |
| M5 | Done | New `gigRunH` / `renderRun`: typing updates state and re-renders only `#gigRun`. `input` and `change` handlers no longer call `renderGig`. | Typed "Mia Wong" into a role field and a band name key by key: focus stayed in the field and the run sheet updated live. |

## Should

| ID | Status | What changed | How verified |
|---|---|---|---|
| S1 | Done | New `drumPat(p)`; `playSeq` plays from it and `drumGrid` draws from it, both using `bandPat(s)`. | Four-downs stage shows four hats. Grid changes with Finish feel (e.g. Flamenco on 4/4 = four hats, Rock = eight). |
| S2 | Done | `runId` token: `stopAll` and each `playSeq` bump it; a run that finds a newer id after `await resume()` returns; `tick` checks it too. | With `resume()` slowed to 300 ms and two taps 100 ms apart: one count-in only (6 clicks, 6 distinct times). |
| S3 | Done | `gigS` rewritten as the validator; also called once at load. | Injected unknown ids, duplicates, 7 songs, non-object bands, unknown role, non-string names, `block:"abc"`, `rotate:"yes"`, bad `open`, `bpm:9999`, and `gig:"junk"`. All came back clean or default. |
| S4 | Done | "View" button (`data-gopen`, `data-gview`) on all six songs; opens the song card and scrolls to it. | View on an unchosen song (Hound Dog) opened its backstory and chart. |
| S5 | Done | Stage 2 `q`/`ql` now Rock Around the Clock. Johnny B. Goode moved to "Also try", described as recorded in B♭. | Read the two links from the page. |
| S6 | Done | `PSTEPS` vocals wording (hum/sing, whole band left on). Cue sheet has a "Roots in sol-fa" line plus a bar-by-bar sol-fa line per section. | Read the steps and cue sheet; roots line checked at every capo. |
| S7 | Done | `PSTEPS` bass step and `bassHow` are metre-aware (4/4, 3/4, 6/8). | Read the text on Amazing Grace (3/4) and Greensleeves (6/8). |
| S8 | Done | Changes entries carry `inst`; rudiment, technique and best-tempo keys get `@instrument` via `ik`; sign-off count filtered by `mineKey`. Load migration tags old changes and journal entries as guitar; old un-suffixed keys are guitar's by design. | Seeded 0.5-style data: guitar shows it, bass shows none. Sign-off count 1 on guitar, 2 on bass from mixed keys. |
| S9 | Done | `playSeq`: gig routes every part straight to the master output. | With guitar and bass muted on Path: 48 connections into a muted bus on Path, 0 on Gig. |
| S10 | Done | Timer tap calls `A()`, resumes, and plays a soft tick; the end beep resumes first if needed. | Oscillator started on the tap. I did not wait out a full timer to hear the end beep. |
| S11 | Done | CSS under `.present`: hides `.gsetup`, header buttons row and footer; single column; run sheet and song title enlarged; wrap goes full width. Leaving the Gig tab drops present mode. | Setup hidden, run sheet visible, table text 14 px → 30.7 px at 1280. No overflow at 1280 or 390. Screenshot looked right. |
| S12 | Done | `curPat` uses the open gig song on the Gig tab. New `bpm()` / `setBpm()`: the Gig tab has its own tempo (`gig.bpm`), set to the song's target when a song is opened. | Gig showed 120 / Boogie shuffle; La Bamba 140 / Straight eighths; Path still 70 / Four downs afterwards. |
| S13 | Done | Keys label reads e.g. "A — A C♯ E" (class `kname`). | Read from the page at several capos. |
| S14 | Done | New `feelMiss`. Toast plus a standing note on the chart and metronome card. Changing feel (or changing Finish while the feel is on) stops playback with a message. | Flamenco on 3/4 and 6/8 announced; others not. Feel change during playback reset the Play button. |
| S15 | Done | Songs without a certain pickup that are not public domain show "Listen for the entry: the recording shows where the voice comes in." | Let It Be, Hallelujah, Hotel California show it; Skip to My Lou still says "Come in after the count-in." |

## Could

| ID | Status | What changed |
|---|---|---|
| C1 | Done | Removed `button.x-unused`. A scripted scan of class selectors found no other unused ones; the scan is weak on one- and two-letter class names. |
| C2 | Done | Each keys card says the order as drawn and its inversion (`invName`); maj7 chords add that the right hand can leave the root to the left. |
| C3 | Done | When the sounding root is D the bass card adds the open D string option. |
| C4 | Done | Removed the second "our own arrangement" from the gig song meta line. |
| C5 | Done | La Bamba map is `A D / E D / A D / E D`. Practice-tempo note under the gig chart (`#gigTempoNote`). |
| C6 | Done | "Whole block: N min" timer button (`#gblock`), follows the block length. Hint under the song list when fewer than four are chosen (`#gigHint`). |
| C7 | Done | Drum rows "Hi-hat (closed)", "Snare", "Rim click", "Kick" with a "Count" row and a legend. Run sheet has column headings and a line per phase saying whether roles moved. Role fields labelled Guitarist, Bassist, Drummer, Keys player, Singer. |
| C8 | Partial | Warm-up is now per instrument (`WARMS`, `REFN`), plus neutral wording on the metronome card, capo row, five-steps heading and journal placeholders. Rudiments and Technique are still guitar content: for other instruments they now say so, rather than being rewritten. |
| C9 | Done | Record headings name the instrument; journal entries are tagged with instrument (and "Invent" for saved loops); the gig song card has an instrument chooser and part panel (`#gigPart`). |

## Judgment calls

**Sol-fa convention.** Movable do with la-based minor, because the app already used it (`SOLFA` table: Am = la, E7 = mi). Syllables do not change with capo; the note names beside them do. Minor songs say "Home note (la)".

**Key spelling under capo.** Notes move by letter as well as semitone, so spellings follow the sounding key. The key name comes from the app's existing table (D♭, E♭, F♯, A♭, B♭ major; C♯, E♭, F♯, G♯, B♭ minor). One exception: if that name forces a double sharp or flat in any chord of the stage, the enharmonic name is used. In practice this only affects Hallelujah at capo 6, which reads G♭ major instead of F♯ major (E7 would otherwise be A♯ C𝄪 E♯ G♯). Stages 4 and 5 at capo 6 stay F♯ major. Correct but unfamiliar spellings do appear, e.g. B♯ in G♯7 at capo 4, C♭ in E♭ minor.

**Bass positions.** Four-string EADG. Roots E to A♭ on the E string (frets 0–4), A to E♭ on the A string (frets 0–6), fifth one string up, two frets higher. This matches 0.5 for every un-capoed chord. I also changed the band's bass audio to wrap into the same octave so sound and panel agree; without a capo it is identical to 0.5.

**Open D bass option (C3).** Shown as an alternative line, not the default: "Or play the open D string, with the fifth on the G string, fret 2." The default stays A string fret 5.

**S1 drum mapping.** The grid shows exactly what the synthesised band plays, not an idealised kit part: hi-hat on every cell of the strum pattern, kick on 1 (and 3 in 4/4), snare on 2 and 4 (or count 4 in 6/8), rim click on 2 and 3 in 3/4. So a swung shuffle shows eight hats with a "swing the quavers" note.

**S12 pattern.** On the Gig tab the metronome uses what the gig band plays, which is the song's own pattern unless the Finish feel toggle was left on from the Path. Gig tempo is separate from Path tempo.

**S3 empty set.** An empty song list is treated as valid (the user unticked everything). Only a list whose entries are all invalid falls back to the default four.

**Chart under capo.** The road map still shows the guitar's shape names. Bass and keys panels show sounding names with "Chart shows A" under each, plus a one-line capo note. Transposing the chart itself was outside M3.

## Gaps and things to know

- C8 is partial, as above: no bass, drum, keys or vocal rudiments were written (the spec rules out new features).
- Dominant colour: the spec's standing rules give `#c8473b`; the app's dark value is `#d0574b` and was already so in 0.5. I left it alone and flag it here.
- M2 lit-key colours are fixed golds, not the chord's function colour. The chord name above each keyboard carries the function colour.
- M4: fixed state confirmed, original fault not reproduced.
- S10: end-of-timer beep path not listened to in real time.
- Warm-up ticks are still shared across instruments (labelled "all instruments" on the Record page); the spec's S8 list did not include them.
- Label changes a test might trip on: bass card and keys label formats, drum row names, run sheet now has a header row in each table, role field labels, an extra `[data-inst]` button group on the Gig tab, `[data-gopen]` now also on the six View buttons.
- Not tested: real phones, Safari, screen readers.
