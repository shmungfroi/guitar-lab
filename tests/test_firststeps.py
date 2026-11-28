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


# ===================================================================== helpers for the checks

SNUM = {6: "low E", 5: "A", 4: "D", 3: "G", 2: "B", 1: "high E"}  # the tests' own table: string 6 is low E
PARTS = ["headstock", "machineHeads", "nut", "neck", "fingerboard", "frets", "positionMarkers", "body", "soundHole", "pickguard",
         "saddle", "bridge", "strings", "pickups"]


def fresh(app, done=(), **kw):
    """A student part-way through First Steps: the steps in done are passed."""
    return app(state={"fs": {"done": list(done), "complete": False, "placed": False}}, returning=False, **kw)


def ask(pg):
    return pg.get_attribute("#fsQuiz", "data-ask")


def expected(pg):
    """Work the right answer out from what is asked and from the app's chord data, never from the page's own marking."""
    a = ask(pg).split(":")
    if a[0] == "part":
        return a[1]
    if a[0].startswith("str-"):
        return a[1]
    if a[0] in ("dia-finger", "dia-fret"):
        c, n = CH[a[1]], int(a[2])
        return (c["g"] if a[0] == "dia-finger" else c["f"])[6 - n]
    if a[0] in ("dia-open", "dia-mute"):
        f = CH[a[1]]["f"]
        return ",".join(str(6 - i) for i in range(6) if f[i] == ("0" if a[0] == "dia-open" else "x"))
    if a[0] == "tab":
        s, f = json.loads(pg.get_attribute("#fsQuiz", "data-ev"))[int(a[1])]
        return f"{6 - s}:{f}"
    raise AssertionError("unknown question " + ask(pg))


def give(pg, val):
    if ask(pg).startswith("part:"):
        pg.click(f'#v-first-steps .gtag[data-part="{val}"]')
    else:
        pg.click(f'#fsQuiz [data-fa="{val}"]')


def options(pg):
    if ask(pg).startswith("part:"):
        return PARTS
    return pg.evaluate("()=>[...document.querySelectorAll('#fsQuiz [data-fa]')].map(b=>b.dataset.fa)")


def passed_quiz(pg):
    return pg.get_attribute("#fsQuiz", "data-pass") == "1"


def run_quiz(pg, limit=40):
    pg.click("#fsQuizGo")
    seen = []
    for _ in range(limit):
        if passed_quiz(pg):
            return seen
        seen.append(ask(pg))
        give(pg, expected(pg))
    raise AssertionError("quiz never passed")


def next_off(pg):
    return pg.is_disabled("#fsNext")


def osc(pg):
    return [s for s in starts(pg) if s["kind"] == "osc"]


def ear_answer(pg, wrong=False):
    n = len(osc(pg))
    pg.click("#fsEarPlay")
    two = osc(pg)[n:]
    assert len(two) == 2 and two[0]["when"] < two[1]["when"]
    a, b = two[0]["freq"], two[1]["freq"]
    ratio = max(a, b) / min(a, b)
    assert ratio >= 2 ** (1 / 12) - 1e-6, f"pair closer than a semitone: {a} {b}"
    up = b > a
    pg.click('[data-ear="up"]' if up != wrong else '[data-ear="down"]')
    return ratio


def pass_ear(pg):
    return [ear_answer(pg) for _ in range(4)]


# ===================================================================== F2, F3 checks gate Next; wrong answers don't pass

def test_F2_F4_step_1_tap_quiz_gates_next(app):
    pg = app(returning=False)
    assert next_off(pg)
    assert pg.evaluate("()=>[...document.querySelectorAll('#v-first-steps .gtag')].map(g=>g.dataset.part).sort()") == sorted(PARTS)
    for kind in ("acoustic", "electric"):
        got = pg.evaluate("()=>[...document.querySelectorAll('#v-first-steps svg.gart')].map(s=>[s.getAttribute('aria-label'),[...s.querySelectorAll('[data-part]')].map(g=>g.dataset.part).sort(),[...new Set([...s.querySelectorAll('[data-string]')].map(g=>g.dataset.string))].sort()])")
    assert len(got) == 2 and got[0][2] == got[1][2] == list("123456")
    assert "pickups" in got[1][1] and "pickups" not in got[0][1] and "soundHole" in got[0][1] and "soundHole" not in got[1][1]
    pg.click('.gtag[data-part="nut"]')
    assert pg.inner_text("#fsCap").startswith("3 · Nut")
    assert pg.evaluate("()=>document.querySelectorAll('.gart [data-part=nut].on').length") == 2, "the part lights up on both drawings"
    pg.click("#fsQuizGo")
    assert pg.locator(".fst-key").count() == 0 and pg.locator("#fsCap").count() == 0, "names are hidden during the check"
    assert all(re.fullmatch(r"Label \d+", l) for l in pg.evaluate("()=>[...document.querySelectorAll('.gtag')].map(g=>g.getAttribute('aria-label'))"))
    # a wrong tap says what it was, does not pass, and the same part is still being asked
    want = expected(pg)
    wrong = next(p for p in PARTS if p != want)
    give(pg, wrong)
    assert "You tapped" in pg.inner_text("#fsFb") and ask(pg) == "part:" + want and "0 of 5" in pg.inner_text("#fsQuiz")
    give(pg, want)
    assert "0 of 5" in pg.inner_text("#fsQuiz"), "a part found on the second go does not count"
    pg.click("#fsQuizEnd")
    assert next_off(pg) and "fs" not in state(pg)
    seen = run_quiz(pg)
    assert len(seen) == 5 and all(s.startswith("part:") and s[5:] in PARTS for s in seen)
    assert not next_off(pg) and state(pg)["fs"]["done"] == [1]
    pg.click("#fsNext")
    assert pg.inner_text("#v-first-steps h2") == TITLES[1]
    assert not pg.errors


