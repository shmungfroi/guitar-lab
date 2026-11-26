"""R13 (0.10): per-instrument content. Tests X1-X13 of tests/reports/r13/SPEC_R13.md, guitar and bass.

X11 (bass theory data) is in test_chords.py. Drums, keys and vocals have no content of their own
yet, so here they are only checked to be exactly as they were on 0.9.
"""
import json
import pathlib
import re

import pytest

import x1snap
from uihelp import OVERFLOW_JS, ROOT, URL, go, state, starts

SNAP = json.loads(x1snap.FILE.read_text(encoding="utf-8"))


# --------------------------------------------------------------------- X1 guitar is byte for byte what it was on 0.9

@pytest.mark.parametrize("inst", ["guitar", "drums", "keys", "vocals"])
def test_X1_snapshot_matches_0_9(browser, inst):
    """Guitar's Rudiments, Technique, Invent and eight side panels are unchanged; so are the three
    instruments whose own content has not shipped yet."""
    got = x1snap.capture_all(browser, [inst])
    assert len(got) == 42
    diff = [k for k, v in got.items() if SNAP[k] != v]
    assert not diff, f"{len(diff)} panels differ from 0.9, e.g. {diff[:6]} (see tests/x1snap.py for how to diff)"
