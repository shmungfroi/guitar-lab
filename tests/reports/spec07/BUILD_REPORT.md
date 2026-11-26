# Build report: The Guitar Lab 0.7 (self-check)

This is the builder's own check against `SPEC_07.md`, item by item. It is not an independent check.

Branch `build-0.7`, not merged to `main`. Three tier commits on top of the spec commit `428b9c2`:

| Tier | Commit | Items |
|---|---|---|
| Must | `7a4933d` | R1, version label |
| Should | `86d29b2` | R2, R3, R4, R5, R6, R7, R12 |
| Could | `fd059ea` | R8, R9, R10, R11, READMEs |

Files changed: `index.html`, `tests/test_ui.py`, `tests/test_chords.py`, `tests/README.md`, `README.md`. Nothing else.

## Test results

Full run at `fd059ea` (`python3 -m pytest tests -q -p no:cacheprovider`), three times in a row:

| Run | Result | Time |
|---|---|---|
| 1 | 311 passed, 0 failed | 3 min 36 s |
| 2 | 311 passed, 0 failed | 3 min 34 s |
| 3 | 311 passed, 0 failed | 3 min 19 s |

| Suite | Tests | Passed |
|---|---|---|
| `test_chords.py` | 163 | 163 |
| `test_ui.py` | 142 | 142 |
| `test_timing.py` | 6 | 6 |
| Total | 311 | 311 |

Baseline before the build was 247 passed (one full run at the spec commit, before any edit). 63 of the 311 are new `test_R<n>_...` cases; one more is `test_version_label_is_0_7`.

Earlier tiers, stated exactly:
- `7a4933d` (Must): one full run gave 269 passed, 1 failed. The failure was my own test asserting the R2 default (`gig.useFin`) a tier early. I removed that assertion from the Must commit (it returns in the Should commit) and re-ran the R1 tests only: 23 passed. The "270 passed" in that commit message is 269 + that one re-run, not a second full run.
- `86d29b2` (Should): one full run gave 294 passed, 2 failed. Both were `test_R7_...[beyond]` reading "Dominant: F#" before the R9 fix for the sharp sign had landed. I made that one check accept either sign and re-ran R6/R7: 6 passed. "296 passed" in that commit message is 294 + those two, not a second full run.

## Register

