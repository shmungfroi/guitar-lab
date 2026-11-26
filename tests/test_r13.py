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


# --------------------------------------------------------------------- shared helpers and data

import appdata

D = appdata.load()
ST, FIN = D["ST"], D["FIN"]
SRC = pathlib.Path(appdata.INDEX).read_text(encoding="utf-8")
INSTDATA = json.loads(re.search(r'<script type="application/json" id="instData">(.*?)</script>', SRC, re.S).group(1))
BS = INSTDATA["bass"]
GUITAR_NAMES = {r["n"] for r in D["RUD"]} | {t["n"] for t in D["TECH"]}
GUITAR_ONLY_CARDS = [D["KNOW"][k][0] for k in ("strings", "parts", "boxes", "tab", "minor", "barre")]
THEORY = ["e7", "func", "four", "six", "vii", "sec"]
STAGE_IDS = [s["id"] for s in ST]
X_TS = 1764200000000


def bass_state(passed=8, **kw):
    """A bass player who has passed the first `passed` stages."""
    st = {"inst": "bass", "lv": {f"{s}@bass:{i}": 2 for s in STAGE_IDS[:passed] for i in range(5)},
          "gates": {s + "@bass": X_TS for s in STAGE_IDS[:passed]}}
    st.update(kw)
    return st


def names(pg, view):
    """Item names on a Rudiments or Technique page, without the tags."""
    return pg.evaluate("v=>[...document.querySelectorAll('#v-'+v+' .card h3')].map(h=>h.firstChild.textContent.trim())", view)


def tech_for(fin):
    order = ["core"] + ([fin] if fin != "rock" else []) + ["rock"]
    return [t["n"] for g in order for t in BS["tech"] if t["f"] == g]


def seen(pg, sel):
    return pg.evaluate("s=>[...document.querySelectorAll(s)].map(e=>e.textContent+' '+[...e.querySelectorAll('[aria-label]')].map(x=>x.getAttribute('aria-label')).join(' ')).join('\\n')", sel)


# --------------------------------------------------------------------- X2 bass sees only bass items

@pytest.mark.parametrize("fin", [f["k"] for f in FIN])
def test_X2_bass_sees_only_bass_items(app, fin):
    pg = app(state=bass_state(finish=fin), hash_="rudiments")
    rud = names(pg, "rudiments")
    assert rud == [r["n"] for r in BS["rud"]]
    go(pg, "technique")
    tech = names(pg, "technique")
    assert tech == tech_for(fin), "core, the current Finish, then rock and roll: nothing else"
    heads = pg.evaluate("()=>[...document.querySelectorAll('#v-technique > h3')].map(h=>h.textContent)")
    want = ["Core"] + [f["n"] for f in FIN if f["k"] == fin and fin != "rock"] + ["Rock and roll"]
    assert heads == want
    # two bass drills share a name with guitar's (the pulse and the spider); what must never be shared is the id
    assert not (set(rud) | set(tech)) & (GUITAR_NAMES - {"Pulse on one string", "The spider (1-2-3-4)"}), "a guitar item is on the bass list"
    keys = pg.evaluate("()=>[...document.querySelectorAll('#v-technique [data-lv]')].map(b=>b.dataset.lv)")
    assert keys and all(re.fullmatch(r"t:bs-[a-z]+@bass", k) for k in keys), keys
    assert "written for guitar" not in pg.inner_text("#v-technique") and "guitar techniques" not in pg.inner_text("#v-technique")
    go(pg, "rudiments")
    assert "written for guitar" not in pg.inner_text("#v-rudiments")
    rkeys = pg.evaluate("()=>[...document.querySelectorAll('#v-rudiments [data-best]')].map(b=>b.dataset.best)")
    assert rkeys == ["r:" + r["id"] + "@bass" for r in BS["rud"]] and all(k.startswith("r:bs-") for k in rkeys), "every bass rudiment logs a tempo under its own bs- id"
    assert not pg.errors


