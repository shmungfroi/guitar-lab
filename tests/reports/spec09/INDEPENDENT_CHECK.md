# The Guitar Lab 0.9: independent check

**Label: independent check.** Written by a checker that did not build 0.9. Verdicts were formed from `SPEC_09.md`, `index.html` and `fonts/` only, with my own Playwright scripts (`check_scripts/`). I did not read `BUILD_REPORT.md` or the builder's `test_U*` tests, and I did not run the existing suites.

- Checked: branch `build-0.9` at `b5740d8`, against 0.8 on `main` (`git show main:index.html`) and 0.7 at `fd059ea`.
- Browser: Playwright Chromium, headless, only.
- App files changed since 0.8: `index.html` only (17 lines added, 10 removed). `fonts/` untouched.

## Verdicts

| Item | Verdict | Measured evidence |
|---|---|---|
| **U1** storage-blocked wording | **PASS** | Sandboxed frame (`allow-scripts`, and `allow-scripts allow-downloads`; storage reports `SecurityError`), at 1280 and 360: footer, Backup intro and import question contain no "saved in this browser" / "lives in this browser"; the phrase "this browser" appears on none of the 7 tabs. Footer: "This page can't keep your progress here, so a backup (Download or Copy) is the only way to keep it: make one from the Record tab before you leave." Intro: "This page can't keep your progress here, so a backup is the only way to keep it: use Download backup or Copy backup before you leave. …" Question: "The progress loaded on this page now (…) will be replaced, and that can't be undone." Message after import is still the 0.8 one ("loaded for this visit only…"). Same result on a top-level page where `setItem` throws and where reading `localStorage` throws. No console messages, no dialogs, no page overflow. |
| **U1** normal wording unchanged | **PASS** | Character-for-character equal to 0.8: footer (`innerText` and `textContent`), footer link, footer size and link style, Backup intro, whole Backup card, import question (wrapped backup and bare state), message after import; with a seeded save and on a first visit. A sandbox with `allow-same-origin` (storage works) shows the normal wording. Across the 140-view sweep the visible text of every view equals 0.8 once "0.9" is read as "0.8". |
| **U3** no drum grid scrolls at 320 to 360 | **PASS** | 1000 combinations per version (Path 8 stages and Gig 6 songs, each with own feel + rock, flamenco, bossa, hair metal; Gig with Present off and on; 10 widths). At 320, 330, 340, 341, 350, 360: worst `scrollWidth − clientWidth` = **0** everywhere; no grid passes its card; 0 clipped cells; 0 page overflow. The 0.8 fault is reproduced on `main` (Gig, 9-column quaver grid, Present off: 269 in 250 at 320, 19 px scroll; 9 px at 330) and is gone in 0.9 (250 in 250; cells 22 → 19.6 px, font and height unchanged). |
| **U3** wider layouts unchanged | **PASS** | At 341, 350, 360, 480, 768, 1280: **0 of 600** combinations differ from 0.8 in any measured value (wrapper scroll/client width, table width and height, font, cell width and height, first column). Sweep: no card, drum grid, header or footer changed size in 140 views. |
| **U3** Present enlargement unchanged | **PARTIAL** | At 1280 Present font 34 px against 15 px, identical to 0.8; unchanged at every width from 341 up. At 340 and below with Present **on**, table width, height and font are the same as 0.8 and nothing scrolls, but the columns divide differently: the label column is 12 to 18 px narrower and the hit cells 2 to 5 px wider (320: label 98.8..141.5 → 86.3..123.3, cells 18.8..26.9 → 20.3..31.4). See C1. |
| Lit key colours | **PASS** | Computed fills of lit keys (Keys, Path): `#7a5c12` and `#a47510` only, both themes, same as 0.8. `--kbl` computes to `#a47510`. Source counts equal 0.8. |
| Dominant colour | **PASS** | `--dom` computes to `#d0574b` dark, `#a8352b` light; all 17 colour variables equal 0.8 in both themes. |
| No alert / confirm / prompt | **PASS** | None in source; no dialog fired in any run (sweep, sandbox, imports). |
| localStorage: only `shredder` | **PASS** | Source has three calls, all naming `'shredder'`; no sessionStorage, IndexedDB or cookies. After real use: keys `["shredder"]`, session storage and cookies empty. |
| Start-up check leaves saved data byte-identical | **PASS** | Nine seeded raw values (odd spacing with an unknown key and non-ASCII; 0.7-shaped compact; 0.8-shaped indented; not JSON; empty string; `{}`; `null`; an array; wrong types): identical after load, reload and a third load. A spy on `Storage` shows the check makes exactly one call on load, `setItem('shredder', <same value>)`. |
| Start-up check leaves nothing on a first visit | **PASS** | Calls on load: `setItem('shredder','{}')` then `removeItem('shredder')`. Afterwards: no localStorage or sessionStorage keys, no cookies, no databases, no caches. A second tab opening does not disturb a first. (Opening the Gig tab then writes the gig plan, 369 bytes, exactly as 0.8 does: same text at every step.) |
| 0.7 / 0.8 backups and bare state import | **PASS** | Real backup files made by running 0.7 and 0.8 and pressing Download. Pasted and via the file chooser: every field restored, still there after reload, Bass shown. Bare state: same. A 0.9 backup also imports into 0.8, and its `state` is identical to the 0.8 backup of the same save (data shape unchanged). |
| Version label 0.9 | **PASS** | Title "The Guitar Lab 0.9"; header "version 0.9 · a Shmungfroi instrument"; new backup `version: "0.9"`, `format: 1`; newer-version message says "(0.9)". No "0.8" in visible text on any view (the four left in source are code comments). |
| No network | **PASS** | Requests: `index.html` and three font files, nothing off-host. No fetch / XHR / WebSocket / beacon / dynamic import in source. The only URL is the song-search link, as in 0.8. |
| British spelling | **PASS** | No American spellings in the lines 0.9 added or in rendered text over 140 views. The one match, "License", is the proper name "SIL Open Font License", unchanged from 0.8. |
| Sweep: 7 tabs × 5 instruments × 360 / 1280 × dark / light | **PASS** | 140 views: 0 console errors or warnings, 0 page overflow, 0 dialogs, 0 off-host requests, 0 drum grids scrolling. |

