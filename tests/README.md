# Tests for The Shredder (index.html)

Three pytest suites. They read `index.html` and never edit it.

| Suite | What it checks | Time |
|---|---|---|
| `test_chords.py` | The 18 chord shapes (frets, fingers, barres, the notes they sound against their spelling), fretboard diagrams, key spellings, roman numerals and functions, sol-fa roots, bass root/fifth positions, song maps vs keys and labelled progressions, strum and Finish patterns, capo sounding keys | ~1 s |
| `test_ui.py` | Render matrix (8 stages x 7 tabs x 5 instruments x 360/768/1280 px x light/dark: no console errors, no page-level horizontal overflow, key panels present); functional tests (gates, sign-off, grading, playback start/stop, capo, mute, gig max four, gig timer, roles); one or more tests per register item M1-M5, S1-S15 in `reports/spec06/SPEC_06.md` | ~70 s |
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
python3 -m pytest tests -q -p no:cacheprovider                 # everything, ~2 min
python3 -m pytest tests/test_chords.py -q -p no:cacheprovider  # one suite
python3 -m pytest tests/test_ui.py -q -p no:cacheprovider -k "not matrix"   # skip the big matrix
python3 -m pytest tests/test_ui.py -q -p no:cacheprovider -k "M3 or S6"     # register items
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
- Results for each build go in `reports/<spec>/TEST_BASELINE.md`.