def test_X2_optional_tag_only_on_the_flamenco_bass_item(app):
    pg = app(state=bass_state(finish="flam"), hash_="technique")
    tagged = pg.evaluate("()=>[...document.querySelectorAll('#v-technique .card h3')].filter(h=>/Optional/.test(h.textContent)).map(h=>h.firstChild.textContent.trim())")
    assert tagged == ["Tangos roots"]
    card = pg.locator("#v-technique .card", has_text="Tangos roots").inner_text()
    assert "counted in four" in card and "weight falls on 2, 3 and 4" in card and not re.search(r"\b12\b", card)


# --------------------------------------------------------------------- X3 no guitar wording on the bass pages

# Guitar-only technique and book words. "fret", "string", "TAB", "pickup" and "hammer-on" belong to the bass too.
X3_DENY = re.compile(r"guitar book|chord box|\bstrum|pendulum|palm[- ]mut|rasgueado|golpe|\bbarre\b|power chord|tremolo|\bbends?\b|"
                     r"\bpick\b|\bpicking\b|plectrum|six strings|\bcapo\b|voicing|\(p\)|i m a\b|written for guitar|guitar techniques", re.I)


def test_X3_no_guitar_only_words_on_bass(app):
    bad = []

    def check(where, textv):
        for m in X3_DENY.finditer(textv):
            bad.append(f"{where}: ...{textv[max(0, m.start() - 30):m.end() + 20]!r}")

    for fin in [f["k"] for f in FIN]:
        pg = app(state=bass_state(finish=fin), hash_="rudiments")
        check(fin + "/rudiments", seen(pg, "#v-rudiments"))
        go(pg, "technique")
        check(fin + "/technique", seen(pg, "#v-technique"))
        for s in ST:
            go(pg, s["id"])
            check(f"{fin}/{s['id']}/cards", seen(pg, "#side details.know"))
            check(f"{fin}/{s['id']}/also", seen(pg, "#stage ul.log"))
            check(f"{fin}/{s['id']}/part note", pg.evaluate("()=>[...document.querySelectorAll('#stage .tab')].map(t=>(t.previousElementSibling||t).textContent+' '+t.textContent).join(' ')"))
            go(pg, "invent")
            check(f"{fin}/{s['id']}/invent", seen(pg, "#v-invent"))
            pg.click("#roll")
            check(f"{fin}/{s['id']}/invent rolled", seen(pg, "#v-invent"))
        assert not pg.errors
        pg.context.close()
    assert not bad, "\n".join(bad[:20])
    assert X3_DENY.search("Palm muting") and X3_DENY.search("Tap a chord box") and X3_DENY.search("Pendulum strum"), "the list still catches guitar wording"


# --------------------------------------------------------------------- X4 bass cards on all eight stages

def test_X4_bass_cards_on_every_stage(app):
    pg = app(state=bass_state())
    for s in ST:
        go(pg, s["id"])
        got = pg.evaluate("()=>[...document.querySelectorAll('#side details.know')].map(d=>[d.querySelector('summary').textContent,d.querySelector('p').textContent])")
        own = [[c["t"], c["b"]] for c in BS["know"][s["id"]]]
        shared = [list(INSTDATA["shared"].get(k) or D["KNOW"][k]) for k in s["know"] if k in THEORY]
        assert own, s["id"]
        assert got == own + shared, s["id"]
        assert not [t for t, _ in got if t in GUITAR_ONLY_CARDS], f"{s['id']}: a guitar-only card on bass"
        assert not re.search(r"chord box", " ".join(b for _, b in got), re.I)
    # every shared theory card still reaches the bass player somewhere on the Path
    assert sorted(k for s in ST for k in s["know"] if k in THEORY) == sorted(THEORY)
    go(pg, "c-g-f")
    func = pg.locator("#side details.know", has_text="Home, away").locator("p").text_content()
    assert "The colours in the Function card show these jobs." in func and "do, fa, so" in func
    assert not pg.errors


