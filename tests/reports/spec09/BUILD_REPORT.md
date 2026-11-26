# The Guitar Lab 0.9: build report (self-check)

**This is the builder's own check, not an independent one.** Spec: `SPEC_09.md` (register 0.8: U1, U3). Branch `build-0.9`, not merged.

- Build commit: `4c8dd7d` (stage A `2529288`, stage B `6dbbb56`, version and README `4c8dd7d`).
- Full suites, run once at `4c8dd7d`'s tree: **382 passed, 0 failed** in 3 min 43 s (`test_chords.py` 163, `test_ui.py` 213, `test_timing.py` 6). Baseline 0.8 was 344; 38 tests are new.
- `index.html` changed by 17 lines added, 10 removed against `main` a51db99. Nothing in `fonts/` changed.

## Item by item

| ID | Result | Measured evidence |
|---|---|---|
| U1 | PASS | Sandboxed frame (`<iframe sandbox="allow-scripts">`, storage blocked). Backup intro now opens "This page can't keep your progress here, so a backup is the only way to keep it: use Download backup or Copy backup before you leave." Footer: "This page can't keep your progress here, so a backup (Download or Copy) is the only way to keep it: make one from the Record tab before you leave." Import question: "The progress loaded on this page now (…) will be replaced, and that can't be undone." None of the three contains "saved in this browser" or "lives in this browser"; each mentions a backup. Normal page (first visit, empty save, full save): intro, footer and question match the 0.8 sentences character for character, and the same three normal-page tests pass when pointed at the 0.8 file. The two sandbox tests fail on 0.8, as they should. |
| U3 | PASS | Drums, 8 Path stages and 6 gig songs, each with its own pattern and with each of the 4 Finish feels, at 320 and 360 px, Present off and on: 200 grids measured. Largest scrollWidth minus clientWidth was 19 px before (24 Gig grids at 320 px: 269 in 250) and 0 px after. No page overflow in any case. The only grids whose size changed are those 24 (268.8 px to 250 px, text still 13 px, cells about 19.6 px). Path grids at 320 px keep their 0.8 widths (158.8 / 180.8 / 224.8 / 268.8 px in a 288 px card); everything at 360 px is unchanged. At 1280 px table widths are the 0.8 values (208.0 / 238.7 / 300.2 / 361.6 px at 15 px; Present 432.1 / 624.4 px at 34 px). The rule is on at 320 and 340 px and off at 341, 360, 481 and 1280 px. On the 0.8 file, 7 of the 28 U3 tests fail (the 320 px Gig cases) and the 1280 px test passes. |
| Version 0.9 | PASS | Title "The Guitar Lab 0.9", header "version 0.9", new backups stamped `version: "0.9"`, newer-version message says "(0.9)". Backups wrapped as 0.7, 0.8 and 0.9 and a bare state all import and round-trip. |

## Hard constraints

| Constraint | Result | Evidence |
|---|---|---|
| Storage key `shredder`, data shape unchanged | PASS | Source still has exactly one `getItem('shredder')` and one `setItem('shredder', …)` (now behind two small helpers); the existing R1 source test passes. No other key is created: after load `Object.keys(localStorage)` is `[]` or `["shredder"]`. |
| No alert / confirm / prompt | PASS | R1 source test passes; pop-up spies stayed empty in the sandbox test. |
| One file plus fonts, no network, no libraries | PASS | R1 source test passes; no new files outside `tests/`. |
| U2 colours and dominant colours untouched | PASS | `#a47510`, `#7a5c12`, `#d0574b`, `#a8352b` each appear the same number of times as on `main`; no changed line mentions any of them. |
| R13 out of scope | PASS | No per-instrument content touched. |
| British spelling | PASS | New wording has no spelling that differs between the two. |

## Judgement calls

1. **How storage is checked (U1).** Once at start-up, by writing back whatever is already stored under `shredder`. On a first visit (nothing stored) it writes a placeholder and removes it straight away, so storage is left exactly as found and no second key ever exists. The spec's example was "a guarded test write"; a separate probe key would have broken the "only `shredder`" rule.
2. **Checked once, as the spec says.** If storage fails later in a visit (for example it fills up), the intro and footer keep the normal wording. The message after an import still tells the truth in that case (0.8 behaviour, T3 test still passes).
3. **Footer wording** adds "before you leave" and keeps the link to the Record tab with new link text ("make one from the Record tab"). In Present mode the footer is hidden, as before.
4. **U3 rule is not a literal copy of the Present rule.** Present's narrow rule stretches the table to the full card (`width:100%`) and trims padding. Copied as is, it would have widened every Path grid at 320 px (for example a four-cell grid from 181 px to 288 px) although those already fit. I used `max-width:100%` with a 22 px preferred cell width instead: grids keep their 0.8 size where there is room and shrink only where there isn't. Same outcome the spec asks for (no grid scrolls), fewer visible changes.
5. **"Below about 340 px"** is implemented as `max-width:340px` (340 included).
6. **Feels tested (U3).** "Quaver and straight feels" was read as: each stage's or song's own pattern (straight fours, quavers, shuffle, 3/4, 6/8) plus all four Finish feels. Present is tested on the Gig tab only, since that is the only place it exists.
7. **Version tests** are named `test_version_0_9_…` rather than `test_U…`, since the version label is not a register item.

## Not tested / gaps

- **Real phones.** Everything was measured in headless Chromium with the bundled fonts. No Safari, Firefox or physical 320 px device was used; a wider fallback font could change the drum-grid numbers.
- **Private browsing and full storage in real browsers** were not exercised; only the sandboxed frame stands in for "storage blocked".
- **claude.ai artifact frame** was not tested directly, only the generic sandboxed iframe.
- **Widths between 320 and 340 px and below 320 px**: only 320 and 340 were measured.
- **Screen reader output** for the new sentences was not checked (they are plain text in the same elements as before).
- **The 1280 px baseline numbers are constants** measured on 0.8 in this container's Chromium; a different browser build could need them re-measured (noted in `tests/README.md`).
- **No visual review** by eye of the 320 px Gig grid; cells are about 19.6 px wide with 13 px text, checked by measurement only.
