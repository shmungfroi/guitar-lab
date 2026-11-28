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


def fresh(app, done=(), extra=None, **kw):
    """A student part-way through First Steps: the steps in done are passed."""
    return app(state=dict(extra or {}, fs={"done": list(done), "complete": False, "placed": False}), returning=False, **kw)


def ask(pg):
    return pg.get_attribute("#fsQuiz", "data-ask")


def expected(pg):
    """Work the right answer out from what is asked and from the app's chord data, never from the page's own marking."""
    a = ask(pg).split(":")
    if a[0] == "part":
        return a[1]
    if a[0] == "lit":  # the part lit on the approved drawing
        lit = pg.evaluate("()=>[...document.querySelectorAll('#v-first-steps .fst-plates [data-part].hl')].map(g=>g.dataset.part)")
        assert len(lit) == 1, lit
        return lit[0]
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


def tap_part(pg, part):
    """Tap a part on the approved drawing through its own hit area (data-part > .hit), on whichever guitar has it."""
    pg.locator(f'#v-first-steps .fst-plates [data-part="{part}"] .hit').first.dispatch_event("click")


def give(pg, val):
    if ask(pg).startswith("part:"):
        tap_part(pg, val)
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

ART_IDS = {"acoustic": sorted(set(PARTS) - {"pickups"}), "electric": sorted(set(PARTS) - {"soundHole"} | {"controls", "outputJack"})}
PLATES_JS = "()=>[...document.querySelectorAll('#v-first-steps .fst-plates svg.ga')].map(s=>({label:s.getAttribute('aria-label'),parts:[...new Set([...s.querySelectorAll('[data-part]')].map(g=>g.dataset.part))].sort(),strings:[...new Set([...s.querySelectorAll('[data-string]')].map(g=>g.dataset.string))].sort(),tags:[...s.querySelectorAll('.tag')].map(t=>t.dataset.for),lit:[...s.querySelectorAll('[data-part].hl')].map(g=>g.dataset.part)}))"


def test_F2_F4_step_1_tap_quiz_gates_next(app):
    pg = app(returning=False)
    assert next_off(pg)
    ac, el = pg.evaluate(PLATES_JS)
    assert "acoustic" in ac["label"] and "electric" in el["label"]
    assert ac["parts"] == ART_IDS["acoustic"] and el["parts"] == ART_IDS["electric"] and ac["strings"] == el["strings"] == list("123456")
    assert sorted(ac["tags"]) == ART_IDS["acoustic"] and sorted(el["tags"]) == ART_IDS["electric"], "the drawing's own labels are on while learning"
    # learning: tap a part on the drawing, or its name, and it lights up on both guitars with its number and what it does
    tap_part(pg, "nut")
    assert pg.inner_text("#fsCap").startswith("3 · Nut") and [p["lit"] for p in pg.evaluate(PLATES_JS)] == [["nut"], ["nut"]]
    names = pg.evaluate("()=>[...document.querySelectorAll('.fst-names [data-fname]')].map(b=>b.dataset.fname)")
    assert names == PARTS + ["controls", "outputJack"]
    pg.click('[data-fname="saddle"]')
    assert pg.inner_text("#fsCap").startswith("12 · Saddle") and pg.get_attribute('[data-fname="saddle"]', "aria-pressed") == "true"
    pg.click('[data-fname="controls"]')
    assert pg.inner_text("#fsCap").startswith("14 · Controls") and [p["lit"] for p in pg.evaluate(PLATES_JS)] == [[], ["controls"]]
    pg.click("#fsQuizGo")
    plates = pg.evaluate(PLATES_JS)
    assert len(plates) == 2 and all(p["tags"] == [] and p["lit"] == [] for p in plates), "labels are hidden during the check"
    assert pg.locator(".fst-names").count() == 0 and pg.locator("#fsCap").count() == 0
    # a wrong tap says what it was, does not pass, and the same part is still being asked
    want = expected(pg)
    wrong = next(p for p in PARTS if p != want and p not in ("pickups", "soundHole"))
    give(pg, wrong)
    assert "You tapped" in pg.inner_text("#fsFb") and ask(pg) == "part:" + want and "0 of 5" in pg.inner_text("#fsQuiz")
    give(pg, want)
    assert "0 of 5" in pg.inner_text("#fsQuiz"), "a part found on the second go does not count"
    tap_part(pg, "outputJack")
    assert "You tapped the output jack" in pg.inner_text("#fsFb"), "the two extra electric parts can be named but are never asked for"
    pg.click("#fsQuizEnd")
    assert next_off(pg) and "fs" not in state(pg)
    for _ in range(4):  # only the 14 parts on the class word list are asked
        pg.click("#fsQuizGo")
        assert ask(pg)[5:] in PARTS
        pg.click("#fsQuizEnd")
    seen = run_quiz(pg)
    assert len(seen) == 5 and all(s.startswith("part:") and s[5:] in PARTS for s in seen)
    assert not next_off(pg) and state(pg)["fs"]["done"] == [1]
    pg.click("#fsNext")
    assert pg.inner_text("#v-first-steps h2") == TITLES[1]
    assert not pg.errors


def test_F4_phone_quiz_answers_by_name_with_full_size_buttons(app):
    """Under 600 px frets, strings and the saddle are a few pixels wide, so a part is lit and named from buttons instead."""
    pg = app(returning=False, width=360, height=800)
    small = pg.evaluate("()=>[...document.querySelectorAll('.fst-names button')].map(b=>b.getBoundingClientRect().height).filter(h=>h<44)")
    assert not small, "name buttons meet 44 px"
    tap_part(pg, "body")
    assert pg.inner_text("#fsCap").startswith("13 · Body"), "the drawing is still tappable on a phone"
    pg.click("#fsQuizGo")
    for i in range(5):
        assert ask(pg) == "lit" and pg.inner_text("#fsAsk") == "Which part is lit up?"
        plates = pg.evaluate(PLATES_JS)
        assert len(plates) == 1 and plates[0]["tags"] == [] and len(plates[0]["lit"]) == 1
        want = plates[0]["lit"][0]
        assert want in PARTS and want in ART_IDS["electric" if "electric" in plates[0]["label"] else "acoustic"]
        btn = pg.evaluate("()=>[...document.querySelectorAll('#fsQuiz [data-fa]')].map(b=>[b.dataset.fa,b.textContent,b.getBoundingClientRect().height])")
        assert len(btn) == 4 and want in [b[0] for b in btn] and all(b[2] >= 44 for b in btn) and len({b[0] for b in btn}) == 4
        assert not vis(pg, "#fsLitGo"), "no switch to tapping on a phone"
        if i == 0:
            give(pg, next(b[0] for b in btn if b[0] != want))
            assert "It isn't" in pg.inner_text("#fsFb") and not passed_quiz(pg)
            give(pg, expected(pg))
            assert "0 of 5" in pg.inner_text("#fsQuiz")
            want = expected(pg)
        give(pg, want)
    assert passed_quiz(pg) and state(pg)["fs"]["done"] == [1]
    assert not pg.errors