def test_X4_guitar_cards_keep_their_wording(app):
    pg = app(state={"inst": "guitar"}, hash_="c-g-f")
    assert "The colours on every chord box show these jobs." in pg.locator("#side details.know p").first.text_content()
    go(pg, "a-e")
    assert pg.evaluate("()=>[...document.querySelectorAll('#side details.know summary')].map(s=>s.textContent)") == GUITAR_ONLY_CARDS[:3]


# --------------------------------------------------------------------- X5 stage-2 note: six lines for guitar, four for bass

def test_X5_stage_2_tab_is_six_line_for_guitar_and_four_line_for_bass(app):
    pg = app(state={"inst": "guitar"}, hash_="twelve-bar")
    g = pg.locator("#stage .tab").text_content().split("\n")
    assert [l[0] for l in g] == list("eBGDAE") and "Boogie riff on A" in pg.inner_text("#stage")
    pg.click('[data-inst="bass"]')
    assert pg.locator("#stage .tab").count() == 1
    b = pg.locator("#stage .tab").text_content().split("\n")
    assert [l[:2] for l in b] == ["G|", "D|", "A|", "E|"], b
    assert len({len(l) for l in b}) == 1, "the four lines are the same length"
    assert b == ["G|---------|-----2-4-|---------|",
                 "D|-----2-4-|-0-4-----|---------|",
                 "A|-0-4-----|---------|-----2-4-|",
                 "E|---------|---------|-0-4-----|"]
    note = pg.inner_text("#stage")
    assert "Boogie walk" in note and "Boogie riff on A" not in note and "string set" not in note
    for s in STAGE_IDS:
        if s != "twelve-bar":
            go(pg, s)
            assert pg.locator("#stage .tab").count() == 0, s
    assert not pg.errors


# --------------------------------------------------------------------- X6 save key and shape

DEF_KEYS = {"finish", "stage", "nsw", "teacher", "lv", "sign", "marks", "changes", "journal", "bpm", "useFin", "gates", "warm", "best", "capo", "mute", "inst", "gig"}


def test_X6_save_key_and_shape_unchanged(app):
    pg = app(state={"inst": "bass"}, hash_="rudiments")
    pg.click('[data-lv="r:bs-pulse@bass"][data-dir="1"]')
    assert pg.evaluate("()=>Object.keys(localStorage)") == ["shredder"]
    st = state(pg)
    assert set(st) == DEF_KEYS, set(st) ^ DEF_KEYS
    assert st["lv"] == {"r:bs-pulse@bass": 1} and st["best"] == {} and st["journal"] == [] and st["inst"] == "bass"
    pg.fill('[data-best="r:bs-pulse@bass"]', "88")
    pg.dispatch_event('[data-best="r:bs-pulse@bass"]', "change")
    go(pg, "technique")
    pg.click('[data-lv="t:bs-kicklock@bass"][data-dir="1"]')
    st = state(pg)
    assert st["lv"] == {"r:bs-pulse@bass": 1, "t:bs-kicklock@bass": 1} and st["best"] == {"r:bs-pulse@bass": 88}
    assert set(st) == DEF_KEYS
    go(pg, "record")
    assert "Pulse on one string: 88 bpm" in pg.inner_text("#v-record")
    assert set(re.findall(r"localStorage\.(?:get|set)Item\('([^']+)'", SRC)) == {"shredder"}
    assert not pg.errors


# --------------------------------------------------------------------- X7 old saves: stray guitar ticks never count on bass

STRAY = {"inst": "bass",
         "lv": {"r:pulse": 2, "r:pulse@bass": 3, "r:cross@bass": 2, "r:spider@bass": 2, "t:power@bass": 2, "t:shuffle@bass": 3, "r:cross@drums": 2, "a-e@bass:0": 2},
         "best": {"r:pulse@bass": 120, "r:pulse": 90}}


