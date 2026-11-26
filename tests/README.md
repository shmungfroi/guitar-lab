# Tests for The Guitar Lab (index.html)

Three pytest suites. They read `index.html` and never edit it.

| Suite | What it checks | Time |
|---|---|---|
| `test_chords.py` | The 18 chord shapes (frets, fingers, barres, the notes they sound against their spelling), fretboard diagrams, key spellings, roman numerals and functions, sol-fa roots, bass root/fifth positions, song maps vs keys and labelled progressions, strum and Finish patterns, capo sounding keys | ~1 s |
| `test_ui.py` | Render matrix (8 stages x 7 tabs x 5 instruments x 360/768/1280 px x light/dark: no console errors, no page-level horizontal overflow, key panels present); functional tests (gates, sign-off, grading, playback start/stop, capo, mute, gig max four, gig timer, roles); one or more tests per register item M1-M5, S1-S15 in `reports/spec06/SPEC_06.md` R1-R11 in `reports/spec07/SPEC_07.md` (`test_R<n>_...`; R6 and R7 also have data tests in `test_chords.py`) T1-T5 in `reports/spec08/SPEC_08.md` (`test_T<n>_...`) and U1, U3 in `reports/spec09/SPEC_09.md` (`test_U<n>_...`) | ~4 min |
| `test_timing.py` | Records every WebAudio source start via an init script and checks the schedule against the beat grid (4/4 at two tempos, swung shuffle, 3/4, 6/8), that nothing is scheduled late, and that a double tap on Play can't stack two bands (S2) | ~30 s |

## Setup (fresh session)

The container normally has these already. If not:

```bash
pip install --break-system-packages pytest playwright
python3 -m playwright install chromium   # skip if PLAYWRIGHT_BROWSERS_PATH already has chromium
```

Node is not needed.

## Run

From the repo root (`/home/claude/guitar`):

```bash
python3 -m pytest tests -q -p no:cacheprovider                 # everything, ~5 min
python3 -m pytest tests/test_chords.py -q -p no:cacheprovider  # one suite
python3 -m pytest tests/test_ui.py -q -p no:cacheprovider -k "not matrix"   # skip the big matrix
python3 -m pytest tests/test_ui.py -q -p no:cacheprovider -k "M3 or S6"     # register items
python3 -m pytest tests/test_ui.py -q -p no:cacheprovider -k "T1 or R10"    # 0.8 items (T1-T5) with the 0.7 test they touch
python3 -m pytest tests/test_ui.py -q -p no:cacheprovider -k "U1 or U3 or T2 or T3 or R1 or version"   # 0.9 items (U1, U3) with the tests they touch
```

`-p no:cacheprovider` just stops pytest writing `.pytest_cache` into the repo.

### Testing an older build

Set `SHREDDER_INDEX` to another copy of the page. It needs a `fonts/` folder next to it
(a symlink is fine):

```bash
mkdir -p /tmp/shredder05 && git show 9d8301a:index.html > /tmp/shredder05/index.html
ln -sfn "$PWD/fonts" /tmp/shredder05/fonts
SHREDDER_INDEX=/tmp/shredder05/index.html python3 -m pytest tests -q -p no:cacheprovider -rf
```

## How it works

- `appdata.py` copies index.html to a temp folder, appends `globalThis.__APP=n=>eval(n)`
  inside the app's block-scoped script (direct eval sees the block's own `const`s),
  loads it in headless Chromium and reads the data tables (`CH`, `KEYS`, `ST`, `GIG`, ...)
  and helpers (`bassPos`, `sounds`, ...) as JSON. It keeps working through refactors as
  long as those names exist.
- `uihelp.py` opens the real page over `file://` with an audio-recording init script
  (every AudioContext, `resume()`, `connect()` and source `start()` is logged; `__audible(e)`
  walks the node graph and multiplies gains to tell whether a note can be heard).
  Saved state is seeded through the app's own `localStorage` key (`shredder`), and
  stages / tabs are changed through the app's own hash routing (`#a-e`, `#gig`, ...).
- Chromium is launched with `--autoplay-policy=no-user-gesture-required` so audio runs headless.
- The gig timer tests use Playwright's fake clock (`page.clock`).

## Notes on specific tests

- Register tests are written against the fixed behaviour in SPEC_06 and fail on 0.5 by design.
- M4: headless Chromium lays the 0.5 drum grid out at ~307 px, which fits a 360 px screen,
  so the phone clipping in the report does not reproduce at 360/390. `test_M4_drum_grid_has_headroom`
  therefore also requires a scroll wrapper, or a grid that fits its column at 320 px.
- S7 treats "beats 1 and 3" as wrong in 3/4 and 6/8 (in 6/8 there are two beats a bar).
- S11 requires the run sheet text to grow by at least 20% in Present mode and the chart not to shrink.
- R1 (0.7): the backup tests stub `navigator.clipboard` and `window.claude.use('downloads')` in the page to reach each
  branch; the sandbox test loads the app in `<iframe sandbox="allow-scripts">` from a temp host page, where storage,
  clipboard and downloads are all blocked.
- R12 (0.7): `test_M3_keys_spelling_every_capo` waits for the keys panel to settle (`settle_keys_panel`) before reading it.
- T1 (0.8): the lit black keys are the same darker gold in both themes, so `test_R10_lit_black_key_contrast_in_light_mode`
  now expects light and dark to match (it used to expect dark to keep `#f0d48a`).
- T2 (0.8): the Present-mode drum grid is measured on the Gig tab (`#v-gig .dgw`) at 320-1280 px, including both sides of the
  480 and 600 px breakpoints.
- T3, T5 (0.8): `sandbox()` in `test_ui.py` loads the app in `<iframe sandbox="allow-scripts">` and collects console errors and
  warnings from the whole page. The font files can't load in that frame over `file://`, so the tests count only messages logged
  after the button press.
- T4 (0.8): `T4_STRUM` is the spec's own word list ("downs", "down-up", "strum"); the wider `STRUM_WORDS` belongs to R8's drum panel test.
- U1 (0.9): the sandboxed-frame test reuses `sandbox()`; the normal-page test holds the three 0.8 sentences as `U1_INTRO_08`,
  `U1_FOOT_08` and `U1_ASK_08`, and also checks that the start-up storage check leaves storage exactly as it found it
  (nothing on a first visit, the same text otherwise).
- U3 (0.9): drums, every Path stage and every gig song, the stage's or song's own pattern and each of the four Finish feels,
  at 320 and 360 px, Present off and on (Present only exists on the Gig tab). `U3_PATH_1280`, `U3_GIG_1280` and
  `U3_PRESENT_1280` are table widths measured on 0.8 (a51db99) in headless Chromium with the bundled fonts; a different
  browser build may need them re-measured with `SHREDDER_INDEX` pointed at 0.8.
- 0.9 version: `test_version_0_9_...` import 0.7, 0.8 and 0.9 wrappers and a bare state, and check the newer-version message.
- Results for each build go in `reports/<spec>/TEST_BASELINE.md` or that spec's `BUILD_REPORT.md`.