def test_F4_names_are_offered_as_the_keyboard_route_on_wide_screens(app):
    pg = app(returning=False)
    pg.click("#fsQuizGo")
    assert ask(pg).startswith("part:") and pg.inner_text("#fsLitGo") == "Answer with names instead"
    pg.click("#fsLitGo")
    assert ask(pg) == "lit" and pg.inner_text("#fsLitGo") == "Tap the drawing instead"
    for _ in range(5):
        give(pg, expected(pg))
    assert passed_quiz(pg)
    assert not pg.errors


ART_SRC = pathlib.Path("/home/claude/guitar-art/guitar-art.js")
ART_SHA = "cbc52de052080124d13f56412cac9e4c4dec536691fb9e04175087eb60cec4d9"  # the artwork Justin approved on 28 Nov


def test_approved_guitar_art_block_is_present_and_unmodified():
    import hashlib
    src = (pathlib.Path(__file__).resolve().parent.parent / "index.html").read_text(encoding="utf-8")
    a, b = "/* guitar-art: approved by Justin 28 Nov, do not edit */\n", "\n/* end guitar-art */\n"
    assert src.count(a) == 1 and src.count(b) == 1
    block = src[src.index(a) + len(a):src.index(b)]
    assert hashlib.sha256(block.encode("utf-8")).hexdigest() == ART_SHA, "the approved artwork has been edited"
    if ART_SRC.exists():
        assert block == ART_SRC.read_text(encoding="utf-8"), "differs from the approved file"
    assert src.count("guitarArt = (function") == 1 and "function guitarArt" not in src, "one drawing only: the placeholder is gone"
    assert not re.search(r"\.ga[ .{][^}]*\{", src.replace(block, "")), "the app must not restyle the artwork"


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
    # the close-up of the approved drawing: string 6 on the left, and the buttons under the text run 6 to 1 with their letters
    xs = pg.evaluate("()=>[6,5,4,3,2,1].map(n=>{const r=document.querySelector('.fst-strz [data-string=\"'+n+'\"]').getBoundingClientRect();return r.left+r.width/2})")
    assert xs == sorted(xs) and xs[0] < xs[5], "string 6 is drawn on the left"
    assert "String 6, the thickest, is on the left" in pg.inner_text(".fst-strcap")
    assert pg.evaluate("()=>[...document.querySelectorAll('[data-fpl]')].map(b=>b.textContent)") == ["6 · E", "5 · A", "4 · D", "3 · G", "2 · B", "1 · E"]
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
            assert pg.evaluate("()=>[...document.querySelectorAll('.fst-strz [data-string].hl')].map(p=>p.dataset.string)") == [str(n)]
            assert pg.locator(".fst-strcap").count() == 0 and pg.locator(".fst-strz .tag").count() == 0, "no labels while a string is being asked"
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
    pg.locator('.fst-strz [data-string="1"] .hit').first.dispatch_event("click")
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


# ===================================================================== F7 chord diagrams

# Reads a chord box as it is DRAWN: finger dots (string, fret, finger number), open circles and crosses, by position in the SVG.
BOX_JS = r"""sel=>{const svg=document.querySelector(sel);if(!svg)return null;const str=x=>6-Math.round((x-12)/13.2),out={name:svg.querySelector('text').textContent,dots:{},open:[],mute:[]};
 svg.querySelectorAll('circle').forEach(c=>{const r=+c.getAttribute('r'),n=str(+c.getAttribute('cx'));if(r<4)out.open.push(n);else{const fret=Math.round((+c.getAttribute('cy')-26)/17+.5);
   const t=[...svg.querySelectorAll('text')].find(t=>Math.abs(+t.getAttribute('x')-+c.getAttribute('cx'))<.1&&Math.abs(+t.getAttribute('y')-+c.getAttribute('cy'))<6);out.dots[n]=[fret,t?t.textContent:'']}});
 svg.querySelectorAll('text').forEach(t=>{if(t.textContent==='×')out.mute.push(str(+t.getAttribute('x')))});
 const lines=[...svg.querySelectorAll('line')].filter(l=>l.getAttribute('x1')===l.getAttribute('x2')).map(l=>[+l.getAttribute('x1'),parseFloat(l.getAttribute('stroke-width'))]).sort((a,b)=>a[0]-b[0]);
 out.thickLeft=lines[0][1]>lines[5][1];out.nut=!!svg.querySelector('rect[height="3.5"]');out.open.sort((a,b)=>b-a);out.mute.sort((a,b)=>b-a);return out}"""


def from_drawing(pg, d):
    a = ask(pg).split(":")
    if a[0] == "dia-finger":
        return d["dots"][a[2]][1]
    if a[0] == "dia-fret":
        return str(d["dots"][a[2]][0])
    return ",".join(str(n) for n in d["open" if a[0] == "dia-open" else "mute"])


