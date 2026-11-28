"""First Steps (0.11): tests F1-F17 of tests/reports/firststeps/SPEC_FS.md, plus the booklet amendments.

A true first visit is opened with returning=False (see uihelp.open_app). Tests find parts and strings by their ids
(data-part, data-string) and questions by data-ask; none depends on the drawing's geometry, so the artwork can be
replaced without touching this file.
"""
import json
import pathlib
import re
import subprocess
import sys

import pytest

import appdata
from uihelp import OVERFLOW_JS, go, state, starts

D = appdata.load()
CH, OPEN = D["CH"], D["OPEN"]
ALL_TABS = ["Path", "Warm-up", "Rudiments", "Technique", "Invent", "Gig", "Record"]
STAGE1 = {f"a-e:{i}": 2 for i in range(5)}
STAGE2 = {f"twelve-bar:{i}": 2 for i in range(5)}
DONE = {"done": [1, 2, 3, 4, 5, 6, 7], "complete": True, "placed": False}
TITLES = ["Meet the guitar", "Get ready", "The strings", "Hear the open strings", "Chord diagrams", "TAB", "First sound"]


def tabs(pg):
    return pg.evaluate("()=>[...document.querySelectorAll('#tabs a')].filter(a=>a.getClientRects().length).map(a=>a.textContent)")


def views(pg):
    return pg.evaluate("()=>[...document.querySelectorAll('section.view')].filter(s=>s.getClientRects().length).map(s=>s.id)")


def raw(pg):
    return pg.evaluate("()=>localStorage.getItem('shredder')")


def vis(pg, sel):
    return pg.evaluate("s=>{const e=document.querySelector(s);return !!e&&e.getClientRects().length>0}", sel)


# ===================================================================== F1 first open

def test_F1_first_open_shows_only_first_steps_step_1(app):
    pg = app(returning=False)
    assert views(pg) == ["v-first-steps"]
    assert tabs(pg) == ["First Steps"]
    assert pg.inner_text("#v-first-steps h2") == TITLES[0]
    assert "step 1 of 7" in pg.inner_text("#v-first-steps .fst-eye")
    for sel in ("#finishes", "#nswBtn", ".mbar", "#neck", "[data-inst]"):
        assert not vis(pg, sel), sel + " should not compete with First Steps"
    assert raw(pg) is None, "a first visit writes nothing until a check is passed"
    for h in ("path", "gig", "a-e", "warm-up"):
        go(pg, h)
        assert views(pg) == ["v-first-steps"], "#" + h + " must not get round First Steps"
    assert not pg.errors


# ===================================================================== F12 tabs as needed

@pytest.mark.parametrize("lv,want", [({}, ["Path", "Record"]), (STAGE1, ["Path", "Warm-up", "Rudiments", "Record"]),
                                     (STAGE2, ["Path", "Technique", "Invent", "Gig", "Record"]), ({**STAGE1, **STAGE2}, ALL_TABS)],
                         ids=["after-first-steps", "stage-1-gate", "stage-2-gate-only", "both-gates"])
def test_F12_tabs_follow_the_gates(app, lv, want):
    pg = app(state={"fs": DONE, "lv": lv})
    assert tabs(pg) == want
    for t in ALL_TABS:
        go(pg, t.lower())
        got = views(pg)
        assert got == (["v-" + t.lower()] if t in want else ["v-path"]), f"#{t.lower()} showed {got}"
    assert not pg.errors


def test_F12_teacher_mode_shows_every_tab_and_never_forces_first_steps(app):
    pg = app(state={"fs": DONE})
    pg.click("#tchBtn")
    assert tabs(pg) == ALL_TABS
    pg.click("#tchBtn")
    assert tabs(pg) == ["Path", "Record"]
    pg = app(returning=False)
    pg.click("#tchBtn")
    assert tabs(pg) == ["First Steps"] + ALL_TABS, "First Steps stays available to a teacher"
    go(pg, "gig")
    assert views(pg) == ["v-gig"]
    pg.click("#tchBtn")
    assert views(pg) == ["v-first-steps"] and tabs(pg) == ["First Steps"]
    assert not pg.errors