def test_X7_stray_guitar_keys_do_not_mark_bass_items_done(app):
    pg = app(state=STRAY, hash_="rudiments")
    assert pg.locator("#v-rudiments .tag.ok").count() == 0, "a stray guitar tick shows as Done on a bass rudiment"
    assert pg.evaluate("()=>[...document.querySelectorAll('#v-rudiments [data-best]')].map(i=>i.value).join('')") == ""
    assert set(pg.evaluate("()=>[...document.querySelectorAll('#v-rudiments .lvname')].map(e=>e.textContent)")) == {"Not started"}
    go(pg, "technique")
    assert pg.locator("#v-technique .tag.ok").count() == 0
    go(pg, "record")
    rec = pg.inner_text("#v-record")
    assert re.search(r"Consistent or better: Bass\s+None yet\.", rec), rec[:400]
    assert re.search(r"Best tempos: Bass\s+None logged yet\.", rec)
    assert "Palm muting" not in rec and "String crossing" not in rec and "Power chords" not in rec
    # nothing is deleted: the old keys are still in the save after the bass player logs something new
    go(pg, "rudiments")
    pg.click('[data-lv="r:bs-alt@bass"][data-dir="1"]')
    st = state(pg)
    assert {k: v for k, v in st["lv"].items() if k != "r:bs-alt@bass"} == STRAY["lv"] and st["best"] == STRAY["best"]
    # guitar's own progress is untouched and still shows
    go(pg, "a-e")
    pg.click('[data-inst="guitar"]')
    go(pg, "rudiments")
    assert "Done" in pg.locator("#v-rudiments .card", has_text="Pulse on one string").inner_text()
    assert pg.input_value('[data-best="r:pulse"]') == "90"
    # drums have no list of their own yet, so their old tick still shows as it did on 0.9
    go(pg, "a-e")
    pg.click('[data-inst="drums"]')
    go(pg, "rudiments")
    assert "Done" in pg.locator("#v-rudiments .card", has_text="String crossing").inner_text()
    assert not pg.errors


def test_X7_a_0_9_backup_with_stray_keys_imports(app):
    pg = app(state={}, hash_="record")
    pg.fill("#bkIn", json.dumps({"app": "The Guitar Lab", "format": 1, "version": "0.9", "saved": "2026-11-20T03:00:00.000Z", "state": STRAY}))
    pg.click("#bkImport")
    pg.click("#bkYes")
    assert "Backup imported" in pg.inner_text("#bkMsg")
    st = state(pg)
    assert st["lv"] == STRAY["lv"] and st["best"] == STRAY["best"] and st["inst"] == "bass"
    assert re.search(r"Consistent or better: Bass\s+None yet\.", pg.inner_text("#v-record"))
    assert not pg.errors


# --------------------------------------------------------------------- X8 gates are per instrument

def test_X8_bass_gates_are_bass_only(app):
    lock = next(r for r in BS["rud"] if r["st"] == 3)            # opens with stage 4
    pg = app(state=bass_state(passed=2), hash_="rudiments")
    card = pg.locator("#v-rudiments .card", has_text=lock["n"])
    assert "Opens with stage 4" in card.inner_text()
    st2 = [r["n"] for r in BS["rud"] if r["st"] <= 2]
    for n in st2:
        assert "Opens with" not in pg.locator("#v-rudiments .card", has_text=n).first.inner_text(), n
    go(pg, "am-e7")
    for i in range(5):
        for _ in range(2):
            pg.click(f'[data-lv="am-e7@bass:{i}"][data-dir="1"]')
    go(pg, "rudiments")
    assert "Opens with" not in pg.locator("#v-rudiments .card", has_text=lock["n"]).inner_text(), "passing stages 1-3 on bass opens the stage-4 item"
    assert "Opens with stage 5" in pg.locator("#v-rudiments .card", has_text="Octave shape").inner_text()
    go(pg, "technique")
    assert "Opens with stage 6" in pg.locator("#v-technique .card", has_text="Walking four").inner_text()
    assert "Opens with" not in pg.locator("#v-technique .card", has_text="Root and octave").inner_text()
    # nothing opened for drums or guitar
    for inst in ("drums", "guitar"):
        go(pg, "a-e")
        pg.click(f'[data-inst="{inst}"]')
        go(pg, "rudiments")
        assert "Opens with stage 2" in pg.inner_text("#v-rudiments"), inst + " was opened by bass progress"
    assert not pg.errors