def test_F2_F3_F7_diagram_quiz_answers_match_the_drawn_diagram(app):
    pg = fresh(app, [1, 2, 3, 4])
    assert pg.inner_text("#v-first-steps h2") == TITLES[4] and next_off(pg)
    body = pg.inner_text("#v-first-steps .fst-body")
    for w in ("String 6, low E, is on the left", "thick line at the top is the nut", "1 index, 2 middle, 3 ring, 4 little", "T means thumb", "play it open", "don't play it"):
        assert w in body, w
    a = pg.evaluate(BOX_JS, ".fst-fig .cb svg")
    assert a["name"] == "A" and a["thickLeft"] and a["nut"] and a["mute"] == [6] and a["open"] == [5, 1] and a["dots"] == {"4": [2, "1"], "3": [2, "2"], "2": [2, "3"]}
    assert "string 6 has a ×" in body and "Strings 5 and 1 are open" in body and "Fingers 1, 2 and 3 sit side by side at fret 2, on strings 4, 3 and 2" in body
    pg.click("#fsQuizGo")
    kinds, first = [], True
    for _ in range(40):
        if passed_quiz(pg):
            break
        d = pg.evaluate(BOX_JS, ".fst-fig .cb svg")
        assert d["name"] == ask(pg).split(":")[1], "the diagram shown is the one asked about"
        want = from_drawing(pg, d)
        assert want == expected(pg), f"{ask(pg)}: drawing says {want}, chord data says {expected(pg)}"
        kinds.append(ask(pg).split(":")[0])
        if first:
            first = False
            give(pg, next(o for o in options(pg) if o != want))
            assert not passed_quiz(pg) and "0 of 4" in pg.inner_text("#fsQuiz") and pg.inner_text("#fsFb")
            give(pg, want)
            assert "0 of 4" in pg.inner_text("#fsQuiz")
            continue
        give(pg, want)
    assert passed_quiz(pg) and set(kinds) == {"dia-finger", "dia-fret", "dia-open", "dia-mute"} and len(kinds) == 5
    assert state(pg)["fs"]["done"] == [1, 2, 3, 4, 5] and not next_off(pg)
    assert not pg.errors


# ===================================================================== F8 TAB

# Estimates the pitch of a plucked note from its sample data (autocorrelation), so play-back is checked by what would be heard.
PITCH_JS = r"""i=>{const b=window.__aud.starts[i].node.buffer,d=b.getChannelData(0),sr=b.sampleRate,o=4000,N=4096;let best=0,bl=0;
 for(let l=Math.floor(sr/1200);l<Math.floor(sr/60);l++){let s=0,e1=0,e2=0;for(let k=0;k<N;k++){s+=d[o+k]*d[o+k+l];e1+=d[o+k]*d[o+k];e2+=d[o+k+l]*d[o+k+l]}const c=s/Math.sqrt(e1*e2+1e-12);if(c>best+.02){best=c;bl=l}}return sr/bl}"""


def midi_hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def heard(pg, since):
    out = []
    for s in starts(pg)[since:]:
        assert s["kind"] == "buf" and pg.evaluate("e=>window.__audible(window.__aud.starts[e])", s["i"]) > 0
        out.append((s["when"], pg.evaluate(PITCH_JS, s["i"])))
    return out


def close(hz, m):
    return abs(1200 * __import__("math").log2(hz / midi_hz(m))) < 40


def read_tab(pg, sel=".fst-fig .tab"):
    """Reads a TAB as printed: [(string number, fret)] left to right, where the TOP line is string 1."""
    rows = pg.inner_text(sel).strip().split("\n")
    assert len(rows) == 6 and [r[0] for r in rows] == ["e", "B", "G", "D", "A", "E"], rows
    notes = []
    for col in range(2, len(rows[0])):
        hit = [(r + 1, int(rows[r][col])) for r in range(6) if rows[r][col].isdigit()]
        if hit:
            notes.append(hit if len(hit) > 1 else hit[0])
    return notes


def test_F2_F3_F8_tab_quiz_and_playback(app):
    pg = fresh(app, [1, 2, 3, 4, 5])
    assert pg.inner_text("#v-first-steps h2") == TITLES[5] and next_off(pg)
    body = pg.inner_text("#v-first-steps .fst-body")
    for w in ("top line is string 1, high E, the thinnest", "bottom line is string 6, low E, the thickest", "0 means play the string open", "counted from the nut",
              "left to right", "stacked", "a chord", "doesn't show rhythm on its own", "by listening", "staff printed above"):
        assert w in body, w
    # the lesson TAB: the booklet's three notes, then a stacked chord, as printed and as played
    shown = read_tab(pg)
    assert shown[:3] == [(6, 3), (2, 1), (3, 0)] and sorted(shown[3]) == [(1, 0), (2, 0), (3, 0), (4, 2), (5, 2), (6, 0)]
    assert "string 6 at fret 3 is G" in body and "String 2 at fret 1 is C" in body and "String 3 open is G" in body and "E minor" in body
    n = len(starts(pg))
    pg.click(".fst-fig [data-ftab]")
    h = heard(pg, n)
    assert len(h) == 9 and close(h[0][1], 43) and close(h[1][1], 60) and close(h[2][1], 55), h  # G2, C4, G3
    assert h[0][0] < h[1][0] < h[2][0] < h[3][0] and sorted(round(x[1]) for x in h[3:]) == sorted(round(pg.evaluate(PITCH_JS, s["i"])) for s in starts(pg)[n + 3:])
    for (_, hz), m in zip(sorted(h[3:], key=lambda x: x[1]), [40, 47, 52, 55, 59, 64]):  # E minor, low to high
        assert close(hz, m), (hz, m)
    pg.click("#fsQuizGo")
    first, asked = True, 0
    for _ in range(30):
        if passed_quiz(pg):
            break
        i = int(ask(pg).split(":")[1])
        printed = read_tab(pg)
        assert len(printed) == 3
        want = f"{printed[i][0]}:{printed[i][1]}"
        assert want == expected(pg), "the answer is the note as printed, counting the top line as string 1"
        assert ["first", "second", "third"][i] in pg.inner_text("#fsAsk")
        asked += 1
        if first:
            first = False
            s, f = printed[i]
            give(pg, f"{7 - s}:{f}")  # the classic slip: reading the TAB upside down
            assert "top line is string 1 and the bottom line is string 6" in pg.inner_text("#fsFb") and not passed_quiz(pg)
            give(pg, want)
            continue
        # play-back sounds the printed notes: open string pitch plus the fret
        k = len(starts(pg))
        pg.click(".fst-fig [data-ftab]")
        h = heard(pg, k)
        assert len(h) == 3 and all(close(hz, OPEN[6 - s] + f) for (_, hz), (s, f) in zip(h, printed)), (h, printed)
        give(pg, want)
    assert passed_quiz(pg) and asked == 4 and state(pg)["fs"]["done"] == [1, 2, 3, 4, 5, 6] and not next_off(pg)
    assert not pg.errors


# ===================================================================== F9, F10 first sound and the Path