| ID | Status | What changed (functions) | Tests |
|---|---|---|---|
| R1 | Pass, with limits below | New Backup card on the Record tab (`backupCard`, in `renderRecord`), and the footer now links to it. `backupObj` / `backupText`: full saved state as JSON inside a small wrapper (`app`, `format`, `version`, `saved`, `state`). `bkDownload`: uses the viewer's downloads capability if `window.claude.use('downloads')` gives one (`dlFind`), otherwise a blob `<a download>` (`bkBlob`). `bkCopy`: clipboard, else shows the text in a visible, selected textarea (`bkShowOut`). Import by file (`#bkFile`, FileReader) or paste, both through `readBackup` (validation) and `bkOffer` (in-page "Replace your progress with this backup?" box), then `bkApply` (replace, save, re-render). Loading was pulled into one `loadState(L)` used by both page load and import, so an import is treated exactly like a reload. | `test_R1_backup_panel_is_findable`, `..._export_import_round_trip_is_lossless`, `..._import_accepts_a_raw_saved_state_and_old_saves`, `..._bad_backup_is_rejected_and_changes_nothing` (13 inputs), `..._confirm_box_cancel_changes_nothing`, `..._import_by_file_pick`, `..._copy_falls_back_to_a_visible_textarea`, `..._download_uses_the_viewer_capability_when_present`, `..._works_in_a_sandboxed_frame`, `..._no_browser_popups_in_source`, `test_version_label_is_0_7` |
| R2 | Pass | New `finOn(s)`: a gig song reads `gig.useFin`, a Path stage reads `useFin`. `bandPat` and `feelMiss` use it. `gigS` gives `gig.useFin` a default of off. Gig song card has its own switch ("Song's own feel" / "<Finish> feel", `data-gpat`) with its own click handler; the Finish-chip handler now stops the band only if the tab that is playing has its feel on. | `test_R2_gig_song_keeps_its_own_feel` (Path on Tangos, boogie still swung, checked on the scheduled drum hits), `test_R2_gig_feel_switch_changes_gig_only` |
| R3 | Pass | `roadmap`: in Present mode on the Gig tab the chart is drawn four bars a line (two on phones) instead of eight (four), so the same width shows each bar about twice as large. CSS under `.present` enlarges phase headings, their sub-notes, the form strip and card headings. The Present button now re-renders the Gig tab. | `test_R3_present_mode_enlarges_chart_and_phase_headings` (360/768/1280 x boogie and La Bamba: chord text at least 1.5x, phase heading at least 1.35x, no overflow, chart still follows playback, sizes restored on leaving), `test_R3_present_mode_does_not_touch_the_path_chart` |
| R4 | Pass | Pattern names: "Straight quavers", "Backbeat quavers", "Rock waltz quavers", "Palm-muted quavers", "Palm-muted quavers in three". Technique text "Strum quavers". | `test_R4_quavers_not_eighths` (5 instruments x 4 Finishes, every stage, tab and gig song; visible text plus aria-labels) |
| R5 | Pass | Capo click handler now calls `renderSide()` as well as `renderStage()`. | `test_R5_changes_card_follows_capo` (bass, keys), `test_R5_guitar_changes_card_keeps_shapes` |
| R6 | Pass, one judgement call | Verse map is `Am G Am E / Am G Am E Am`. See "Judgement calls": F was also taken out of the stage's chord list. | `test_R6_greensleeves_verse_bar_3_is_A_minor` (chords suite), `test_R6_greensleeves_chart_and_band_agree` (chart text, chord boxes, and the band's bass note in bar 3 is A) |
| R7 | Pass | New function `N` ("subtonic") in `FN` with its own colour variable `--sub` (dark `#b3a98f`, light `#5e5340`: a neutral ivory-brown). `KEYS`: G in A minor and A in B minor are `['VII','N','subtonic']`. Chord box, chart and the function card all read from `FN`, so they agree. `--dom` not touched. | `test_R7_subtonic_is_not_a_dominant` (chords suite), `test_R7_subtonic_not_coloured_dominant` (both stages, light and dark; also asserts the dominant colours are still `#d0574b` / `#a8352b`), `test_R7_true_dominant_E7_still_dominant`; existing `test_roman_numerals_and_functions` updated to expect `N` for a minor-key VII |
| R8 | Pass | New `drumWords(p,d)` builds the sentence from the same `drumPat` the band plays, e.g. "hats in swung quavers, snare on 2 and 4, kick on 1 and 3". Used in the grid's note and its aria-label in `drumGrid`. | `test_R8_drum_panel_uses_drum_words` (all stages and the Gig, each Finish feel on and off) |
| R9 | Pass | New `shp()` turns `#` into `♯`; used in the function card (`renderSide`), the Invent pool and saved loops (`renderInvent`), and the chord-box and chart aria-labels. La Bamba's note now reads "Recordings vary in key; the loop is the same four bars all the way through" (12-bar songs keep "bars 10 and 12"). Play row reads "at the metronome tempo, which counts the dotted crotchet," in 6/8 and has no bracket otherwise. | `test_R9_f_sharp_uses_the_proper_sign`, `test_R9_la_bamba_bar_reference_fits_its_loop`, `test_R9_bpm_label_is_tidy` (5 instruments) |
| R10 | Pass | `kbd`: lit black keys fill from `--kbl` (dark mode `#f0d48a` as before; light mode `#a47510`). Contrast against the cream white keys goes from about 1.1 to about 3.2; against unlit black keys about 4.7; note name on the key about 4.7. | `test_R10_lit_black_key_contrast_in_light_mode` (A and E), `test_R10_follows_the_page_theme_not_just_the_os`; existing M2 tests still pass |
| R11 | Pass | New `spellNote(notes,K)` in `partPanel` (bass, keys, vocals): "Not a misprint: C♭ is the same pitch as B. In E♭ minor each letter name is used once, so it is written this way." | `test_R11_spelling_note_only_when_needed` (keys, bass, vocals x every stage x capo 0 to 7: note present exactly when such a spelling is on screen), `test_R11_b_minor_capo_4_explains_c_flat` |
| R12 | Partial: fix applied, cause not confirmed | Test-only change. `test_M3_keys_spelling_every_capo` now waits (`settle_keys_panel`) until the hash, stage title, keyboard count and "Capo N" all match before reading the panel, and reports what is on screen if it never settles. No app change. | The M3 test itself, plus `test_R12_keys_panel_settle_wait_is_real` (the wait is false for a wrong stage or capo). Three full runs in a row passed, as required. |

## Hard constraints