def test_F12_a_new_tab_is_announced_once_and_stays_open(app):
    pg = app(state={"fs": dict(DONE, seen=["path", "record"])})
    assert pg.locator("#tabNote").count() == 0
    for i in range(5):
        for _ in range(2):
            pg.click(f'[data-lv="a-e:{i}"][data-dir="1"]')
    note = pg.inner_text("#tabNote")
    assert "Rudiments is open: short daily drills for your hands." in note and "Warm-up is open:" in note
    assert tabs(pg) == ["Path", "Warm-up", "Rudiments", "Record"]
    assert sorted(state(pg)["fs"]["seen"]) == ["path", "record", "rudiments", "warm-up"]
    go(pg, "rudiments")
    go(pg, "path")
    assert pg.locator("#tabNote").count() == 0, "announced once"
    pg.click('[data-lv="a-e:0"][data-dir="-1"]')
    assert "a-e" not in state(pg)["gates"]
    assert tabs(pg) == ["Path", "Warm-up", "Rudiments", "Record"], "a tab that has opened stays open"
    pg.reload()
    pg.wait_for_selector("#tabs a[aria-current=page]", state="attached")
    assert tabs(pg) == ["Path", "Warm-up", "Rudiments", "Record"] and pg.locator("#tabNote").count() == 0
    assert not pg.errors


# ===================================================================== F13 returning saves

OLD_SAVES = {"one-level": {"lv": {"a-e:0": 1}}, "journal": {"journal": [{"d": 1764200000000, "st": "a-e", "inst": "guitar", "h": "x", "o": "", "w": ""}]},
             "mark": {"marks": {"a-e:0": 1}}, "gate": {"lv": STAGE1, "gates": {"a-e": 1764200000000}}, "bass-level": {"lv": {"a-e@bass:0": 2}}}


@pytest.mark.parametrize("name", list(OLD_SAVES))
def test_F13_returning_save_skips_first_steps_and_keeps_every_tab(app, name):
    seed = OLD_SAVES[name]
    pg = app(state=seed, returning=False)
    assert views(pg) == ["v-path"] and tabs(pg) == ALL_TABS
    assert json.loads(raw(pg)) == seed, "loading must not rewrite a 0.9 save"
    pg.click("#nswBtn")  # any ordinary save
    assert "fs" not in state(pg), "a 0.9 save gains nothing until a First Steps check is passed"
    assert pg.locator("#tabNote").count() == 0
    go(pg, "first-steps")
    assert views(pg) == ["v-first-steps"], "First Steps can be revisited"
    assert not pg.errors


# ===================================================================== F15 other instruments

@pytest.mark.parametrize("inst", ["bass", "drums", "keys", "vocals"])
def test_F15_other_instruments_keep_0_9_behaviour_with_a_note(app, inst):
    pg = app(state={"inst": inst}, returning=False)
    assert views(pg) == ["v-path"] and tabs(pg) == ALL_TABS
    assert pg.inner_text("#fsSoon").startswith(f"First Steps for {inst} is coming")
    assert pg.locator("#fsLink").count() == 0
    go(pg, "first-steps")
    assert views(pg) == ["v-path"]
    pg.click('[data-inst="guitar"]')
    assert views(pg) == ["v-first-steps"], "a guitar student with nothing saved starts at First Steps"
    assert not pg.errors


def test_F15_first_steps_student_who_switches_instrument_gets_every_tab(app):
    pg = app(state={"fs": DONE})
    assert pg.locator("#fsSoon").count() == 0 and pg.get_attribute("#fsLink", "href") == "#first-steps"
    pg.click('[data-inst="drums"]')
    assert tabs(pg) == ALL_TABS and "drums" in pg.inner_text("#fsSoon")
    pg.click('[data-inst="guitar"]')
    assert tabs(pg) == ["Path", "Record"]
    assert not pg.errors