def test_F9_em_diagram_matches_the_apps_em_box(app):
    pg = fresh(app, [1, 2, 3, 4, 5, 6])
    assert pg.inner_text("#v-first-steps h2") == TITLES[6]
    em = pg.evaluate(BOX_JS, ".fst-fig .cb svg")
    f, g = CH["Em"]["f"], CH["Em"]["g"]
    assert f == "022000" and em["name"] == "Em" and em["mute"] == [] and em["open"] == [6, 3, 2, 1]
    assert em["dots"] == {str(6 - i): [int(f[i]), g[i]] for i in range(6) if f[i] not in "0x"} == {"5": [2, "2"], "4": [2, "3"]}
    body = pg.inner_text("#v-first-steps .fst-body")
    assert "Finger 2 goes on string 5, the A string, at fret 2" in body and "Finger 3 goes on string 4, the D string, at fret 2" in body and "Sing it first" in body
    path = app(state={"stage": "beyond"})
    there = path.evaluate(BOX_JS, '#stage .cb[data-strum="Em"] svg')
    assert there["dots"] == em["dots"] and there["open"] == em["open"] and there["mute"] == em["mute"], "same shape as the Path's Em box"
    n = len(starts(pg))
    pg.click('.fst-fig .cb[data-strum="Em"]')
    assert sorted(round(hz) for _, hz in heard(pg, n)) == sorted(round(hz) for hz in [pg.evaluate(PITCH_JS, s["i"]) for s in starts(pg)[n:]]) and len(starts(pg)) == n + 6
    # three notes on string 1: E, F, G
    assert read_tab(pg) == [(1, 0), (1, 1), (1, 3)]
    assert "open, fret 1, fret 3" in body and "E, F and G" in body and "mi, fa and so in C major" in body and "finger 1 for F and finger 3 for G" in body
    n = len(starts(pg))
    pg.click(".fst-fig [data-ftab]")
    h = heard(pg, n)
    assert len(h) == 3 and close(h[0][1], 64) and close(h[1][1], 65) and close(h[2][1], 67)
    assert not pg.errors and not path.errors


def test_F2_F10_finishing_step_7_opens_the_path_at_stage_1(app):
    pg = fresh(app, [1, 2, 3, 4, 5, 6], extra={"bpm": 200})
    assert pg.is_disabled("#fsStart")
    n = len(starts(pg))
    pg.click("#fsBand")
    pg.wait_for_function("()=>document.getElementById('fsBand').textContent==='Stop'")
    pg.wait_for_timeout(3200)
    band = starts(pg)[n:]
    assert len([s for s in band if s["kind"] == "osc"]) >= 6 and len([s for s in band if s["kind"] == "buf"]) >= 6, "the band counts in and plays"
    em = [pg.evaluate(PITCH_JS, s["i"]) for s in band if s["kind"] == "buf" and s["dur"] > 2]
    assert em and all(any(close(hz, m) for m in (40, 47, 52, 55, 59, 64)) for hz in em), em  # only the six notes of the Em shape
    pg.click("#fsBand")
    assert pg.inner_text("#fsBand") == "Play with the band"
    m = len(starts(pg))
    pg.wait_for_timeout(600)
    assert len(starts(pg)) == m, "the band stops"
    pg.check('[data-ftick="7"]')
    assert not pg.is_disabled("#fsStart") and pg.inner_text("#fsStart") == "Start the Path"
    pg.click("#fsStart")
    pg.wait_for_selector("#stage h2")
    assert views(pg) == ["v-path"] and tabs(pg) == ["Path", "Record"]
    assert pg.inner_text("#stage h2") == "A and E" and pg.get_attribute('[data-st="a-e"]', "aria-current") == "step"
    note = pg.inner_text("#tabNote")
    assert "The Path is open:" in note and "Record is open:" in note
    fs = state(pg)["fs"]
    assert fs["complete"] is True and fs["done"] == [1, 2, 3, 4, 5, 6, 7] and fs["placed"] is False
    assert vis(pg, "[data-inst]") and vis(pg, "#finishes") and vis(pg, ".mbar"), "the full app is back"
    # revisiting from the Path loses nothing
    pg.click("#fsLink")
    pg.wait_for_selector("#v-first-steps h2")
    assert views(pg) == ["v-first-steps"] and tabs(pg) == ["Path", "Record"] and not next_off(pg)
    pg.click('[data-fgo="7"]')
    assert pg.inner_text("#fsStart") == "Back to the Path"
    pg.click("#fsStart")
    pg.wait_for_selector("#stage h2")
    assert state(pg)["fs"] == fs and views(pg) == ["v-path"]
    assert not pg.errors


def test_F10_steps_are_taken_in_order(app):
    pg = fresh(app, [1, 2, 4, 5, 6])
    assert pg.inner_text("#v-first-steps h2") == TITLES[2], "opens at the first step not yet passed"
    assert not pg.is_disabled('[data-fgo="4"]'), "a passed step can be revisited"
    assert pg.is_disabled('[data-fgo="7"]') and next_off(pg), "step 7 waits for step 3"
    assert not pg.errors


# ===================================================================== F11 placement

def place(pg, wrong_at=()):
    pg.click("#fsPlaceGo")
    steps = []
    for i in range(8):
        assert pg.get_attribute("#fsQuiz", "data-place") == str(i)
        a = ask(pg)
        steps.append({"part": 1, "lit": 1, "str-hl": 3, "str-num": 3, "str-name": 3, "dia-finger": 5, "dia-fret": 5, "dia-open": 5, "dia-mute": 5, "tab": 6}[a.split(":")[0]])
        want = expected(pg)
        give(pg, next(o for o in options(pg) if o != want) if i in wrong_at else want)
    return steps


def test_F11_placement_all_correct_skips_first_steps(app):
    pg = app(returning=False)
    steps = place(pg)
    assert steps == [1, 1, 3, 3, 5, 5, 6, 6], "eight items, two each from steps 1, 3, 5 and 6"
    pg.wait_for_selector("#stage h2")
    assert views(pg) == ["v-path"] and tabs(pg) == ["Path", "Record"] and pg.inner_text("#stage h2") == "A and E"
    fs = state(pg)["fs"]
    assert fs["complete"] is True and fs["placed"] is True and fs["done"] == [1, 2, 3, 4, 5, 6, 7]
    assert not pg.errors


