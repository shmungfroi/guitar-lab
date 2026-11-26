# The Guitar Lab 0.8: independent check

**Label: independent check.** Written by a checker that did not build 0.8.
Inputs used: `SPEC_08.md`, `index.html` and `fonts/` on branch `build-0.8` at 8d12082. `BUILD_REPORT.md` and the builder's `test_T*` tests were not read or run. `main`'s `index.html` (0.7) was run once, only to produce a real 0.7 backup file.
Date: 27 Nov 2026. Browser: Playwright Chromium, headless. The existing full suites were not run (left for the main session).

Scripts: `check_scripts/` (`t1_keys.py`, `t2_drumgrid.py`, `t3_t5_sandbox.py`, `t4_wording.py`, `sweep.py`, `shots.py`, shared `common.py`). Raw output: `check_scripts/results/`. Close-up screenshots: `check_scripts/shots/`.

## Verdict

All five register items pass and every hard constraint holds. No Must or Should findings. Four Could findings, two of them already in 0.7.

## Register items

| ID | Verdict | Evidence (measured) |
|---|---|---|
| T1 | PASS | Lit black key fill is `#a47510` in both themes. Against the white key `#ece2c8`: **3.17:1** in dark and in light (target 3:1 or more; 0.7 was `#f0d48a`, 1.12:1). Lit black vs unlit black `#12100b`: 4.64:1. Not the dominant colour (`#d0574b` dark, `#a8352b` light) and not `--sub` (`#b3a98f` dark, `#5e5340` light). Hue 41°, saturation 0.82, so it reads as gold; the dominant red sits near 5°. Note label on the lit black key: 4.64:1. Lit white keys unchanged (`#7a5c12`). Same values on the Path (capo 0 and capo 2) and the Gig. |
| T2 | PASS | Present mode, Drums, all 6 gig songs x 5 feels (song's own, rock, flamenco, bossa, hair metal) = 30 combinations per width. Grid wrapper scrollWidth vs clientWidth: 360 px **290 / 290**; 768 px **669 / 669**; 1280 px **1140 / 1140**. Largest excess at any width: 0 px. Page scrollWidth equals clientWidth at every width. No cell text clipped. At 1280 the Present grid is still larger: font 34 px vs 15 px, cell 48.1 px vs 30.7 px wide. At 360 the Present grid is font 14.04 px, cells 21.5 to 30.7 px. |
| T3 | PASS | Sandboxed iframe (`sandbox="allow-scripts"`, storage confirmed blocked: `SecurityError`). Import message: "Backup imported: 3 levels set, 2 journal entries, 1 one-minute log, 1 warm-up day. It is loaded for this visit only: this page isn't allowed to store anything here, so it will be gone when the page closes. Keep your backup file, and use Download backup or Copy backup before you leave to keep anything new." No "saved in this browser". The state really loaded (Path showed Bass, "C, G and the small F"). Download message: "Backup prepared as guitar-lab-backup-2026-11-27.json. If no file appeared in your downloads, this page isn't allowed to download here: use Copy backup instead." No download event fired in that frame, and the message does not claim one. Normal page: import says "Your progress has been replaced and saved in this browser." and the data is in `localStorage` and survives a reload; Download fires a real download. See finding C1 for the question shown before the import. |
| T4 | PASS | Drums, 8 stages x 5 feels on the Path, plus Gig, Rudiments and Warm-up (55 views): **0** strum names or strum letters in the metronome bar, the Metronome card or its cells. Example bar: "Groove: hats on every beat, snare on 2 and 4, kick on 1 and 3"; cells "1 2 3 4" or "1 & 2 & 3 & 4 &". Bass and Keys at capo 2 on the A–E stage: "Tonic: **B** Chart shows A · Dominant: **F♯** Chart shows E" (also reached by pressing Capo up twice). Guitar at capo 2 unchanged: "Tonic: A · Dominant: E". No overflow at 360 px with the extra note. |
| T5 | PASS | Sandboxed iframe, clipboard blocked by permissions policy (`allowsFeature('clipboard-write')` = false). Copy backup: fallback box visible, holds the 0.8 backup, fully selected; **0 console messages of any type**, also on a second press. Control: calling the clipboard directly in the same frame does log "Permissions policy violation: The Clipboard API has been blocked…", so the harness would have caught it. Also 0 messages when the clipboard call is allowed by policy but rejects. |

## Hard constraints

| Constraint | Verdict | Evidence |
|---|---|---|
| Dominant colours unchanged | PASS | Computed `--dom`: `#d0574b` dark, `#a8352b` light. Compared with `main`, the only colour literal that dropped out of changed lines is `#f0d48a` (the old lit black key). |
| No alert / confirm / prompt | PASS | No such calls in `index.html`. No dialog event in any run (140-view sweep, import, download, copy, capo, Present). Import still asks in-page ("Replace your progress with this backup?"). |
| localStorage key `shredder` | PASS | After an import, `Object.keys(localStorage)` = `["shredder"]`. |
| 0.7 backup files and bare state import | PASS | A backup made by the real 0.7 app (`version: "0.7"`, `format: 1`, 18 state fields) imported three ways: pasted, through the file chooser, and as bare state. Fields that differ after import: none, each time. Damaged text and a `format: 2` file are refused in-page with "Nothing has been changed." |
| Version label 0.8 | PASS | Title "The Guitar Lab 0.8"; header "version 0.8 · a Shmungfroi instrument"; new backup file `version: "0.8"`; "0.7" appears in no rendered view. |
| No network calls | PASS | Requests in every run: `index.html` and the three font files only. No `fetch` or `XMLHttpRequest` in the source. The one outside address is the YouTube search link a student chooses to open, as in 0.7. |
| British spelling | PASS | Rendered text of all 140 views scanned for American spellings and terms (color, center, meter, measure, quarter note and so on): none. The only match is the proper name "SIL Open Font License". |
| On-brand look | PASS | Checked from close-up screenshots in both themes: the keyboard, Function card, drum metronome card and Present grid keep the existing type, card and colour language. Nothing new looks generic. |

## Regression sweep

7 tabs x 5 instruments x 360 and 1280 px x dark and light = **140 views**: 0 console errors or warnings, 0 page-level horizontal overflow, 0 dialogs, 0 requests off the local host. Drum grids on all 8 Path stages x 5 feels at 360 px: no sideways scroll inside the card.

## New findings

No Must. No Should.

| ID | Sev | Finding | Evidence | Recommended fix |
|---|---|---|---|---|
| C1 | Could | In a frame with no storage, the question shown before an import still says "Everything saved in this browser now (0 levels set, …) will be replaced". The message after the import is honest (T3), but the question just before it talks about saved progress that cannot exist there. The Backup card's opening line, "Your progress lives in this browser only", has the same problem in that frame. | `results/t3_t5.json`, "import ask" under `sandbox=allow-scripts`. | When storage is unavailable, word the question as "Everything loaded on this page now (…) will be replaced", and the card's opening line as "this page can't store progress here; a backup is the only way to keep it". |
| C2 | Could | Lit black keys (`#a47510`) and lit white keys (`#7a5c12`) are close to each other: 1.52:1. They are told apart by key shape and position, and the spec only asked for contrast against the unlit white keys, so this is not a T1 failure. The two golds do read as slightly different "lit" colours side by side. | `results/t1.json`; `shots/kb_dark.png`, `shots/kb_light.png`. | Leave as is, or in a later design pass choose one lit gold that works on both key colours. |
| C3 | Could (already in 0.7) | At 320 px, outside Present mode, the Gig drum grid for a quaver groove is 269 px wide in a 250 px card, so it scrolls sideways by 19 px inside its card. The page itself does not overflow. In Present mode at 320 px it fits (250 / 250). 320 px is outside the widths the spec names. | `results/t2.txt`, first lines. The CSS rule involved is unchanged from `main`. | Reuse the Present-mode narrow rule (table at 100% width, no cell minimum) for all drum grids under about 340 px. |
| C4 | Could (R13, out of scope) | With Drums selected, the 12-bar stage on the Path still shows the guitar riff and its tab ("On D move it up a string set … on E move it down"). This is per-instrument stage content, which the spec leaves to R13. | `results/t4.json`, "stage_panel_mentions": 5 views. | Carry into the R13 framework; no change in 0.8. |

## What I could not test

- **Real devices and other browsers.** Everything ran in headless Chromium. Safari and Firefox treat sandboxed downloads, the clipboard and permissions policy differently; the T3 and T5 results are for Chromium only.
- **The claude.ai artifact viewer.** The code has a separate download path for it (`window.claude.use('downloads')`, message "Backup saved as …" once the save resolves). I did not run the app inside a real artifact or stub that interface, so that wording is unverified in practice.
- **How the colours look to a person.** T1 is measured as contrast and hue. Whether `#a47510` "reads as lit gold" on a projector or a cheap classroom screen is a judgement from two screenshots.
- **Sound.** No audio checks; none of T1–T5 changes sound, and the timing suite covers it.
- **The existing full suites** (`test_chords.py`, `test_ui.py`, `test_timing.py`): not run, by instruction.
- **Light and dark for T2–T5.** Those were run in dark only; the 140-view sweep and T1 covered both themes.
- **Teacher mode, the timer and the journal** were not exercised beyond loading their tabs in the sweep.