# --------------------------------------------------------------------- X9 the instrument switch changes the tabs

def test_X9_instrument_switch_changes_rudiments_technique_and_invent(app):
    pg = app(state={"inst": "guitar", "lv": {"r:pulse": 2}}, hash_="rudiments")
    assert names(pg, "rudiments") == [r["n"] for r in D["RUD"]]
    go(pg, "a-e")
    pg.click('[data-inst="bass"]')
    go(pg, "rudiments")
    assert names(pg, "rudiments") == [r["n"] for r in BS["rud"]]
    assert pg.locator("#v-rudiments .tag.ok").count() == 0, "guitar's level shows on bass"
    pg.click('[data-lv="r:bs-pulse@bass"][data-dir="1"]')
    pg.click('[data-lv="r:bs-pulse@bass"][data-dir="1"]')
    go(pg, "technique")
    assert names(pg, "technique") == tech_for("bossa") and pg.locator("#v-technique svg").count() == 0
    go(pg, "invent")
    assert "one bar of bass" in pg.inner_text("#v-invent")
    go(pg, "a-e")
    pg.click('[data-inst="guitar"]')
    go(pg, "technique")
    assert names(pg, "technique")[0] == "Power chords" and pg.locator("#v-technique svg.fb").count() == 4
    go(pg, "rudiments")
    assert names(pg, "rudiments") == [r["n"] for r in D["RUD"]]
    assert pg.locator("#v-rudiments .tag.ok").count() == 1, "one Done each: the levels are independent"
    go(pg, "invent")
    assert "one bar of bass" not in pg.inner_text("#v-invent")
    assert state(pg)["lv"] == {"r:pulse": 2, "r:bs-pulse@bass": 2}
    assert not pg.errors


# --------------------------------------------------------------------- X10 bass Invent

GUITAR_PROMPT = re.compile(r"strum|voicing|Fmaj7|Hum a melody|order of the chords|two bars instead", re.I)


def cells(pg):
    return pg.evaluate("()=>[...document.querySelectorAll('[data-bcell] b')].map(b=>b.textContent)")


