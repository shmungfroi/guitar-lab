# The Guitar Lab 0.8: approved spec (register 0.7)

Approved by Justin, 27 Nov 2026: "approve guitar lab as recommended" (all recommended changes for T1–T5).
Baseline: `main` 40910bb (0.7), full suites 311/311 at fd059ea.

## Scope
Fix T1–T5 as recommended below. **Out of scope:** R13 (per-instrument Rudiments / Technique / Invent / stage-1 content: needs its own framework first) and any new feature or visual redesign.
**Q2 (dominant colour) closed 27 Nov:** asked twice without an answer, so under build-method §6.6 the app keeps its current dominant colours exactly (`#d0574b` dark / `#a8352b` light). Do not touch them.

## Hard constraints (unchanged from 0.7)
- Keep the localStorage key `shredder` and the saved-data shape; old saves and 0.7 backup files must load unchanged. Any new fields get defaults.
- No browser pop-ups (`alert`, `confirm`, `prompt`): confirmations stay in-page.
- One file (`index.html`) plus `fonts/`. No network calls, no new libraries.
- Brand and design language unchanged (Poiret One + Outfit, Garden black/ivory/gold, function colours). Nothing generic or AI-looking.
- British/Australian spelling and terms (quavers, crotchets).
- No student names; no lyrics or transcriptions.
- Version label becomes 0.8 everywhere 0.7 is shown (title, footer, backup `version` field for new files; import still accepts 0.7 files and bare state).

## Register
| ID | Sev | Finding | Required change | Regression test |
|---|---|---|---|---|
| T1 | Should | Keyboard drawn cream in both themes; a lit black key `#f0d48a` on `#ece2c8` white keys is 1.12:1 (dark mode repeats the R10 problem). | Darker gold for lit black keys in **both** themes, clearly distinct from the white keys (aim ≥ 3:1 against `#ece2c8`) and still reading as "lit" gold, not brown or red (must not be confused with the dominant red or the subtonic ivory-brown). Lit white keys unchanged unless needed for consistency. | In light and dark: lit black-key fill contrast vs white-key fill ≥ 3:1; lit black ≠ unlit black; lit black not equal to dominant or `--sub` colours |
| T2 | Could | Present mode, 360 px, Drums: enlarged drum grid scrolls sideways inside its card (page doesn't overflow). | Let the grid shrink to fit at narrow widths (cells/labels scale down; no internal horizontal scroll at 360 px in Present mode). Larger widths keep the enlarged look. | Present mode, drums, 360/768/1280: grid scrollWidth ≤ clientWidth (+1px); no page overflow; grid still larger at 1280 Present than non-Present |
| T3 | Could | Sandboxed frame: import says "saved in this browser" when storage isn't available; download says "Backup file made…" before the "If no file appeared…" hint. | Honest wording: when storage is unavailable, import says the progress is loaded for this visit only and to keep the backup file / use Download backup to keep it. Download message must not claim a file was made when that can't be known; lead with neutral wording (e.g. "Backup prepared — if no file appeared, use Copy backup") or confirm only when the download path is known to work. | In a sandboxed frame without storage: import message contains no "saved in this browser"; download message doesn't assert a file was made before the fallback hint. Normal page: existing messages still correct |
| T4 | Could | Drums selected: metronome bar and card still show guitar strum names ("Four downs"). Bass/keys with a capo: "Function in this stage" card still shows guitar shape names. | Instrument-appropriate wording: drums show groove wording (hats/snare/kick or "groove"), never strum names, in the metronome bar and stage card. Bass and keys with a capo show **sounding** chord names in the Function card (with "Chart shows …" style note consistent with the other panels). Guitar unchanged. | Drums: no strum names ("downs", "down-up", "strum") in metronome bar or stage card. Bass and keys at capo 2 on A–E stage: Function card shows B / F♯ (sounding) names |
| T5 | Could | Blocked clipboard in a sandboxed frame leaves two browser console messages (fallback works). | Catch the clipboard failure quietly (no console error/warning); fallback textarea still appears. | Sandboxed frame, clipboard blocked: Copy backup → fallback visible, zero console errors/warnings from it |

## Test plan
- Add `test_T1_…` to `test_T5_…` in `tests/test_ui.py` (one or more each).
- Builder runs only affected tests between stages, then the full suites **once** at the end (`test_chords.py`, `test_ui.py`, `test_timing.py`). Expected: 311 + new tests, all passing.
- Update `tests/README.md` to mention T-items in `reports/spec08/SPEC_08.md`.
- Builder writes `tests/reports/spec08/BUILD_REPORT.md`: item-by-item against this spec, judgement calls, what wasn't tested.