@pytest.mark.parametrize("wrong_at,miss", [((6,), [6]), ((0, 4), [1, 5]), ((3,), [3])], ids=["tab", "part-and-diagram", "strings"])
def test_F11_placement_wrong_answer_routes_to_the_right_step(app, wrong_at, miss):
    pg = app(returning=False)
    place(pg, wrong_at)
    assert pg.get_attribute("#fsPlace", "data-miss") == ",".join(map(str, miss))
    txt = pg.inner_text("#v-first-steps")
    assert f"{8 - len(wrong_at)} of 8 right" in txt and all(f"Step {n}: {TITLES[n - 1]}" in txt for n in miss)
    assert all(f"Step {n}:" not in txt for n in range(1, 8) if n not in miss)
    fs = state(pg)["fs"]
    assert fs["complete"] is False and fs["placed"] is False and fs["done"] == [n for n in range(1, 8) if n not in miss]
    assert pg.inner_text("#fsPlaceOpen") == f"Open step {miss[0]}"
    pg.click("#fsPlaceOpen")
    assert views(pg) == ["v-first-steps"] and pg.inner_text("#v-first-steps h2") == TITLES[miss[0] - 1] and next_off(pg)
    for n in miss:  # pass what was missed, then the Path can be started
        pg.click(f'[data-fgo="{n}"]')
        run_quiz(pg)
    pg.click('[data-fgo="7"]')
    pg.click("#fsStart")
    pg.wait_for_selector("#stage h2")
    assert views(pg) == ["v-path"] and state(pg)["fs"]["complete"] is True
    assert not pg.errors


def test_F11_placement_can_be_left(app):
    pg = app(returning=False)
    pg.click("#fsPlaceGo")
    pg.click("#fsPlaceQuit")
    assert pg.inner_text("#v-first-steps h2") == TITLES[0] and raw(pg) is None
    assert not pg.errors


# ===================================================================== F14 saving, backups, older saves

OLD = {"finish": "rock", "stage": "c-g-f", "lv": {"a-e:0": 2, "a-e:1": 3, "c-g-f@keys:0": 1}, "marks": {"a-e:0": 2}, "bpm": 96, "inst": "guitar",
       "journal": [{"d": 1764200000000, "st": "a-e", "inst": "guitar", "h": "Heard it", "o": "Played it", "w": "Wrote it"}], "gates": {}, "warm": {}}
CLIP_JS = "()=>{window.__clip=null;Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:t=>{window.__clip=t;return Promise.resolve()}}})}"


def backup_of(pg):
    go(pg, "record")
    pg.evaluate(CLIP_JS)
    pg.click("#bkCopy")
    pg.wait_for_function("()=>window.__clip")
    return json.loads(pg.evaluate("()=>window.__clip"))


def bring_back(pg, txt):
    pg.fill("#bkIn", txt)
    pg.click("#bkImport")
    pg.click("#bkYes")


def test_F14_fs_is_saved_survives_reload_and_is_in_backups(app):
    pg = app(returning=False)
    run_quiz(pg)
    pg.click("#fsNext")
    pg.check('[data-ftick="2"]')
    saved = state(pg)
    assert saved["fs"] == {"done": [1, 2], "complete": False, "placed": False}
    assert set(saved) - {"fs"} == set(D_KEYS), "the save gains fs and nothing else"
    pg.reload()
    pg.wait_for_selector("#v-first-steps h2")
    assert views(pg) == ["v-first-steps"] and pg.inner_text("#v-first-steps h2") == TITLES[2], "picks up at the first step not yet passed"
    assert state(pg) == saved
    done = app(state={"fs": dict(DONE, line="Eels Always Dance Gently Before Eating", seen=["path", "record"], ear=True), "lv": STAGE1})
    out = backup_of(done)
    assert out["version"] == "0.11" and out["format"] == 1 and {k: out["state"]["fs"][k] for k in state(done)["fs"] if k != "seen"} == {k: v for k, v in state(done)["fs"].items() if k != "seen"}
    assert out["state"]["fs"]["done"] == [1, 2, 3, 4, 5, 6, 7] and out["state"]["fs"]["line"].startswith("Eels")
    # that backup, brought back on a first visit through the link on step 1
    new = app(returning=False)
    new.click('#v-first-steps a[href="#record"]')
    new.wait_for_selector("#bkIn")
    assert views(new) == ["v-record"] and tabs(new) == ["First Steps", "Record"]
    bring_back(new, json.dumps(out))
    assert "Backup imported" in new.inner_text("#bkMsg") and state(new)["fs"] == out["state"]["fs"]
    assert tabs(new) == ["Path", "Warm-up", "Rudiments", "Record"]
    assert not pg.errors and not done.errors and not new.errors


D_KEYS = ["finish", "stage", "nsw", "teacher", "lv", "sign", "marks", "changes", "journal", "bpm", "useFin", "gates", "warm", "best", "capo", "mute", "inst", "gig"]


@pytest.mark.parametrize("wrap", ["0.7", "0.8", "0.9", None], ids=["0.7", "0.8", "0.9", "bare-state"])
def test_F14_older_backups_and_bare_state_still_import(app, wrap):
    pg = app(returning=False, hash_="record")
    assert views(pg) == ["v-record"]
    bring_back(pg, json.dumps(OLD if wrap is None else {"app": "The Guitar Lab", "format": 1, "version": wrap, "saved": "2026-11-20T03:00:00.000Z", "state": OLD}))
    assert "Backup imported" in pg.inner_text("#bkMsg")
    got = state(pg)
    assert "fs" not in got and all(got[k] == v for k, v in OLD.items()), "an older backup comes back exactly, with nothing added"
    assert tabs(pg) == ALL_TABS, "and its owner keeps every tab"
    go(pg, "path")
    assert views(pg) == ["v-path"] and pg.inner_text("#stage h2") == "C, G and the small F"
    assert not pg.errors


def test_F14_importing_an_empty_old_backup_starts_first_steps(app):
    pg = app(state={"fs": DONE, "lv": STAGE1}, hash_="record")
    bring_back(pg, json.dumps({"app": "The Guitar Lab", "format": 1, "version": "0.9", "state": {"bpm": 80, "lv": {}}}))
    # the student is on Record, which stays open by name so a different backup can be tried; everything else is First Steps again
    assert views(pg) == ["v-record"] and tabs(pg) == ["First Steps", "Record"] and "fs" not in state(pg)
    go(pg, "path")
    assert views(pg) == ["v-first-steps"] and tabs(pg) == ["First Steps"]
    assert not pg.errors