## New findings

None are Must or Should. Nothing here blocks 0.9.

**Must:** none.

**Should:** none.

**Could:**

- **C1. Present mode at 340 px and below: columns divide differently from 0.8.** The new rule `.dg th,.dg td{min-width:0;width:22px}` also reaches the Present grid, which is `width:100%`. Overall size and font are unchanged and nothing scrolls or clips, so on screen it reads as slightly wider hit cells and a narrower label column. There is also a small step between 340 and 341 px (narrowest Present cell 22.1 → 20.2 px). *Fix if exact parity is wanted:* scope the new rule to `body:not(.present) .dg …`. *Or accept:* the wider hit cells are arguably the better layout; in that case note it as a judgement call.
- **C2. At 300 px the Gig quaver grid still scrolls 14 px inside its card** (244 in 230; was 39 px in 0.8). This is below the spec's widths (spec: 320/360). The cells stop shrinking at 18.9 px because the label column holds at 91.8 px. *Fix:* in the ≤340 rule let the first column give way too (smaller left/right padding on the first column, or `font-size:12px` under 320 px). Low value: 300 px screens are rare.
- **C3. The start-up check writes saved data back to itself.** With data present it runs `getItem` then `setItem` of the same text. In one tab this is safe (measured byte-identical). With two tabs open, if the other tab saved in the instant between the read and the write, that one save would be overwritten by the older text. I could not make this happen and it is a matter of microseconds, but it is a write of real data that isn't needed. *Fix:* when a save already exists, do not write it back; treat storage as working (`canStore = true`), and let the existing `save()` result keep the message after import honest. Keep the write-then-remove probe for the first-visit case only.
- **C4. Where `setItem` fails but reading works (storage full, some private modes), earlier saved progress still loads, and the page says "This page can't keep your progress here".** True for anything new, but a returning user might read it as "my progress is gone". Rare. *Fix (optional):* no change, or add "anything new" to the wording in that case only.
- **C5. Outside U1's scope:** in a storage-blocked frame the journal's "Save entry" button and level buttons give no sign of their own that the entry lasts for this visit only. The footer on every tab now says so, which may be enough. Flag for the design pass rather than 0.9.

## What I could not test

- Any browser other than headless Chromium: no Safari, Firefox, iOS or Android, no real phone. Sub-pixel table layout at 320 to 340 px may differ by a pixel in other engines.
- A real claude.ai artifact frame, or a real private-browsing window. "Storage blocked" was a sandboxed iframe (opaque origin) plus two simulated top-level failures.
- A genuinely full storage quota, and the two-tab timing in C3 (reasoned from the code, not reproduced).
- Sound, timing and the metronome: not touched by 0.9 and not re-checked.
- The builder's suites (`tests/test_*.py`) were not run and the builder's report was not read, by instruction. The 382/382 figure in the commit log is the builder's claim, not verified here.
- Screen-reader output for the changed footer and Backup card.
- U2 and R13 are out of scope in the spec and were not assessed.

## Scripts and results

| Script | What it does | Result file |
|---|---|---|
| `check_scripts/common.py` | Local server, sandboxed-frame wrapper, 0.8-from-`main` copy, console / dialog / request recording | |
| `check_scripts/u3_grids.py` | Every drum grid, 10 widths, Present off/on, 0.9 and 0.8 side by side (`reuse` re-runs the analysis on saved measurements) | `results/u3.txt`, `results/u3_raw.json` |
| `check_scripts/u1_constraints.py` | U1 wording (blocked and normal), start-up storage check, imports, version, colours, source checks: 111 checks, 0 fails | `results/u1_constraints.json` |
| `check_scripts/sweep.py` | 140-view sweep with text and size comparison against 0.8 | `results/sweep.json` |
| `check_scripts/adhoc.py` | First-visit save step by step against 0.8; other "save/keep" wording in a blocked frame | `results/adhoc.txt` |

Run from `tests/reports/spec09/check_scripts/` with `python3 <script>`.

## Main-session follow-up (Opus, 27 Nov)
- **C3 fixed before merge** (named per build-method §3: a new risk to saved progress introduced in 0.9). `canStore` now returns straight away when a save exists, so an existing save is never rewritten at start-up; only a first visit probes with a write-then-remove. New test `test_C3_startup_check_never_rewrites_existing_save` passes on the fix and fails on the pre-fix build (`b5740d8`).
- Full suites after the fix: **383/383** (163 + 214 + 6). Not re-checked independently: the change is three lines and covered by the new test plus the U1 tests.
- C1, C2, C4, C5 carried to register 0.9 for Justin.