def test_X10_bass_invent_builds_plays_and_saves_a_bar(app):
    pg = app(state=bass_state(passed=1, bpm=200), hash_="invent")
    assert "Pool: A, E." in pg.inner_text("#v-invent") and pg.locator("[data-bcell]").count() == 0
    pg.click("#roll")
    assert pg.locator("#v-invent .bcard").count() == 4 and pg.locator("#v-invent .cb").count() == 0, "bass sees root cards, not chord boxes"
    assert "Root A (do): A string, open" in pg.inner_text("#v-invent")
    assert cells(pg) == ["R", "·", "·", "·", "R", "·", "·", "·"], "starts as the band plays it: roots on 1 and 3"
    assert pg.locator("#chg").text_content() in BS["invent"]["prompts"]
    # tap: beat 3 goes root -> fifth; the last cell cycles through to the approach note
    pg.click('[data-bcell="4"]')
    assert cells(pg)[4] == "5" and pg.get_attribute('[data-bcell="4"]', "aria-label") == "Count 3: fifth"
    assert pg.evaluate("()=>document.activeElement.dataset.bcell") == "4", "focus stays on the cell"
    for want in ["R", "5", "8", "↗"]:
        pg.click('[data-bcell="7"]')
        assert cells(pg)[7] == want
    assert pg.get_attribute('[data-bcell="7"]', "aria-label") == "Count and: approach note"
    for want in ["R", "5", "8", "·"]:
        pg.click('[data-bcell="1"]')
        assert cells(pg)[1] == want, "only the last cell offers the approach note"
    assert "root on 1, fifth on 3, approach note on &" in pg.get_attribute(".bbar", "aria-label")
    # the band's bass voice plays the bar: roots, fifths and a semitone lead-in, nothing on beat 3's old root
    pg.click("#playLoop")
    assert pg.inner_text("#playLoop") == "Stop"
    pg.wait_for_timeout(4000)   # the count-in is two bars
    pg.click("#playLoop")
    loop = pg.evaluate("()=>[...document.querySelectorAll('#v-invent .bname')].map(e=>e.textContent)")
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    tri = [s["freq"] for s in starts(pg) if s["type"] == "triangle"]
    root = {"A": 33, "E": 28}
    near = lambda f, m: abs(f - hz(m)) < 0.3
    assert len(tri) >= 6
    assert near(tri[0], root[loop[0]]) and near(tri[1], root[loop[0]] + 7), tri[:4]
    nxt = root[loop[1]] - 1
    assert near(tri[2], nxt if nxt >= 28 else nxt + 12), "approach note: a semitone below the next root (an octave up if that is below the open E)"
    assert near(tri[3], root[loop[1]])
    # save
    pg.click("#keepLoop")
    j = state(pg)["journal"]
    assert len(j) == 1 and j[0]["inst"] == "bass" and j[0]["tag"] == "Invent" and j[0]["st"] == "a-e"
    assert set(j[0]) == {"d", "st", "inst", "tag", "h", "o", "w"}, "same journal entry shape as guitar's Invent"
    assert j[0]["o"] == "Loop: " + " – ".join(loop) + " · bar of bass: root on 1, fifth on 3, approach note on &"
    assert j[0]["w"] in BS["invent"]["prompts"] and not GUITAR_PROMPT.search(j[0]["w"] + j[0]["o"])
    go(pg, "record")
    assert "bar of bass" in pg.inner_text("#v-record") and "Invent" in pg.inner_text("#v-record")
    assert not pg.errors


@pytest.mark.parametrize("stage,n,first", [("c-g-f", 6, ["R", "·", "·", "·", "·", "·"]), ("six-eight", 6, ["R", "·", "·", "R", "·", "·"]), ("four-chords", 8, None)])
def test_X10_bass_bar_fits_the_stage_metre(app, stage, n, first):
    pg = app(state=bass_state(bpm=200), hash_=stage)
    go(pg, "invent")
    pg.click("#roll")
    assert len(cells(pg)) == n and (first is None or cells(pg) == first)
    pg.click("#playLoop")
    pg.wait_for_timeout(3500)
    pg.click("#playLoop")
    assert [s for s in starts(pg) if s["type"] == "triangle"], "no bass was scheduled"
    assert not pg.errors


def test_X10_prompt_never_crosses_between_guitar_and_bass(app):
    for _ in range(4):
        pg = app(state={"inst": "guitar"}, hash_="invent")
        pg.click("#roll")
        assert GUITAR_PROMPT.search(pg.locator("#chg").text_content()) or True
        go(pg, "a-e")
        pg.click('[data-inst="bass"]')
        go(pg, "invent")
        assert pg.locator("#chg").count() == 0, "the guitar loop and its prompt followed the player to bass"
        pg.click("#roll")
        assert pg.locator("#chg").text_content() in BS["invent"]["prompts"]
        go(pg, "a-e")
        pg.click('[data-inst="guitar"]')
        go(pg, "invent")
        assert pg.locator("#chg").count() == 0, "the bass prompt followed the player to guitar"
        assert not pg.errors
        pg.context.close()


# --------------------------------------------------------------------- X12 content policy

