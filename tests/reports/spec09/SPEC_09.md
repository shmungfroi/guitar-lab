# The Guitar Lab 0.9: approved spec (register 0.8)

Approved by Justin, 27 Nov 2026: ".8 approved" (register 0.8 as recommended).
Baseline: `main` a51db99 (0.8), full suites 344/344.

## Scope
Fix U1 and U3 as below. **U2 approved as "leave"**: do not change the lit key colours (`--kbl:#a47510`, lit white `#7a5c12`); it goes to the program-wide design pass. **R13** (per-instrument content) is out of scope here: its framework is being drafted separately. No other features or redesign.

## Hard constraints (unchanged)
- localStorage key `shredder` and data shape unchanged; 0.7/0.8 backups and bare state still import.
- No `alert`/`confirm`/`prompt`; in-page confirms only.
- One `index.html` + `fonts/`; no network, no libraries.
- Brand unchanged; dominant `#d0574b` / `#a8352b` untouched.
- British/Australian spelling. No student names, lyrics or transcriptions.
- Version label 0.9 everywhere 0.8 shows (title, header, new backup `version`, "newer version" message).

## Register
| ID | Sev | Finding | Required change | Regression test |
|---|---|---|---|---|
| U1 | Could | In a frame where storage is blocked, the import question still says "Everything saved in this browser now… will be replaced", and the Backup card intro and the footer say "Your progress lives in this browser only". The message after import is already honest (0.8). | When storage is unavailable (detect once, e.g. a guarded test write to localStorage), the import question says the progress loaded on this page now will be replaced; the Backup card intro and footer say this page can't keep progress here, so a backup (Download or Copy) is the only way to keep it. Where storage works, today's wording stays exactly as it is. | Sandboxed frame without storage: import question, Backup intro and footer contain no "saved in this browser" / "lives in this browser"; they mention keeping a backup. Normal page: wording unchanged from 0.8 |
| U3 | Could | At 320 px, outside Present mode, the Gig drum grid for a quaver groove is ~269 px in a ~250 px card and scrolls ~19 px inside it (0.7 behaviour). | Apply the same shrink-to-fit rule the Present narrow rule uses to every drum grid (Path and Gig) below about 340 px, so no drum grid scrolls inside its card at 320/360 px. Wider layouts unchanged; Present enlargement unchanged. | Drums, Path all stages and Gig all six songs, quaver and straight feels, 320 and 360 px, Present off and on: grid scrollWidth ≤ clientWidth + 1; no page overflow; at 1280 sizes unchanged from 0.8 |

## Test plan
- Add `test_U1_…` and `test_U3_…` to `tests/test_ui.py`.
- Builder runs only affected tests between stages (`-k "U1 or U3 or T2 or T3 or R1"`), then the full suites once at the end. Expected 344 + new, all passing.
- Update `tests/README.md` for U-items in `reports/spec09/SPEC_09.md`.
- Builder writes `tests/reports/spec09/BUILD_REPORT.md` (self-check, item by item, judgement calls, gaps, pass counts against commit).