@pytest.mark.parametrize("bad", [[1, 2], "done", {"done": "all", "complete": "yes"}, {"done": [0, 9, 2, 2, "3"], "seen": [1, "gig"], "line": 5}])
def test_F14_odd_fs_values_load_safely(app, bad):
    pg = app(state={"fs": bad}, returning=False)
    assert views(pg) == ["v-first-steps"]
    if isinstance(bad, dict) and isinstance(bad.get("done"), list):
        assert pg.inner_text("#v-first-steps h2") == TITLES[0] and pg.get_attribute('[data-fgo="2"]', "class") == "dn"
    assert not pg.errors


# ===================================================================== unchanged once open

def test_path_gig_and_record_are_as_0_9_once_open(browser, tmp_path):
    """Hard constraint: for a returning guitar student the Path, Gig and Record are 0.9's, apart from the version and the First Steps link."""
    import uihelp
    root = pathlib.Path(__file__).resolve().parent.parent
    old = subprocess.run(["git", "show", "90719f9:index.html"], cwd=root, capture_output=True)
    if old.returncode:
        pytest.skip("0.9 (90719f9) is not in this clone")
    (tmp_path / "index.html").write_bytes(old.stdout)
    (tmp_path / "fonts").symlink_to(root / "fonts")
    seed = {"lv": {**STAGE1, "twelve-bar:0": 1}, "gates": {"a-e": 1764200000000}, "journal": OLD["journal"]}
    grab = r"""()=>{const o={};for(const id of ['next','neck','stage','side','v-gig','v-record']){const e=document.getElementById(id).cloneNode(true);e.querySelectorAll('#fsLink').forEach(x=>x.remove());o[id]=e.innerHTML}return o}"""
    got = {}
    for name, url in (("old", (tmp_path / "index.html").as_uri()), ("new", uihelp.URL)):
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        pg = ctx.new_page()
        pg.clock.install(time=1764300000000)
        pg.goto(url + "#__seed")
        pg.evaluate("s=>localStorage.setItem('shredder',s)", json.dumps(seed))
        got[name] = {}
        for h in ("a-e", "twelve-bar", "hallelujah", "gig", "record"):
            pg.goto("about:blank")
            pg.goto(url + "#" + h)
            pg.wait_for_selector("#tabs a[aria-current=page]", state="attached")
            got[name][h] = pg.evaluate(grab)
        got[name]["tabs"] = tabs(pg)
        ctx.close()
    assert got["new"]["tabs"] == got["old"]["tabs"] == ALL_TABS
    for h in got["old"]:
        if h != "tabs":
            for part in got["old"][h]:
                assert got["new"][h][part] == got["old"][h][part], f"#{h} {part} differs from 0.9"


# ===================================================================== F16 layout, F17 design

def _walk(pg, problems, where):
    for p in pg.evaluate(OVERFLOW_JS):
        problems.append(f"{where}: overflow {p}")
    small = pg.evaluate("""()=>[...document.querySelectorAll('#v-first-steps button, #v-first-steps a.lk')].filter(e=>e.getClientRects().length).map(e=>{const r=e.getBoundingClientRect();return [e.id||e.textContent.trim().slice(0,20),Math.round(Math.min(r.width,r.height))]}).filter(x=>x[1]<40)""")
    for s in small:
        problems.append(f"{where}: tap target {s}")
    tiny = pg.evaluate("""()=>[...document.querySelectorAll('#v-first-steps text')].filter(t=>t.getClientRects().length).map(t=>[t.textContent,Math.round(parseFloat(getComputedStyle(t).fontSize)*t.getBoundingClientRect().height/Math.max(1,t.getBBox().height)*10)/10]).filter(x=>x[1]<11.5)""")
    for s in tiny[:3]:
        problems.append(f"{where}: drawing text under 12px {s}")


@pytest.mark.parametrize("scheme", ["dark", "light"])
@pytest.mark.parametrize("width", [360, 1280])
def test_F16_every_step_fits_with_no_console_errors(app, width, scheme):
    pg = fresh(app, [1, 2, 3, 4, 5, 6], width=width, height=800, scheme=scheme)
    lum = sum(int(x) for x in re.findall(r"\d+", pg.evaluate("()=>getComputedStyle(document.body).backgroundColor"))[:3])
    assert (lum > 600) if scheme == "light" else (lum < 120)
    problems = []
    for n in range(1, 8):
        pg.click(f'[data-fgo="{n}"]')
        assert pg.inner_text("#v-first-steps h2") == TITLES[n - 1]
        _walk(pg, problems, f"step {n}")
        if pg.locator("#fsQuizGo").count():
            pg.click("#fsQuizGo")
            _walk(pg, problems, f"step {n} check")
            give(pg, next(o for o in options(pg) if o != expected(pg)))
            _walk(pg, problems, f"step {n} check, after a miss")
            pg.click("#fsQuizEnd")
    pg.click('[data-fgo="1"]')
    pg.click("#fsPlaceGo")
    for i in range(8):
        _walk(pg, problems, f"placement {i + 1}")
        give(pg, expected(pg) if i else next(o for o in options(pg) if o != expected(pg)))
    _walk(pg, problems, "placement result")
    if width == 1280:  # the drawing sits beside the words
        pg.click("#fsPlaceOpen")
        box = pg.evaluate("()=>['.fst-fig','.fst-body'].map(s=>{const r=document.querySelector(s).getBoundingClientRect();return [r.left,r.right,r.top]})")
        assert box[0][1] <= box[1][0] and abs(box[0][2] - box[1][2]) < 80, box
    else:  # the drawing sits on top
        pg.click("#fsPlaceOpen")
        box = pg.evaluate("()=>['.fst-fig','.fst-body'].map(s=>{const r=document.querySelector(s).getBoundingClientRect();return [r.top,r.bottom]})")
        assert box[0][1] <= box[1][0] + 1, box
    assert not problems and not pg.errors, "\n".join(problems + pg.errors)