def test_F2_step_2_honour_tick(app):
    pg = fresh(app, [1])
    assert pg.inner_text("#v-first-steps h2") == TITLES[1] and next_off(pg)
    body = pg.inner_text("#v-first-steps")
    for w in ("right leg", "never down", "pad of your thumb", "wrist", "behind the fret", "thumb behind the neck", "T thumb, 1 index, 2 middle, 3 ring, 4 little",
              "downstroke", "upstroke", "Left-handed?", "Mirror everything"):
        assert w in body, w
    pg.check('[data-ftick="2"]')
    assert not next_off(pg) and state(pg)["fs"]["done"] == [1, 2]
    pg.uncheck('[data-ftick="2"]')
    assert next_off(pg) and state(pg)["fs"]["done"] == [1]
    assert not pg.errors


def test_F2_F3_F5_strings_quiz(app):
    pg = fresh(app, [1, 2])
    assert pg.inner_text("#v-first-steps h2") == TITLES[2] and next_off(pg)
    body = pg.inner_text("#v-first-steps .fst-body")
    assert "String 6 is the thickest" in body and "low E" in body and "closest to the floor" in body and "E A D G B E" in body
    assert "fret 1 is finger 1, fret 2 is finger 2 and fret 3 is finger 3" in body
    # the labelled drawing: string numbers beside the letters, 6 = E at the bottom
    labels = pg.evaluate("()=>[...document.querySelectorAll('.fst-strfig > text')].slice(0,12).map(t=>t.textContent)")
    assert labels == ["1", "E", "2", "B", "3", "G", "4", "D", "5", "A", "6", "E"]
    ys = pg.evaluate("()=>[1,6].map(n=>document.querySelector('.fst-strfig path.gs[data-string=\"'+n+'\"]').getBoundingClientRect().top)")
    assert ys[1] > ys[0], "string 6 is drawn at the bottom"
    pg.click("#fsQuizGo")
    kinds = set()
    for _ in range(60):
        if passed_quiz(pg):
            break
        kind, n = ask(pg).split(":")
        kinds.add(kind)
        n = int(n)
        q = pg.inner_text("#fsAsk")
        labels = dict(pg.evaluate("()=>[...document.querySelectorAll('#fsQuiz [data-fa]')].map(b=>[b.dataset.fa,b.textContent])"))
        if kind == "str-hl":
            assert pg.evaluate("()=>[...document.querySelectorAll('.fst-strfig path.gs.on')].map(p=>p.dataset.string)") == [str(n)]
            assert pg.locator(".fst-strfig > text").count() == 0, "no labels while a string is being asked"
        if kind in ("str-hl", "str-num"):
            assert {int(k): v.lower() for k, v in labels.items()} == {k: v.lower() for k, v in SNUM.items()}
            if kind == "str-num":
                assert f"number {n}" in q
        else:
            assert f"the {SNUM[n]} string" in q and labels == {str(i): str(i) for i in range(1, 7)}
        if len(kinds) == 1 and "0 of 5" in pg.inner_text("#fsQuiz"):  # one wrong answer on the way
            give(pg, str(n % 6 + 1))
            assert ask(pg) == f"{kind}:{n}" and not passed_quiz(pg) and "Count from there" in pg.inner_text("#fsFb")
            give(pg, str(n))
            assert "0 of 5" in pg.inner_text("#fsQuiz")
            continue
        give(pg, str(n))
    assert passed_quiz(pg) and kinds == {"str-hl", "str-num", "str-name"}
    assert state(pg)["fs"]["done"] == [1, 2, 3] and not next_off(pg)
    assert not pg.errors


