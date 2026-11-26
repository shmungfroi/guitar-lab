# Spec for build 0.6 — register 0.5, approved as recommended

Approved by Justin, 26 Nov 2026: "Approve as recommended".
Source: project doc claude/guitar/GTR_Visual_Direction_Framework_26Nov.md §12.

Fix every item below exactly as "Recommended". No new features, no visual redesign beyond what an item needs.

## Standing rules
- Brand: Poiret One + Outfit (local fonts/), Garden black #0b0906, ivory #ece2c8, gold #c9a24a / #f0d48a. Function colours reserved for harmony: tonic #8fbf6a, predominant #c9a24a, dominant #c8473b, secondary #a493d8. Do not use function colours for anything else.
- Act as an expert guitarist, bassist, drummer, keys player, vocal coach and teacher. Use the keys and voicings players actually use.
- Copyright: popular songs are chord maps + recording link only. No lyrics. No transcribed melodies.
- Student-facing text: plain, Australian spelling, must not read as AI-generated.
- Keep it one self-contained index.html (fonts in fonts/).

## Must
| ID | Finding | Fix |
|---|---|---|
| M1 | Gig rotation fills every role and scrambles players, even in phase 1 (one student on guitar ends up on all five instruments). | Rotate only among the roles that have a player filled in. Phase 1 = roles exactly as entered. |
| M2 | Keys: lit white keys barely differ from unlit. | Strong fill on lit keys (white and black) + the note name printed on each lit key. Readable in light and dark. |
| M3 | Capo moves the band's bass and keys audio, but the bass and keys part panels still show un-capoed notes. | Transpose the bass and keys panels (note names, positions, keyboard highlights) by the capo, matching the sounding key the band plays. Spell notes correctly for the sounding key. |
| M4 | Drum grid clipped on phones (beats 3 and 4 cut off at 390px). | Scroll wrapper (overflow-x:auto) and/or smaller cells so the whole bar is reachable at 360–390px. |
| M5 | Gig band name and role inputs lose focus on every keystroke. | Re-render only the run sheet (or update in place), never the input fields being typed in. |

## Should
| ID | Finding | Fix |
|---|---|---|
| S1 | Drum grid doesn't match band hats (4-down stage shows eight hats, band plays four; Finish feel differs). | Build the drum grid from the band's actual drum pattern for the current stage and feel. |
| S2 | Double tap on Play can start two bands. | Run token: each start invalidates the previous run; second tap can't stack. |
| S3 | Gig state not validated on load. | Validate/sanitise saved gig state (unknown song ids, >4 songs, bad roles, bad timers) and fall back to defaults. |
| S4 | Backstory card unreachable for unchosen songs. | "View" button on every song that opens its backstory. |
| S5 | Stage 2 link calls Johnny B. Goode "a 12-bar in A" (recording is in B♭). | Use Rock Around the Clock (in A) as the stage-2 example link instead. |
| S6 | Vocals step wording wrong; no roots line on vocal cue sheet. | Fix wording for vocals; add a sol-fa roots line (do/so/la/fa etc. per chord, correct for capo/sounding key). |
| S7 | Bass wording assumes 4/4. | Metre-aware wording (3/4, 6/8 handled). |
| S8 | Changes log, rudiment unlocks and sign-off count not separated per instrument. | Store and display them per instrument. Migrate existing saved data to guitar. |
| S9 | Gig band obeys Path mutes. | Gig playback always plays the full band. |
| S10 | Gig timer may end silently. | Unlock/start audio on the timer tap so the end beep sounds. |
| S11 | Present mode only enlarges the timer. | Present mode hides setup, scales run sheet and chart for projection. |
| S12 | Metronome uses the Path pattern on the Gig tab. | On Gig tab, metronome uses the current gig song's pattern and tempo. |
| S13 | Keys button label hides the spelling. | Label shows the chord spelling (e.g. "A — A C♯ E"). |
| S14 | Finish feel that can't apply isn't announced; feel changes mid-play. | Announce when the band can't follow the Finish feel (different beats per bar); changing feel stops playback. |
| S15 | Pickup notes uncertain for Let It Be, Hallelujah, Hotel California. | Replace with "Listen for the entry" (no specific pickup claim). |

## Could
C1 dead CSS removed · C2 inversion and maj7 notes on keys · C3 open D option for bass · C4 duplicate "our own arrangement" removed · C5 practice-tempo note; La Bamba bar 2 reads E D (not other) · C6 block timer, and a hint when fewer than 4 gig songs are chosen · C7 drum, run-sheet and role labels clarified · C8 guitar-only wording on shared pages made instrument-neutral · C9 Record per instrument, journal tags, a part panel on the gig song.

## Tests (recreate; none survived the last session)
- tests/test_chords.py — 18 shapes, fretboards, key spellings, bass root/fifth positions, map chords (extract data from index.html and assert).
- tests/test_ui.py — Playwright: 8 stages × 7 tabs × 5 instruments, widths 360/768/1280, light and dark, no console errors, no horizontal page overflow; gates, sign-off, grading, playback, capo, mute, gig max-four, timer, roles. Plus one test per register item above.
- A timed playback check (scheduled notes land within tolerance).