| Constraint | Result |
|---|---|
| localStorage key `shredder`, shape kept, old saves load | Kept. One new field, `gig.useFin`, default off. `test_R1_import_accepts_a_raw_saved_state_and_old_saves` loads a pre-0.6 shaped save both from storage and through import. |
| No `alert` / `confirm` / `prompt` | None in the source (`test_R1_no_browser_popups_in_source`); the R1 tests also trap the three functions in the page and assert none was called. |
| One file plus `fonts/`, no network, no new libraries | Kept. The same test checks for `fetch`, `XMLHttpRequest`, external scripts and stylesheets. |
| Design language | New controls reuse the app's own button, card, note and gate styles; the confirm box is the gold gate box. Checked by screenshot in light and dark, and `test_R1_backup_panel_is_findable` compares the button styles with an existing button. |
| British terms | "quavers" throughout (R4). |
| No student names, lyrics or transcriptions | None added. Test data uses "Player One" and "Player Two". The Backup card tells the user that a backup includes any names typed on the Gig tab. |
| Version label 0.7 | Title and header (`test_version_label_is_0_7`). |
| Out of scope: R13, dominant colour (Q2) | Not touched. |

## Judgement calls

1. **R6: F removed from the Greensleeves stage.** With bar 3 as Am, F no longer appears anywhere on the chart. I took F out of that stage's chord list so the stage teaches exactly the chords it charts (Am, G, E, C); the existing chord suite already requires this ("every stage chord should appear in its song"). Effect: one fewer chord box on stage 6, and "Predominant: F" leaves its function card. F is still taught in stage 4, and the Andalusian cadence card on the Technique tab keeps its F. If F should stay on the stage as an extra shape, it is a one-word change, but that suite rule would then need an exception.
2. **R1: backup format.** The file is a wrapper (`app`, `format`, `version`, `saved`, `state`) around the saved state, so the confirm box can say when the backup was made and a future version can be told apart. Import also accepts the bare saved state, exactly as it sits in localStorage.
3. **R1: validation is stricter than page load.** Page load quietly drops a field of the wrong type. Import refuses the whole backup and says which field is wrong, because the spec asks that bad input change nothing. Fields the app doesn't know are ignored.
4. **R1: Teacher mode.** A backup does not switch Teacher mode on or off. After an import the switch stays as it was in the current session (a reload always turns it off, as before).
5. **R1: "lossless" as tested.** Export from one browser, import into an empty one, and the stored state equals the original field for field, including after a reload and after visiting the Gig tab. Tested for a state in the app's own normal form.
6. **R3 on phones.** At 360 px Present mode draws two bars a line. It is larger, as required, but a phone is not a projector; the readable-from-the-back sizes (chords at least 26 px, phase headings at least 22 px) are asserted at 768 and 1280 only.
7. **R7 colour.** A neutral ivory-brown rather than the purple secondary-dominant colour, so a subtonic is not mistaken for a secondary dominant. Contrast against the card is at least 4.5 in both themes.
8. **R11 covers B♯ and E♯ as well** as C♭ and F♭ (e.g. B minor capo 2 has B♯ in G♯ major). The spec says "C♭/F♭-type spellings".

## Gaps and things to know

- **R1 has not been run inside a real claude.ai artifact.** The capability path follows the artifact runtime's published contract (`claude.use('downloads')`, then `save({filename, data})`, with `declined` handled as a cancel) and is tested against a stand-in object, not the real viewer. The artifact must also declare the downloads capability when it is published; without that the page falls back to the blob link by itself.
- **Blocked downloads cannot be detected.** In a sandboxed frame without download permission the browser drops a blob download silently. The message after Download therefore always says to use Copy backup if no file appeared. The sandbox test confirms the panel keeps working there (copy falls back to the visible text box; import by paste and by file both work); it cannot confirm a file lands on disk, because in that frame none does.
- **Storage inside a sandboxed frame.** With storage blocked, progress (imported or not) lasts only until the page is reloaded. That was already true in 0.6; the backup panel is the way round it.
- **R12 cause not found.** I could not make the test fail: the baseline full run passed, the test passed 6 times in isolation under CPU load, and 250 seeded page loads showed no stale state. I found no race in the app (the route change is synchronous). So the settle wait is a guard against slow rendering under load, not a fix for a known cause. If it flakes again the new failure message will show what was on screen.
- **Not changed, noticed in passing:** on bass and keys with a capo, the "Function in this stage" card still lists the guitar's shape names (R5 asked only for the one-minute changes card). For drums, the Metronome card and top bar still show the guitar strum name and D/U cells, with the existing line explaining them (R8 covers the drum panel). The internal pattern key `eighths` is unchanged; it is never shown.
- **Visual check** was by screenshot of the Backup card (light and dark), Present mode at 1280, the Greensleeves stage and the keys panel in light mode. Present mode at 360 and 768 was checked by the tests' measurements, not by eye.