def test_step_3_memory_line_is_optional_and_saved(app):
    pg = fresh(app, [1, 2])
    assert "Make your own memory line (E A D G B E)" in pg.inner_text("#v-first-steps")
    eg = re.search(r"Ours, to start you off: ([^.]+)\.", pg.inner_text("#v-first-steps")).group(1)
    assert [w[0] for w in eg.split()] == list("EADGBE")
    for common in ("Eddie", "Elephants", "Easter", "Every"):
        assert common not in eg
    pg.fill("#fsLine", "Eels Always Dance Gently Before Eating")
    assert state(pg)["fs"]["line"] == "Eels Always Dance Gently Before Eating" and state(pg)["fs"]["done"] == [1, 2]
    pg.reload()
    pg.wait_for_selector("#fsLine")
    assert pg.input_value("#fsLine") == "Eels Always Dance Gently Before Eating"
    assert not pg.errors


def test_step_3_tapping_a_string_plays_it(app):
    pg = fresh(app, [1, 2])
    n = len(starts(pg))
    pg.click('[data-fpl="6"]')
    pg.locator('.fst-strfig .gh[data-string="1"]').click(force=True)
    assert len(starts(pg)) == n + 2 and all(s["kind"] == "buf" for s in starts(pg)[n:])
    assert not pg.errors


# ===================================================================== F6 open strings and the ear check

E2A2 = {6: 82.41, 5: 110.00, 4: 146.83, 3: 196.00, 2: 246.94, 1: 329.63}  # E2 A2 D3 G3 B3 E4


def test_F6_reference_tones_and_ear_check(app):
    pg = fresh(app, [1, 2, 3])
    assert pg.inner_text("#v-first-steps h2") == TITLES[3] and next_off(pg)
    for n, hz in E2A2.items():
        k = len(osc(pg))
        pg.click(f'[data-fref="{n}"]')
        o = osc(pg)[k:]
        assert len(o) == 1 and abs(o[0]["freq"] - hz) < 0.01 and o[0]["type"] == "triangle", (n, o)
        assert pg.evaluate("e=>window.__audible(window.__aud.starts[e])", o[0]["i"]) > 0
        assert pg.get_attribute(f'[data-fref="{n}"]', "aria-pressed") == "true"
    # it repeats until tapped again
    k = len(osc(pg))
    pg.wait_for_timeout(3100)
    again = osc(pg)[k:]
    assert again and all(abs(o["freq"] - E2A2[1]) < 0.01 for o in again)
    pg.click('[data-fref="1"]')
    k = len(osc(pg))
    pg.wait_for_timeout(3100)
    assert len(osc(pg)) == k and pg.get_attribute('[data-fref="1"]', "aria-pressed") == "false"
    # the ear check: the tick is locked until it is passed; a wrong answer does not move on
    assert pg.is_disabled('[data-ftick="4"]') and pg.is_disabled('[data-ear="up"]')
    ear_answer(pg, wrong=True)
    assert "Pair 1 of 4" in pg.inner_text("#fsEar") and "Not this time" in pg.inner_text("#fsEar") and pg.is_disabled('[data-ear="up"]')
    ratios = pass_ear(pg)
    assert ratios == sorted(ratios, reverse=True) and ratios[0] > 3.9 and abs(ratios[-1] - 2 ** (1 / 12)) < 1e-3, "big gaps first, a semitone last"
    assert pg.get_attribute("#fsEar", "data-pass") == "1" and next_off(pg), "the honour tick is still needed"
    pg.check('[data-ftick="4"]')
    assert "I can hear and match all six open strings" in pg.inner_text("#v-first-steps")
    assert not next_off(pg) and state(pg)["fs"]["done"] == [1, 2, 3, 4] and state(pg)["fs"]["ear"] is True
    assert not pg.errors


TURN = re.compile(r"\b(turn|tighten|loosen|tune up|twist|wind)\w*\b", re.I)


def test_step_4_no_tuning_instruction_outside_the_home_box(app):
    """Booklet amendment: the teacher tunes the class set, so students are told to turn a machine head only in 'Your own guitar at home'."""
    pg = fresh(app, [1, 2, 3])
    home = pg.inner_text("#fsHome")
    assert home.startswith("Your own guitar at home") and "clip" in home.lower() and "slowly" in home and "from below" in home and TURN.search(home)
    rest = pg.evaluate("()=>{const c=document.getElementById('v-first-steps').cloneNode(true);c.querySelector('#fsHome').remove();return c.textContent}")
    assert not TURN.search(rest), TURN.search(rest)
    assert "your teacher tunes the class guitars" in rest and "Leave the machine heads alone" in rest
    assert "loo" in rest and "hum" in rest.lower() and "Sing it first" in rest and "octave higher than it sounds" in rest
    for n in (1, 2, 3):  # and nowhere in the earlier steps either
        pg.click(f'[data-fgo="{n}"]')
        assert not TURN.search(pg.inner_text("#v-first-steps .fst-body")), n
    assert not pg.errors
