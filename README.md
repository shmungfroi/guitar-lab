# The Guitar Lab

A Shmungfroi instrument: a browser-based guitar and band teacher. Same two chords, four Finishes (rock and roll, flamenco, bossa, hair metal), and a learning path from A and E to I–V–vi–IV and Hallelujah in C. Band mode covers guitar, bass, drums, keys and vocals, and Gig mode runs a class or a private band through a four-song set.

Open `index.html` in a browser (keep `fonts/` next to it). Progress saves in the browser it's used in.

## Repo layout
| Path | What it is |
|---|---|
| `index.html` | The app (one file). |
| `fonts/` | Poiret One and Outfit (SIL Open Font License). |
| `tests/` | Regression suites: chord and theory data, UI matrix, playback timing. See `tests/README.md`. |
| `tests/reports/spec06/` | Approved spec, build report, test baseline and independent check for 0.6. |

## Rules for editing
1. Work on a branch per build; push as you go; merge to `main` after the independent check.
2. Run every suite before publishing (`cd tests && python3 -m pytest -q`).
3. Keep the localStorage key `shredder` and the saved-data shape, or students lose progress.
4. Popular songs: chord maps and a link to the recording only. No lyrics, no transcriptions.
5. Students appear only as codes. No student data in this repo.

Non-commercial teaching resource by Justin Ossher.