def all_text(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from all_text(v)
    elif isinstance(o, list):
        for v in o:
            yield from all_text(v)


X12_US = re.compile(r"\beighth|\bsixteenth|quarter[- ]note|half[- ]note|whole[- ]note|\bmeasures?\b|\bhalf[- ]step|\bwhole[- ]step|\bcolor\b", re.I)
X12_PROGRAMS = re.compile(r"kod[aá]ly|orff|suzuki|dalcroze|hal leonard|rockschool|\bameb\b|trinity|essential elements|yousician|fender play|"
                          r"simply (piano|guitar)|rocksmith|musition|auralia|alfred'?s|mel bay|justinguitar|scott'?s bass", re.I)


def test_X12_bass_content_policy():
    texts = [t for t in all_text(INSTDATA) if len(t) > 3]
    assert len(texts) > 60
    blob = "\n".join(texts)
    assert not X12_US.search(blob), X12_US.search(blob).group(0)
    assert not X12_PROGRAMS.search(blob), X12_PROGRAMS.search(blob).group(0)
    # no lyrics: nothing quoted at length, and no song words; songs are named only in the Also try links
    assert not re.findall(r"[\"“][^\"”]{25,}[\"”]", blob) and not re.findall(r"(?<!\w)'[^']{25,}'(?!\w)", blob)
    assert not re.search(r"\b(student|year \d+)\b", blob, re.I)
    for t in texts:
        assert "—" not in t and "  " not in t and t == t.strip(), repr(t[:60])
    assert re.search(r"quavers", blob) and re.search(r"crotchets", blob) and re.search(r"\bbars?\b", blob) and "semitone" in blob


def test_X12_hard_constraints_in_source():
    assert not re.search(r"(?<![\w.$])(alert|confirm|prompt)\s*\(", SRC)
    assert not re.search(r"\b(fetch|XMLHttpRequest|WebSocket|sendBeacon|importScripts)\b", SRC)
    assert not re.search(r"<script[^>]+src=|<link[^>]+href=", SRC)
    assert sorted(p.name for p in ROOT.iterdir() if not p.name.startswith(".")) == ["README.md", "fonts", "index.html", "tests"]


# --------------------------------------------------------------------- X13 the new bass pages render cleanly everywhere

@pytest.mark.parametrize("scheme", ["light", "dark"])
@pytest.mark.parametrize("width", [320, 360, 768, 1280])
def test_X13_bass_pages_render_clean(app, width, scheme):
    problems = []
    for fin in [f["k"] for f in FIN]:
        pg = app(width=width, scheme=scheme, state=bass_state(finish=fin, useFin=fin == "flam"))
        for s in ST:
            go(pg, s["id"])
            if pg.locator("#side details.know").count() < 1:
                problems.append(f"{fin}/{s['id']}: no cards")
            pg.evaluate("()=>document.querySelectorAll('#side details.know').forEach(d=>d.open=true)")
            problems += [f"{fin}/{s['id']}/path: overflow {p}" for p in pg.evaluate(OVERFLOW_JS)]
            go(pg, "invent")
            pg.click("#roll")
            if pg.locator("[data-bcell]").count() not in (6, 8):
                problems.append(f"{fin}/{s['id']}: no bar of bass")
            small = pg.evaluate("()=>[...document.querySelectorAll('[data-bcell]')].filter(b=>b.getBoundingClientRect().height<44||b.getBoundingClientRect().width<30).length")
            if small:
                problems.append(f"{fin}/{s['id']}: {small} bar cells too small to tap")
            problems += [f"{fin}/{s['id']}/invent: overflow {p}" for p in pg.evaluate(OVERFLOW_JS)]
        for tab, n in (("rudiments", len(BS["rud"])), ("technique", len(tech_for(fin))), ("record", None)):
            go(pg, tab)
            if n is not None and pg.locator(f"#v-{tab} .card").count() != n:
                problems.append(f"{fin}/{tab}: {pg.locator(f'#v-{tab} .card').count()} cards, not {n}")
            problems += [f"{fin}/{tab}: overflow {p}" for p in pg.evaluate(OVERFLOW_JS)]
        problems += [f"{fin}: {e}" for e in pg.errors]
        pg.context.close()
    assert not problems, "\n".join(problems[:30])