def test_F16_no_popups_network_or_new_storage_keys():
    src = (pathlib.Path(__file__).resolve().parent.parent / "index.html").read_text(encoding="utf-8")
    assert not re.search(r"\b(alert|confirm|prompt)\s*\(", src)
    assert {m[1] for m in re.findall(r"localStorage\.(get|set|remove)Item\('([^']+)'", src)} == {"shredder"} and "localStorage.clear" not in src
    assert not re.search(r"\b(fetch|XMLHttpRequest|WebSocket|sendBeacon|importScripts)\b", src) and not re.search(r"<script[^>]+src=|<link[^>]+href=", src)
    for token, dark, light in (("--ton", "#8fbf6a", "#4a7434"), ("--pre", "#c9a24a", "#8a6a22"), ("--dom", "#d0574b", "#a8352b"), ("--sec", "#a493d8", "#6b55b0"), ("--sub", "#b3a98f", "#5e5340")):
        assert f"{token}:{dark}" in src and f"{token}:light-dark({light},{dark})" in src, token + " changed"
    fs_css = src[src.index("/* First Steps (0.11)"):src.index("@media(prefers-reduced-motion")]
    assert not re.search(r"--(ton|pre|dom|sec|sub)\b", fs_css), "function colours are for harmony, not for First Steps' interface"


SKILL = pathlib.Path("/root/.claude/skills/synced/f1b3e4ab-b47d-4f75-b27e-08d2e93f882c_202e44b6-919b-40e3-8017-b3049067e2b4/shmungfroi-design/scripts/check_design.py")
# The one FAIL the checker already gives 0.9 (main 90719f9): the whole app has no number-diamond trace yet. That is an app-wide
# restyle outside this spec, listed in BUILD_REPORT.md for Justin; First Steps must add no FAIL of its own.
KNOWN_FAIL = {"Number-diamond trace"}


def test_F17_design_checker_has_no_new_fail():
    if not SKILL.exists():
        pytest.skip("shmungfroi-design skill is not installed here")
    index = pathlib.Path(__file__).resolve().parent.parent / "index.html"
    out = subprocess.run([sys.executable, str(SKILL), str(index), "--lab", "guitar"], capture_output=True, text=True).stdout
    fails = [l.split("|")[2].strip() for l in out.splitlines() if l.startswith("| FAIL")]
    assert "PASS" in out and set(fails) <= KNOWN_FAIL, out


# ===================================================================== FS facts (independent music/guitar fact check, 28 Nov)
# Data tests: they read First Steps' own tables and question builders straight out of index.html (through appdata's
# hook) and compare them with an answer key written here from standard guitar practice, not from the app.

FS_HZ = {6: 82.41, 5: 110.00, 4: 146.83, 3: 196.00, 2: 246.94, 1: 329.63}  # E2 A2 D3 G3 B3 E4, A4 = 440
FS_NAMES = {6: "E", 5: "A", 4: "D", 3: "G", 2: "B", 1: "E"}
NOTE = ["C", "D♭", "D", "E♭", "E", "F", "F♯", "G", "A♭", "A", "B♭", "B"]
# standard open shapes, written string 6 to string 1: frets and fingers
SHAPES = {"A": ("x02220", "001230"), "D": ("xx0232", "000132"), "Em": ("022000", "023000"),
          "Am": ("x02210", "002310"), "C": ("x32010", "032010")}


@pytest.fixture(scope="module")
def fsx(browser, tmp_path_factory):
    """Evaluate an expression inside the app's own script scope. Audio starts are recorded, as in uihelp."""
    import uihelp
    td = tmp_path_factory.mktemp("fsfacts")
    (td / "index.html").write_text(appdata.hooked_html(), encoding="utf-8")
    (td / "fonts").symlink_to(appdata.INDEX.parent / "fonts")
    ctx = browser.new_context()
    ctx.add_init_script(uihelp.AUDIO_JS)
    pg = ctx.new_page()
    pg.goto((td / "index.html").as_uri())
    pg.wait_for_function("()=>typeof globalThis.__APP==='function'")
    yield lambda js: pg.evaluate("j=>__APP(j)", js), pg
    ctx.close()


def test_FS_facts_open_string_pitches_and_reference_tones(fsx):
    ev, pg = fsx
    assert ev("OPEN") == [40, 45, 50, 55, 59, 64], "E2 A2 D3 G3 B3 E4"
    for n, hz in FS_HZ.items():
        m = ev(f"sOpen({n})")
        assert abs(440 * 2 ** ((m - 69) / 12) - hz) < 0.01, (n, m)
    # what step 4's reference buttons actually play: one triangle oscillator at the exact frequency
    for n, hz in FS_HZ.items():
        k = len(pg.evaluate("()=>window.__starts()"))
        ev(f"(fsLoopI=0,fsRef({n}),0)")
        o = [s for s in pg.evaluate("()=>window.__starts()")[k:] if s["kind"] == "osc"]
        assert len(o) == 1 and o[0]["type"] == "triangle" and abs(o[0]["freq"] - hz) < 0.01, (n, o)
    ev("(stopAll(),fsQuiet(),0)")


def test_FS_facts_string_order_and_names(fsx):
    ev, _ = fsx
    assert ev("SLET")[1:] == [FS_NAMES[n] for n in range(1, 7)]
    assert ev("SNAME")[1:] == ["high E", "B", "G", "D", "A", "low E"]
    assert [NOTE[ev(f"sOpen({n})") % 12] for n in range(6, 0, -1)] == list("EADGBE")
    assert ev("sOpen(6)") < ev("sOpen(1)") and ev("sOpen(1)") - ev("sOpen(6)") == 24, "string 6 lowest, string 1 two octaves up"
    b3 = ev("FSV[3]().body")
    for w in ("String 6 is the thickest string and it sounds the lowest. It is called low E.", "String 1 is the thinnest and it sounds the highest",
              "closest to the floor", "E A D G B E", "fret 1 is finger 1, fret 2 is finger 2 and fret 3 is finger 3"):
        assert w in b3, w
    line = re.search(r"Ours, to start you off: ([^.]+)\.", b3).group(1)
    assert "".join(w[0] for w in line.split()) == "EADGBE", line


def test_FS_facts_ear_pairs(fsx):
    ev, _ = fsx
    pairs = ev("EARG")
    assert pairs == [[40, 24], [45, 14], [50, 5], [55, 1]], "E2-E4, A2-B3, D3-G3, G3-G#3"
    for lo, gap in pairs:
        assert lo in ev("OPEN") and gap >= 1
    for i in range(4):
        e = ev(f"fsEarNew({i})")
        assert abs(e["pair"][0] - e["pair"][1]) == pairs[i][1] and min(e["pair"]) == pairs[i][0]
    act = ev("fsAct.toString()")
    assert "const up=fe.pair[1]>fe.pair[0];if((d.ear==='up')===up)" in act, "Higher is right when the second note is higher"


def test_FS_facts_chord_shapes_are_standard(fsx):
    ev, _ = fsx
    for ch, (f, g) in SHAPES.items():
        c = ev(f"CH[{json.dumps(ch)}]")
        assert (c["f"], c["g"]) == (f, g), ch


def test_FS_facts_diagram_answer_keys(fsx):
    ev, _ = fsx
    for ch, (f, g) in SHAPES.items():
        if ch == "Em":
            continue
        fr = {6 - i: (f[i], g[i]) for i in range(6) if f[i] not in "0x"}
        opn = ",".join(str(6 - i) for i in range(6) if f[i] == "0")
        mute = ",".join(str(6 - i) for i in range(6) if f[i] == "x")
        for _ in range(12):
            for kind in ("finger", "fret"):
                q = ev(f"qDia({json.dumps(ch)},'{kind}')")
                n = int(q["ask"].split(":")[2])
                assert q["ans"] == fr[n][1 if kind == "finger" else 0], (ch, kind, n, q["ans"])
                assert q["ans"] in [o[0] for o in q["opts"]]
        qo, qm = ev(f"qDia({json.dumps(ch)},'open')"), ev(f"qDia({json.dumps(ch)},'mute')")
        assert qo["ans"] == opn and qm["ans"] == mute, ch
        assert qo["ans"] in [o[0] for o in qo["opts"]] and qm["ans"] in [o[0] for o in qm["opts"]]
    # the D check: 1 on G, 3 on B, 2 on high E; D open; low E and A not played
    assert {n: SHAPES["D"][1][6 - n] for n in (3, 2, 1)} == {3: "1", 2: "3", 1: "2"}
    b5 = ev("FSV[5]().body")
    assert "string 6 has a ×" in b5 and "Strings 5 and 1 are open" in b5 and "Fingers 1, 2 and 3 sit side by side at fret 2, on strings 4, 3 and 2" in b5


def test_FS_facts_tab_orientation_answer_keys_and_pitches(fsx):
    ev, _ = fsx
    rows = ev("mkTab([[5,3]])").split("\n")
    assert [r[0] for r in rows] == list("eBGDAE") and "3" in rows[0] and "3" not in "".join(rows[1:]), "string 1 (index 5) on the top line"
    # lesson TAB: string 6 fret 3 = G, string 2 fret 1 = C, string 3 open = G, then Em stacked
    t = ev("FS_TAB")
    pit = [ev(f"OPEN[{s}]") + f for s, f in t[:3]]
    assert [6 - s for s, _ in t[:3]] == [6, 2, 3] and [f for _, f in t[:3]] == [3, 1, 0] and [NOTE[p % 12] for p in pit] == ["G", "C", "G"]
    assert pit == [43, 60, 55], "G2, middle C, G3"
    assert "".join(str(f) for _, f in sorted(t[3])) == SHAPES["Em"][0]
    assert ev("evM(FS_TAB[0])") == 43 and ev("evM(FS_TAB[3])") == [40, 47, 52, 55, 59, 64]
    want = [[("B", 5, 2), ("G", 3, 0), ("G", 1, 3)], [("E", 6, 0), ("E", 4, 2), ("D", 2, 3)], [("F", 1, 1), ("C", 5, 3), ("A", 3, 2)]]
    for line, key in zip(ev("QT"), want):
        for i, (name, n, f) in enumerate(key):
            q = ev(f"qTab({json.dumps(line)},{i})")
            assert q["ans"] == f"{n}:{f}" and q["ans"] in [o[0] for o in q["opts"]], (line, i, q["ans"])
            assert NOTE[(ev(f"sOpen({n})") + f) % 12] == name and f"That note is {name}." in q["yes"], (line, i, q["yes"])
    b6 = ev("FSV[6]().body")
    for w in ("The top line is string 1, high E, the thinnest. The bottom line is string 6, low E, the thickest.", "0 means play the string open",
              "counted from the nut, which is 0, towards the bridge", "stacked on top of each other are played together", "TAB doesn't show rhythm",
              "string 6 at fret 3 is G. String 2 at fret 1 is C. String 3 open is G."):
        assert w in b6, w


def test_FS_facts_step_7_em_and_efg(fsx):
    ev, _ = fsx
    efg = ev("FS_EFG")
    assert all(s == 5 for s, _ in efg) and [f for _, f in efg] == [0, 1, 3]
    pit = [ev("OPEN[5]") + f for _, f in efg]
    assert pit == [64, 65, 67] and [NOTE[p % 12] for p in pit] == ["E", "F", "G"]
    assert [(p - 60) % 12 for p in pit] == [4, 5, 7], "mi fa so above do = C"
    b7 = ev("FSV[7]().body")
    assert "Finger 2 goes on string 5, the A string, at fret 2. Finger 3 goes on string 4, the D string, at fret 2." in b7
    assert "E, F and G, which are mi, fa and so in C major" in b7 and "finger 1 for F and finger 3 for G" in b7


def test_FS_facts_parts_and_technique_words(fsx):
    ev, _ = fsx
    fp = {p[0]: p for p in ev("FPART")}
    assert [p[1] for p in ev("FPART")] == ["Headstock", "Machine heads", "Nut", "Neck", "Fingerboard", "Frets", "Position markers", "Body",
                                           "Sound hole", "Pickguard", "Saddle", "Bridge", "Strings", "Pickups"]
    assert "also called the head" in fp["headstock"][3] and "tuning pegs" in fp["machineHeads"][3] and "fretboard" in fp["fingerboard"][3]
    assert "3, 5, 7 and 9" in fp["positionMarkers"][3] and "two dots at fret 12" in fp["positionMarkers"][3]
    assert "set into the bridge" in fp["saddle"][3] and "electric" in fp["pickups"][3]
    b2 = ev("FSV[2]().body")
    assert "T thumb, 1 index, 2 middle, 3 ring, 4 little" in b2
    assert "The square arch means a downstroke: pick towards the floor. The V means an upstroke" in b2 and "down on the beat and up on the “&amp;”" in b2
    assert "just behind the fret wire" in b2
    b4 = ev("FSV[4]().body")
    assert "your teacher tunes the class guitars" in b4 and "written an octave higher than it sounds" in b4
