"""Browser tests for index.html (Playwright, Chromium, file://).

1. A render matrix: 8 stages x 7 tabs x 5 instruments x 3 widths x light/dark.
2. Functional tests: gates, sign-off, grading, playback, capo, mute, gig.
3. One test per register item M1-M5, S1-S15 of tests/reports/spec06/SPEC_06.md,
   written against the FIXED behaviour the spec describes. On the 0.5 baseline
   most of these fail; that is expected until the fixes land.

Saved state is seeded through localStorage (the app's own storage key), and
stages / tabs are switched through the app's own hash routing.
"""
import re
import time

import pytest

import appdata
from uihelp import OVERFLOW_JS, PANELS_JS, go, state, starts

D = appdata.load()
ST, PAT, GIGS = D["ST"], D["PAT"], D["GIG"]
TABS = ["path", "warm-up", "rudiments", "technique", "invent", "gig", "record"]
INSTS = ["guitar", "bass", "drums", "keys", "vocals"]
NRUD, NTECH = len(D["RUD"]), len(D["TECH"])
FAST = {"bpm": 200}


def text(pg, sel):
    return pg.locator(sel).first.inner_text()


def toast(pg):
    return pg.evaluate("()=>{const t=document.getElementById('toast');return t&&!t.classList.contains('hide')?t.textContent:''}")


# ===================================================================== matrix

@pytest.mark.parametrize("inst", INSTS)
@pytest.mark.parametrize("scheme", ["light", "dark"])
@pytest.mark.parametrize("width", [360, 768, 1280])
def test_render_matrix(app, width, scheme, inst):
    pg = app(width=width, scheme=scheme, state={"inst": inst})
    bg = pg.evaluate("()=>getComputedStyle(document.body).backgroundColor")
    lum = sum(int(x) for x in re.findall(r"\d+", bg)[:3])
    assert (lum > 600) if scheme == "light" else (lum < 120), "colour scheme not applied: " + bg
    problems = []
    for s in ST:
        nch = len(set(s["ch"]))
        for tab in TABS:
            go(pg, s["id"])
            if tab != "path":
                go(pg, tab)
            where = f"{s['id']}/{tab}"
            for p in pg.evaluate(PANELS_JS, {"view": tab, "inst": inst, "nch": nch, "nrud": NRUD, "ntech": NTECH}):
                problems.append(where + ": " + p)
            for p in pg.evaluate(OVERFLOW_JS):
                problems.append(where + ": overflow " + p)
    problems += pg.errors
    assert not problems, "\n".join(problems[:40])


# ===================================================================== functional

def raise_step(pg, k, times=2):
    for _ in range(times):
        pg.click(f'[data-lv="{k}"][data-dir="1"]')


def test_gate_opens_and_closes(app):
    pg = app(state={})
    for i in range(5):
        raise_step(pg, f"a-e:{i}")
    assert "Gate passed" in text(pg, "#stage .gate")
    assert "gate passed" in pg.get_attribute('[data-st="a-e"]', "aria-label")
    assert state(pg)["gates"].get("a-e")
    assert "Stage 2" in text(pg, "#next")
    pg.click('[data-lv="a-e:2"][data-dir="-1"]')
    assert pg.locator("#stage .gate").count() == 0
    assert "gate closes" in toast(pg)
    assert "a-e" not in state(pg)["gates"]
    assert not pg.errors


def test_teacher_sign_off(app):
    pg = app(state={})
    pg.click("#tchBtn")
    assert pg.locator('[data-sign="a-e:0"]').count() == 0, "sign-off only from Consistent"
    raise_step(pg, "a-e:0")
    pg.click('[data-sign="a-e:0"]')
    assert "Teacher signed off" in text(pg, "#stage")
    assert "a-e:0" in state(pg)["sign"]
    pg.click('[data-lv="a-e:0"][data-dir="-1"]')
    assert "Press − again" in toast(pg)
    assert "a-e:0" in state(pg)["sign"], "first press only warns"
    pg.click('[data-lv="a-e:0"][data-dir="-1"]')
    assert "a-e:0" not in state(pg)["sign"]
    assert state(pg)["lv"]["a-e:0"] == 1
    assert not pg.errors


def test_grading(app):
    pg = app(state={})
    pg.click("#nswBtn")
    assert pg.locator("select[data-mark]").count() == 0
    assert "Not yet marked" in text(pg, "#grade")
    pg.click("#tchBtn")
    for i, v in enumerate(["2", "2", "2", "2"]):
        pg.select_option(f'select[data-mark="a-e:{i}"]', v)
    assert text(pg, "#grade") == "8 / 10 · grade B so far"
    pg.select_option('select[data-mark="a-e:4"]', "1")
    assert text(pg, "#grade") == "9 / 10 · grade A"
    for i in range(5):
        pg.select_option(f'select[data-mark="a-e:{i}"]', "1")
    assert text(pg, "#grade") == "5 / 10 · grade C"
    go(pg, "record")
    assert "A and E: 5 / 10" in text(pg, "#v-record")
    assert not pg.errors


def test_playback_start_stop(app):
    pg = app(state=FAST)
    pg.click("#playMap")
    assert text(pg, "#playMap") == "Stop"
    pg.wait_for_timeout(1800)
    n = len(starts(pg))
    assert n > 10, "the band scheduled nothing"
    pg.click("#playMap")
    assert text(pg, "#playMap") == "Play the chart"
    m = len(starts(pg))
    pg.wait_for_timeout(700)
    assert len(starts(pg)) == m, "scheduler kept running after Stop"
    assert not pg.errors


def test_capo(app):
    pg = app(state=FAST)
    row = "#stage"
    pg.click('[data-capo="1"]')
    assert "Capo 1" in text(pg, row) and "sounds in B♭ major" in text(pg, row)
    pg.click('[data-capo="1"]')
    assert "Capo 2" in text(pg, row) and "sounds in B major" in text(pg, row)
    assert state(pg)["capo"] == {"a-e": 2}
    # the band plays in the sounding key: bass A + 2 = B1 (61.7 Hz)
    pg.click("#playMap")
    pg.wait_for_timeout(1800)
    pg.click("#playMap")
    bass = [s["freq"] for s in starts(pg) if s["type"] == "triangle"]
    assert bass and abs(min(bass) - 61.735) < 0.5, bass[:4]
    pg.click('[data-capo="-1"]')
    pg.click('[data-capo="-1"]')
    assert "No capo" in text(pg, row) and "sounds in A major" in text(pg, row)
    pg.click('[data-capo="-1"]')
    assert "No capo" in text(pg, row), "capo can't go below 0"
    go(pg, "c-g-f")
    for _ in range(3):
        pg.click('[data-capo="1"]')
    assert "sounds in E♭ major" in text(pg, "#stage")
    for _ in range(6):
        pg.click('[data-capo="1"]')
    assert "Capo 7" in text(pg, "#stage"), "capo tops out at 7"
    assert not pg.errors


def audible(pg, flt):
    return pg.evaluate("f=>window.__aud.starts.filter(e=>(new Function('e','return '+f))(e)).map(e=>window.__audible(e))", flt)


PLUCK = "e.kind==='buf'&&e.dur>1"   # Karplus-Strong guitar notes (2.2 s buffers)
BASS = "e.kind==='osc'&&e.type==='triangle'"


def test_mute(app):
    pg = app(state=FAST)
    pg.click('[data-mute="guitar"]')
    assert pg.get_attribute('[data-mute="guitar"]', "aria-pressed") == "false"
    assert state(pg)["mute"]["guitar"] is True
    pg.click("#playMap")
    pg.wait_for_timeout(2000)
    g, b = audible(pg, PLUCK), audible(pg, BASS)
    pg.click("#playMap")
    assert not g or max(g) == 0, "muted guitar is still audible"
    assert b and min(b) > 0, "bass should still play"
    pg.reload()
    assert pg.get_attribute('[data-mute="guitar"]', "aria-pressed") == "false", "mute is saved"
    pg.click('[data-mute="guitar"]')
    assert pg.get_attribute('[data-mute="guitar"]', "aria-pressed") == "true"
    assert not pg.errors


def checked_songs(pg):
    return pg.evaluate("()=>[...document.querySelectorAll('input[data-gsong]')].filter(x=>x.checked).map(x=>x.dataset.gsong)")


def test_gig_choose_max_four(app):
    pg = app(state={}, hash_="gig")
    assert len(checked_songs(pg)) == 4
    pg.click('input[data-gsong="g-hound"]')
    assert "g-hound" not in checked_songs(pg)
    assert "Four songs" in toast(pg)
    pg.click('input[data-gsong="g-clock"]')
    assert len(checked_songs(pg)) == 3
    pg.click('input[data-gsong="g-hound"]')
    assert set(checked_songs(pg)) == {"g-boogie", "g-johnny", "g-bamba", "g-hound"}
    assert state(pg)["gig"]["songs"][-1] == "g-hound"
    assert "Hound Dog" in text(pg, "#v-gig")
    assert not pg.errors


def test_gig_timer(app):
    pg = app(state={}, hash_="gig", clock=True)
    pg.click('[data-gtime="5"]')
    assert text(pg, "#gtime") in ("5:00", "4:59")
    pg.clock.run_for(60_000)
    assert text(pg, "#gtime") in ("4:00", "3:59")
    pg.clock.run_for(4 * 60_000 + 1000)
    assert text(pg, "#gtime") == "0:00"
    assert "change over" in toast(pg)
    pg.click('[data-gtime="10"]')
    pg.clock.run_for(2000)
    pg.click("#gstop")
    assert text(pg, "#gtime") == "0:00"
    pg.clock.run_for(5000)
    assert text(pg, "#gtime") == "0:00", "Stop really stops"
    assert not pg.errors


def run_sheet(pg):
    """[[row text per band] per phase] from the visible run sheet."""
    return pg.evaluate(r"""()=>{const card=[...document.querySelectorAll('#v-gig .card')].find(c=>/run sheet/i.test((c.querySelector('h3')||{}).textContent||''));
     if(!card)return null;return [...card.querySelectorAll('table')].map(t=>[...t.querySelectorAll('tr')].filter(tr=>tr.querySelector('td')).map(tr=>[...tr.children].map(td=>td.innerText.trim())))}""")


def roles_of(cell):
    out = {}
    for part in cell.split(","):
        if ":" in part:
            r, n = part.split(":", 1)
            out[r.strip()] = n.strip()
    return out


def fill_role(pg, sel, value):
    pg.fill(sel, value)
    pg.dispatch_event(sel, "change")


def test_gig_roles(app):
    pg = app(state={}, hash_="gig")
    pg.click("#rot")  # rotation off: roles exactly as entered
    fill_role(pg, '[data-bm="0:guitar"]', "Ann")
    fill_role(pg, '[data-bm="0:bass"]', "Ben")
    sheet = run_sheet(pg)
    assert len(sheet) == 4, "one phase per chosen song"
    for ph in sheet:
        assert roles_of(ph[0][-1]) == {"Guitar": "Ann", "Bass": "Ben"}
    pg.click("#addBand")
    sheet = run_sheet(pg)
    assert all(len(ph) == 2 for ph in sheet)
    assert sheet[0][0][1] != sheet[0][1][1], "two bands rehearse different songs in a phase"
    songs = [ph[0][1] for ph in sheet]
    assert len(set(songs)) == 4, "each band works through every song"
    g = state(pg)["gig"]
    assert g["bands"][0]["m"] == {"guitar": "Ann", "bass": "Ben"} and g["rotate"] is False
    assert not pg.errors


# ===================================================================== register: Must

def gig_state(m, rotate=True):
    return {"gig": {"songs": ["g-boogie", "g-clock", "g-johnny", "g-bamba"],
                    "bands": [{"name": "Band 1", "m": m}], "block": 20, "rotate": rotate, "open": "g-boogie"}}


def test_M1_rotation_only_among_filled_roles(app):
    pg = app(state=gig_state({"guitar": "Ann"}), hash_="gig")
    for ph in run_sheet(pg):
        assert roles_of(ph[0][-1]) == {"Guitar": "Ann"}, "one student on guitar stays on guitar"
    pg2 = app(state=gig_state({"guitar": "Ann", "drums": "Cat"}), hash_="gig")
    sheet = [roles_of(ph[0][-1]) for ph in run_sheet(pg2)]
    assert sheet[0] == {"Guitar": "Ann", "Drums": "Cat"}, "phase 1 = roles exactly as entered"
    for ph in sheet:
        assert set(ph) == {"Guitar", "Drums"}, "rotate only among roles with a player"
        assert sorted(ph.values()) == ["Ann", "Cat"]
    assert any(ph["Drums"] == "Ann" for ph in sheet), "players do rotate"


def _lum(rgb):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    def rgb(s):
        return [float(x) for x in re.findall(r"[\d.]+", s)[:3]]
    la, lb = _lum(rgb(a)), _lum(rgb(b))
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


KBD_JS = r"""
name=>{const btn=document.querySelector('#stage [data-strum="'+name+'"]');const svg=btn&&btn.querySelector('svg.kb, svg');if(!svg)return null;
 const rects=[...svg.querySelectorAll('rect')].map(r=>({b:r.getBBox(),fill:getComputedStyle(r).fill}));
 const maxH=Math.max(...rects.map(r=>r.b.height));const white=rects.filter(r=>r.b.height>=maxH*.8),black=rects.filter(r=>r.b.height<maxH*.8);
 const mode=a=>{const c={};a.forEach(x=>c[x]=(c[x]||0)+1);const e=Object.entries(c).sort((p,q)=>q[1]-p[1]);return e.length?e[0][0]:null};
 const blackH=black.length?Math.max(...black.map(r=>r.b.y+r.b.height)):0;
 const at=(x,y)=>{let h=null;for(const r of rects)if(x>=r.b.x&&x<=r.b.x+r.b.width&&y>=r.b.y&&y<=r.b.y+r.b.height)h=r;return h};
 const labels=[...svg.querySelectorAll('text')].map(t=>{const b=t.getBBox(),cx=b.x+b.width/2,cy=b.y+b.height/2,r=at(cx,cy);
   return {s:t.textContent.trim(),fill:getComputedStyle(t).fill,key:r&&r.fill,white:cy>blackH}});
 return {labels,unlitWhite:mode(white.map(r=>r.fill)),unlitBlack:mode(black.map(r=>r.fill))}}
"""


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_M2_lit_keys_strong_and_named(app, scheme):
    pg = app(scheme=scheme, state={"inst": "keys"})
    for chord, notes in [("A", {"A", "C♯", "E"}), ("E", {"E", "G♯", "B"})]:
        k = pg.evaluate(KBD_JS, chord)
        assert k, "no keyboard for " + chord
        names = {lb["s"].replace("#", "♯") for lb in k["labels"] if re.fullmatch(r"[A-G][♯#♭b]?", lb["s"])}
        assert names == notes, f"{chord}: lit keys should be labelled {notes}, got {names}"
        for lb in k["labels"]:
            if lb["s"].replace("#", "♯") not in notes:
                continue
            assert lb["key"], "label not on a key"
            unlit = k["unlitWhite"] if lb["white"] else k["unlitBlack"]
            c = contrast(lb["key"], unlit)
            assert c >= 3, f"{chord} {lb['s']}: lit {lb['key']} vs unlit {unlit} contrast {c:.2f} < 3"
            t = contrast(lb["fill"], lb["key"])
            assert t >= 4.5, f"{chord} {lb['s']}: label contrast {t:.2f} < 4.5"


NOTE = r"([A-G][♯♭#b]?)"
POS = r"\s*:?\s*(E|A|D|G) string,?\s*(open|fret (\d+))"
BASS_OPEN = {"E": 28, "A": 33, "D": 38, "G": 43}


def _pc(n):
    from test_chords import pc
    return pc(n)


@pytest.mark.parametrize("stage,capo,roots", [
    ("a-e", 1, {"B♭": "F", "F": "C"}),
    ("a-e", 2, {"B": "F♯", "F♯": "C♯"}),
    ("c-g-f", 3, {"E♭": "B♭", "B♭": "F", "A♭": "E♭"}),
])
def test_M3_bass_panel_follows_capo(app, stage, capo, roots):
    pg = app(state={"inst": "bass", "stage": stage, "capo": {stage: capo}}, hash_=stage)
    t = text(pg, "#stage")
    found = {}
    for m in re.finditer(r"Root " + NOTE + POS, t):
        nm, s, _, fr = m.groups()
        midi = BASS_OPEN[s] + int(fr or 0)
        assert midi % 12 == _pc(nm), f"root {nm} is not at {s} string {fr or 'open'}"
        found[nm.replace("#", "♯")] = None
    for m in re.finditer(r"Fifth " + NOTE + POS, t):
        nm, s, _, fr = m.groups()
        assert (BASS_OPEN[s] + int(fr or 0)) % 12 == _pc(nm), f"fifth {nm} is not at {s} string {fr or 'open'}"
    expect = {r for r in roots}
    assert set(found) >= expect, f"capo {capo}: bass roots should be {expect}, panel shows {set(found)}"
    for r, f in roots.items():
        assert re.search(r"Fifth " + re.escape(f) + r"(?![♯♭#b])", t), f"fifth of {r} should read {f}"


@pytest.mark.parametrize("stage,capo,spellings,absent", [
    ("a-e", 1, ["B♭ D F", "F A C"], ["A C♯ E", "E G♯ B"]),
    ("a-e", 2, ["B D♯ F♯", "F♯ A♯ C♯"], ["A C♯ E"]),
    ("c-g-f", 3, ["E♭ G B♭", "B♭ D F", "A♭ C E♭"], ["C E G"]),
])
def test_M3_keys_panel_follows_capo(app, stage, capo, spellings, absent):
    pg = app(state={"inst": "keys", "stage": stage, "capo": {stage: capo}}, hash_=stage)
    t = text(pg, "#stage")
    for sp in spellings:
        assert sp in t, f"keys panel should spell {sp} with capo {capo}"
    for sp in absent:
        assert sp not in t, f"keys panel still shows un-capoed {sp}"
    labels = " | ".join(pg.evaluate("()=>[...document.querySelectorAll('#stage svg.kb')].map(s=>s.getAttribute('aria-label')||'')"))
    for sp in spellings:
        assert sp in labels, f"keyboard drawing for {sp} missing: {labels}"


def _transpose_name(n, frm, to):
    """Letter-preserving transposition: the interval from key to note stays the same interval."""
    from test_chords import LETTERS, pc, spell_note
    li = (LETTERS.index(n[0]) + LETTERS.index(to[0]) - LETTERS.index(frm[0])) % 7
    return spell_note(LETTERS[li], (pc(n) + pc(to) - pc(frm)) % 12)


SETTLED_JS = r"""({id,title,nkb,capo})=>{const st=document.getElementById('stage'),h=st&&st.querySelector('h2');
 return location.hash==='#'+id&&!!h&&h.textContent.trim()===title&&st.querySelectorAll('svg.kb').length===nkb
  &&[...st.querySelectorAll('svg.kb')].every(s=>s.getAttribute('aria-label'))&&st.innerText.includes('Capo '+capo)&&/sounds in [A-G]/.test(st.innerText)}"""


def settle_keys_panel(pg, s, capo):
    """R12 (0.7): wait until the keys panel for this stage and capo is fully drawn before reading it.
    Returns False if it never settles, so the caller reports what is on screen instead of a bare timeout."""
    try:
        pg.wait_for_function(SETTLED_JS, arg={"id": s["id"], "title": s["title"], "nkb": len(dict.fromkeys(s["ch"])), "capo": capo}, timeout=15_000)
        return True
    except Exception:
        return False


def test_M3_keys_spelling_every_capo(app):
    """Every stage, capo 1-7: the keys panel spells each chord in the sounding key,
    exactly as the un-capoed spelling moved by the same interval (no enharmonic slips)."""
    from test_chords import MAJOR_KEYS, MINOR_KEYS, pc
    tonic = {"A": "A", "Am": "A", "C": "C", "Am6": "A", "Bm": "B"}
    bad = []
    for capo in range(1, 8):
        pg = app(state={"inst": "keys", "capo": {s["id"]: capo for s in ST}})
        pg.wait_for_function("()=>document.querySelectorAll('#stage svg.kb').length>0", timeout=15_000)   # seeded state is on screen
        for s in ST:
            go(pg, s["id"])
            if not settle_keys_panel(pg, s, capo):
                bad.append(f"{s['id']} capo {capo}: keys panel never settled; stage shows {text(pg, '#stage')[:100]!r}; saved {state(pg).get('inst')}/{state(pg).get('capo')}")
                continue
            t = text(pg, "#stage")
            m = re.search(r"sounds in ([A-G][♯♭]?) (major|minor)", t)
            if not m:
                bad.append(f"{s['id']} capo {capo}: no 'sounds in' key")
                continue
            to, md = m.groups()
            allowed = (MAJOR_KEYS if md == "major" else MINOR_KEYS)[(pc(tonic[s["key"]]) + capo) % 12]
            if to not in allowed:
                bad.append(f"{s['id']} capo {capo}: sounds in {to} {md}, expected {allowed}")
            labels = " | ".join(pg.evaluate("()=>[...document.querySelectorAll('#stage svg.kb')].map(s=>s.getAttribute('aria-label')||'')"))
            for c in dict.fromkeys(s["ch"]):
                want = " ".join(_transpose_name(n, tonic[s["key"]], to) for n in D["CH"][c]["t"].split(" "))
                if want not in labels:
                    bad.append(f"{s['id']} capo {capo} ({to} {md}): {c} should read {want}; panel: {labels[:120]}")
        assert not pg.errors, pg.errors
        pg.context.close()
    assert not bad, "\n".join(bad[:25])


def test_R12_keys_panel_settle_wait_is_real(app):
    """The settle check must be true for the right stage and capo, and false for a wrong one (so it cannot pass vacuously)."""
    pg = app(state={"inst": "keys", "capo": {"beyond": 3}})
    by = {s["id"]: s for s in ST}
    go(pg, "beyond")
    assert settle_keys_panel(pg, by["beyond"], 3)
    args = lambda s, c: {"id": s["id"], "title": s["title"], "nkb": len(dict.fromkeys(s["ch"])), "capo": c}
    assert not pg.evaluate(SETTLED_JS, args(by["beyond"], 4)), "wrong capo reported as settled"
    assert not pg.evaluate(SETTLED_JS, args(by["a-e"], 3)), "wrong stage reported as settled"
    go(pg, "a-e")
    assert not pg.evaluate(SETTLED_JS, args(by["beyond"], 3))


@pytest.mark.parametrize("width", [360, 390])
def test_M4_drum_grid_reachable_on_phones(app, width):
    pg = app(width=width, state={"inst": "drums", "stage": "four-chords"}, hash_="four-chords")
    r = pg.evaluate(r"""()=>{const t=document.querySelector('#stage table');if(!t)return 'no grid';const W=document.documentElement.clientWidth;
      const tr=t.getBoundingClientRect();if(tr.right<=W+1&&tr.left>=-1)return 'ok';
      let p=t.parentElement;while(p&&p!==document.body){const o=getComputedStyle(p).overflowX;if(o==='auto'||o==='scroll'){const pr=p.getBoundingClientRect();
        return pr.right<=W+1&&pr.left>=-1&&p.scrollWidth>=tr.width-1?'ok':'scroller off screen'}p=p.parentElement}
      return 'grid spans '+Math.round(tr.left)+'..'+Math.round(tr.right)+' in '+W+' with no scroller'}""")
    assert r == "ok", r
    heads = pg.evaluate("()=>[...document.querySelector('#stage table tr').children].map(x=>x.textContent.trim())")
    assert "3" in heads and "4" in heads


def test_M4_drum_grid_has_headroom(app):
    """Headless Chromium lays the 0.5 grid out at ~307px, just inside a 360px phone, so the
    clipping seen on real phones (larger system text, artifact frame padding) doesn't
    reproduce at 360/390 here. The fix is 'scroll wrapper and/or smaller cells': require
    either a horizontal scroll wrapper around the grid, or a grid that fits its column on a 320px screen."""
    pg = app(width=320, state={"inst": "drums", "stage": "four-chords"}, hash_="four-chords")
    r = pg.evaluate(r"""()=>{const t=document.querySelector('#stage table');if(!t)return 'no grid';
      let p=t.parentElement;while(p&&p.id!=='stage'){const o=getComputedStyle(p).overflowX;if(o==='auto'||o==='scroll')return 'ok';p=p.parentElement}
      const W=document.getElementById('stage').getBoundingClientRect().right,tr=t.getBoundingClientRect();return tr.right<=W+1?'ok':'no scroll wrapper and grid spans to '+Math.round(tr.right)+', past its column edge at '+Math.round(W)}""")
    assert r == "ok", r


def test_M5_gig_inputs_keep_focus(app):
    pg = app(state={}, hash_="gig")
    pg.click('[data-bname="0"]')
    pg.keyboard.press("End")
    pg.evaluate("()=>{document.activeElement.__mark=1}")
    same = "s=>document.activeElement.__mark===1&&document.activeElement.matches(s)"
    for ch in " Rox":
        pg.keyboard.type(ch)
        assert pg.evaluate(same, '[data-bname="0"]'), "band name lost focus while typing"
    pg.keyboard.press("Tab")
    assert pg.evaluate("()=>document.activeElement.matches('[data-bm=\"0:guitar\"]')"), "Tab should land in the guitar field"
    pg.evaluate("()=>{document.activeElement.__mark=1}")
    for ch in "Ann":
        pg.keyboard.type(ch)
        assert pg.evaluate(same, '[data-bm="0:guitar"]'), "role field lost focus while typing"
    pg.keyboard.press("Tab")
    assert pg.evaluate("()=>document.activeElement.matches('[data-bm=\"0:bass\"]')"), "Tab should land in the bass field"
    pg.keyboard.type("Ben")
    pg.keyboard.press("Tab")
    assert "Ann" in text(pg, "#v-gig") and "Ben" in str(run_sheet(pg))
    g = state(pg)["gig"]
    assert g["bands"][0]["name"] == "Band 1 Rox"
    assert g["bands"][0]["m"].get("guitar") == "Ann" and g["bands"][0]["m"].get("bass") == "Ben"


# ===================================================================== register: Should

HAT_JS = r"""()=>{const t=document.querySelector('#stage table');if(!t)return null;const row=[...t.querySelectorAll('tr')].find(r=>/hat/i.test((r.children[0]||{}).textContent||''));
 if(!row)return null;return [...row.children].slice(1).filter(td=>td.textContent.trim()).length}"""


@pytest.mark.parametrize("stage,extra,hats", [
    ("a-e", {}, 4),                                          # four downs: band plays four hats
    ("twelve-bar", {}, 8),                                   # shuffle quavers
    ("six-eight", {}, 6),                                    # six quavers
    ("twelve-bar", {"finish": "flam", "useFin": True}, 4),   # band plays tangos (4 crotchets)
])
def test_S1_drum_grid_matches_band(app, stage, extra, hats):
    pg = app(state=dict({"inst": "drums", "stage": stage}, **extra), hash_=stage)
    assert pg.evaluate(HAT_JS) == hats


def countin_clicks(st):
    return [s for s in st if s["kind"] == "osc" and s["type"] == "sine" and s["freq"] in (1000, 1500)]


def test_S2_double_tap_play_does_not_stack(app):
    pg = app(state=FAST)
    pg.evaluate("()=>{const b=document.getElementById('playMap');b.click();b.click()}")
    pg.wait_for_timeout(1800)
    st = starts(pg)
    pg.evaluate("()=>{const b=document.getElementById('playMap');if(b.textContent==='Stop')b.click()}")
    assert len(countin_clicks(st)) <= 6, f"{len(countin_clicks(st))} count-in clicks: two bands started"
    noise = [round(s["when"], 2) for s in st if s["kind"] == "buf" and s["dur"] and s["dur"] < 0.5]
    assert noise, "no drums scheduled"
    assert max(noise.count(x) for x in noise) <= 2, "overlapping drum schedules (more than kick/snare + hat at one time)"


def test_S3_bad_gig_state_is_sanitised(app):
    bad = {"gig": {"songs": ["nope", "g-clock", "g-clock", 42, "g-johnny", "g-bamba", "g-hound", "g-shoes"],
                   "bands": [{"name": 7, "m": {"guitar": {"x": 1}, "piano": "Zed", "bass": "Ben"}}, "bad", None],
                   "block": 999, "rotate": "yes", "open": "zzz"}}
    pg = app(state=bad, hash_="gig")
    assert not pg.errors, pg.errors
    ch = checked_songs(pg)
    ids = {g["id"] for g in GIGS}
    assert 1 <= len(ch) <= 4 and len(set(ch)) == len(ch) and set(ch) <= ids
    m = re.search(r"(\d+) of 4 chosen", text(pg, "#v-gig"))
    assert m and int(m.group(1)) == len(ch)
    assert pg.input_value("#blk") == "20"
    t = text(pg, "#v-gig")
    for junk in ("undefined", "[object Object]", "null", "Zed", "NaN"):
        assert junk not in t, junk + " leaked into the page"
    assert len(run_sheet(pg)) == len(ch)
    assert not pg.errors


def test_S4_view_button_on_every_song(app):
    pg = app(state={}, hash_="gig")
    tagged = pg.evaluate(r"""()=>{const out={};for(const inp of document.querySelectorAll('input[data-gsong]')){let p=inp.parentElement;
      while(p&&p.querySelectorAll('input[data-gsong]').length===1){const b=[...p.querySelectorAll('button')].find(b=>/\bview\b/i.test(b.textContent+' '+(b.getAttribute('aria-label')||'')));
        if(b){b.setAttribute('data-testview',inp.dataset.gsong);out[inp.dataset.gsong]=1;break}p=p.parentElement}}return Object.keys(out)}""")
    assert set(tagged) == {g["id"] for g in GIGS}, "every song needs its own View button"
    assert "g-hound" not in checked_songs(pg)
    pg.click('[data-testview="g-hound"]')
    assert "Jerry Leiber" in text(pg, "#v-gig"), "Hound Dog backstory not shown"
    assert "g-hound" not in checked_songs(pg), "View must not choose the song"
    assert not pg.errors


def test_S5_stage2_example_is_rock_around_the_clock(app):
    pg = app(state={"stage": "twelve-bar"}, hash_="twelve-bar")
    t = text(pg, "#stage")
    for line in t.splitlines():
        if re.search(r"Johnny B\.? Goode", line):
            assert "in A" not in line and "B♭" in line, "Johnny B. Goode (recorded in B♭) offered as a 12-bar in A: " + line
    links = pg.evaluate("()=>[...document.querySelectorAll('#stage .card a')].map(a=>[a.textContent,a.href])")
    main = [l for l in links if "Rock Around the Clock" in l[0]]
    assert main and "Rock" in main[0][1], links


def cue_sheet(pg):
    return pg.evaluate(r"""()=>{const h=[...document.querySelectorAll('#stage h3')].find(h=>/cue sheet/i.test(h.textContent));
      if(!h)return null;const c=h.closest('.card')||h.parentElement;return {all:c.innerText,
      lines:[...c.querySelectorAll('p,li,div')].map(e=>e.innerText)}}""")


@pytest.mark.parametrize("stage,capo,syl,names", [
    ("a-e", 0, ["do", "so"], ["A", "E"]),
    ("am-e7", 0, ["la", "mi"], ["A", "E"]),
    ("c-g-f", 0, ["do", "fa", "so"], ["C", "F", "G"]),
    ("a-e", 1, ["do", "so"], ["B♭", "F"]),
])
def test_S6_vocal_roots_line_and_wording(app, stage, capo, syl, names):
    st = {"inst": "vocals", "stage": stage}
    if capo:
        st["capo"] = {stage: capo}
    pg = app(state=st, hash_=stage)
    cs = cue_sheet(pg)
    assert cs, "no cue sheet"
    line = [l for l in cs["lines"] if all(re.search(r"\b%s\b" % s, l) for s in syl)]
    assert line, f"no sol-fa roots line with {syl}: {cs['all']!r}"
    for n in names:
        assert re.search(r"(^|[\s(·,:=–-])" + re.escape(n) + r"(?![♯♭#b\w])", line[0]), f"roots line should name the root {n}: {line[0]!r}"
    steps = pg.evaluate("()=>[...document.querySelectorAll('#stage .step')].map(s=>s.innerText)")
    reh = [s for s in steps if "Rehearse" in s] or [steps[3]]
    assert "play your part" not in reh[0].lower() and re.search(r"\bsing", reh[0], re.I), reh[0]


@pytest.mark.parametrize("stage,metre", [("four-chords", 4), ("c-g-f", 3), ("six-eight", 6)])
def test_S7_bass_wording_metre_aware(app, stage, metre):
    pg = app(state={"inst": "bass", "stage": stage}, hash_=stage)
    t = text(pg, "#stage")
    if metre == 4:
        assert "1 and 3" in t
    else:
        assert "1 and 3" not in t, f"{metre}-time stage still says beats 1 and 3"


def test_S8_records_per_instrument(app):
    ts = int(time.time() * 1000) - 86400000
    seed = {"changes": [{"d": ts, "st": "a-e", "pair": "A-E", "n": 33}], "sign": {"a-e:0": ts},
            "lv": {f"a-e:{i}": 2 for i in range(5)}}
    pg = app(state=seed)
    assert "Best: 33" in text(pg, "#side"), "old data migrates to guitar"
    go(pg, "rudiments")
    assert "Opens with stage 2" not in text(pg, "#v-rudiments")
    go(pg, "record")
    assert re.search(r"\b1 steps? signed off", text(pg, "#v-record"))
    go(pg, "a-e")
    pg.click('[data-inst="bass"]')
    assert "not logged yet" in text(pg, "#side"), "bass shows the guitar's changes"
    pg.fill("#cnt", "40")
    pg.click("#logChg")
    assert "Best: 40" in text(pg, "#side")
    go(pg, "record")
    rec = text(pg, "#v-record")
    assert not re.search(r"\b1 steps? signed off", rec), "bass shows the guitar's sign-off count"
    assert "33" not in rec, "bass record shows guitar changes"
    go(pg, "rudiments")
    assert "Opens with stage 2" in text(pg, "#v-rudiments"), "bass hasn't passed stage 1"
    go(pg, "a-e")
    pg.click('[data-inst="guitar"]')
    assert "Best: 33" in text(pg, "#side")
    go(pg, "record")
    assert "40" not in text(pg, "#v-record"), "guitar record shows bass changes"


def test_S9_gig_plays_full_band_despite_path_mutes(app):
    pg = app(state=dict(FAST, mute={"guitar": True, "bass": True, "keys": True, "drums": True}), hash_="gig")
    pg.click("#playGig")
    pg.wait_for_timeout(5000)  # gig may play at the song's own tempo (S12), so allow a 120 bpm count-in
    g, b = audible(pg, PLUCK), audible(pg, BASS)
    pg.click("#playGig")
    assert g and max(g) > 0, "gig guitar silent because of a Path mute"
    assert b and max(b) > 0, "gig bass silent because of a Path mute"


def test_S10_gig_timer_unlocks_audio(app):
    pg = app(state={}, hash_="gig", clock=True)
    assert pg.evaluate("()=>window.__audState().ctxs") == 0
    pg.click('[data-gtime="5"]')
    pg.wait_for_timeout(200)
    a = pg.evaluate("()=>window.__audState()")
    assert a["ctxs"] >= 1 and "running" in a["states"], f"timer tap didn't start audio: {a}"
    n0 = len(starts(pg))
    pg.clock.run_for(5 * 60_000 + 1000)
    beeps = [s for s in starts(pg)[n0:] if s["kind"] == "osc"]
    assert len(beeps) >= 1, "end beep not scheduled"


def test_S11_present_mode_projects_run_sheet(app):
    pg = app(width=1280, state={}, hash_="gig")
    fs = "()=>{const c=[...document.querySelectorAll('#v-gig .card')].find(c=>/run sheet/i.test(c.textContent));const td=c&&c.querySelector('td');return td?parseFloat(getComputedStyle(td).fontSize):0}"
    chart = "()=>{const s=document.querySelector('#v-gig .rmap');if(!s||!s.getClientRects().length)return 0;const r=s.getBoundingClientRect();return r.width*r.height}"
    before, cb = pg.evaluate(fs), pg.evaluate(chart)
    pg.click("#present")
    hidden = pg.evaluate("()=>['input[data-gsong]','input[data-bname]','#addBand'].map(s=>{const e=document.querySelector(s);return !e||!e.getClientRects().length})")
    assert all(hidden), "setup still shown in Present mode"
    after, ca = pg.evaluate(fs), pg.evaluate(chart)
    assert after > before * 1.2, f"run sheet not scaled ({before}px -> {after}px)"
    assert ca >= cb and ca > 0, "chart hidden or shrunk"
    pg.click("#present")
    assert pg.locator("input[data-gsong]").first.is_visible(), "leaving Present restores setup"


def test_S12_gig_metronome_uses_gig_song(app):
    pg = app(state={"stage": "a-e", "bpm": 70}, hash_="gig")
    assert pg.inner_text(".mbar .m-name") == PAT["shuffle"]["n"]
    pg.click(".mbar .m-toggle")
    pg.wait_for_timeout(1600)
    pg.click(".mbar .m-toggle")
    t = sorted(s["when"] for s in countin_clicks(starts(pg)))
    assert len(t) >= 4
    beat = 60 / 120
    for a, b in zip(t, t[1:]):
        d = b - a
        assert min(abs(d - beat * 2 / 3), abs(d - beat / 3)) < 0.004, f"click gap {d:.3f}s is not swung quavers at 120"


def test_S13_keys_label_shows_spelling(app):
    pg = app(state={"inst": "keys"})
    for c, sp in [("A", "A C♯ E"), ("E", "E G♯ B")]:
        lab = pg.get_attribute(f'#stage [data-strum="{c}"]', "aria-label") or text(pg, f'#stage [data-strum="{c}"]')
        assert sp in lab, f"label {lab!r} should show {sp}"


ANNOUNCE_JS = r"""()=>{const out=[];for(const el of document.querySelectorAll('#v-path *, #toast')){if(!el.getClientRects().length&&el.id!=='toast')continue;
  const t=(el.innerText||el.textContent||'').trim();if(!t||t.length>300)continue;
  if(/\b(can[’']?t|cannot|won[’']?t|doesn[’']?t|does not|isn[’']?t|not)\b/i.test(t)&&/\b(feel|finish|flamenco)\b/i.test(t)&&/\bband\b/i.test(t))out.push(t)}return out}"""


def test_S14_finish_feel_mismatch_announced(app):
    pg = app(state={"stage": "c-g-f", "finish": "flam"}, hash_="c-g-f")
    pg.click('[data-pat="1"]')
    msgs = pg.evaluate(ANNOUNCE_JS)
    assert msgs, "no announcement that the band can't follow the flamenco 12-beat compás in 3/4"


@pytest.mark.parametrize("change,extra", [('[data-pat="1"]', {}), ('[data-fin="rock"]', {"useFin": True})])
def test_S14_changing_feel_stops_playback(app, change, extra):
    pg = app(state=dict(FAST, **extra))
    pg.click("#playMap")
    pg.wait_for_timeout(500)
    pg.click(change)
    assert text(pg, "#playMap") == "Play the chart", "feel changed mid-play"
    n = len(starts(pg))
    pg.wait_for_timeout(1200)
    assert len(starts(pg)) == n, "band kept scheduling after the feel changed"


@pytest.mark.parametrize("stage", ["four-chords", "hallelujah", "beyond"])
def test_S15_listen_for_the_entry(app, stage):
    pg = app(state={"inst": "vocals", "stage": stage}, hash_=stage)
    cs = cue_sheet(pg)
    assert cs and re.search(r"listen for the entry", cs["all"], re.I), cs and cs["all"]
    assert not re.search(r"come in after the count-in|pickup", cs["all"], re.I), "specific pickup claim"
    pg2 = app(state={"stage": stage}, hash_=stage)
    assert not re.search(r"pickup", text(pg2, "#stage"), re.I)


# ===================================================================== register 0.7
# One or more tests per item R1-R11 of tests/reports/spec07/SPEC_07.md (R6 and the data half
# of R7 are in test_chords.py; R12 is the settle-wait in test_M3_keys_spelling_every_capo).

import json
import pathlib

from uihelp import URL

TS = 1764200000000
# A full saved state in the app's own normal form: every field of the 0.7 shape is used.
RICH = {
    "finish": "rock", "stage": "c-g-f", "nsw": True, "teacher": False,
    "lv": {"a-e:0": 2, "a-e:1": 2, "a-e:2": 3, "a-e:3": 2, "a-e:4": 2, "c-g-f@keys:0": 1, "r:pulse": 2, "t:power@bass": 1},
    "sign": {"a-e:0": TS}, "marks": {"a-e:0": 1.5, "a-e:1": 2},
    "changes": [{"d": TS, "st": "a-e", "inst": "guitar", "pair": "A-E", "n": 31},
                {"d": TS + 5, "st": "beyond", "inst": "bass", "pair": "Bm-F#", "n": 12}],
    "journal": [{"d": TS, "st": "a-e", "inst": "guitar", "h": "Heard the pull", "o": "Two clean runs", "w": "B string buzzes"},
                {"d": TS + 9, "st": "c-g-f", "inst": "keys", "tag": "Invent", "h": "", "o": "Loop: C – F – G – C", "w": "Swap one voicing"}],
    "bpm": 96, "useFin": True, "gates": {"a-e": TS}, "warm": {"2026-11-20": ["tune", "clap", "spider", "changes", "sing"]},
    "best": {"r:pulse": 80, "r:pulse@bass": 70}, "capo": {"beyond": 4}, "mute": {"bass": True}, "inst": "keys",
    "gig": {"songs": ["g-clock", "g-bamba", "g-hound", "g-shoes"],
            "bands": [{"name": "Band 1", "m": {"guitar": "Player One", "drums": "Player Two"}}, {"name": "The Loud Ones", "m": {}}],
            "block": 15, "rotate": False, "useFin": True, "open": "g-bamba", "bpm": 110},
}
POPUPS_JS = "()=>{window.__pop=[];for(const k of ['alert','confirm','prompt'])window[k]=(...a)=>{window.__pop.push(k+': '+a.join(' '));return k==='confirm'?true:''}}"
CLIP_OK_JS = "()=>{window.__clip=null;Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:t=>{window.__clip=t;return Promise.resolve()}}})}"
CLIP_BLOCKED_JS = "()=>{Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:()=>Promise.reject(new Error('blocked'))}})}"


def raw(pg):
    return pg.evaluate("()=>localStorage.getItem('shredder')")


def copy_backup(pg):
    pg.evaluate(CLIP_OK_JS)
    pg.click("#bkCopy")
    pg.wait_for_function("()=>window.__clip")
    return pg.evaluate("()=>window.__clip")


def offer(pg, txt):
    pg.fill("#bkIn", txt)
    pg.click("#bkImport")


def test_R1_backup_panel_is_findable(app):
    pg = app(state={})
    foot = pg.locator(".foot a[href='#record']")
    assert foot.count() == 1 and re.search(r"backup", foot.inner_text(), re.I), "footer should point to the backup"
    foot.click()
    pg.wait_for_selector("#backup")
    card = text(pg, "#backup")
    for label in ["Download backup", "Copy backup", "Choose a backup file", "Import pasted backup"]:
        assert label in card, label
    look = pg.evaluate("""()=>{const b=document.getElementById('bkDown'),o=document.getElementById('playMap')||document.querySelector('#jf button'),c=s=>getComputedStyle(s);
      return [c(b).fontFamily===c(o).fontFamily,c(b).borderRadius===c(o).borderRadius,c(b).backgroundColor===c(o).backgroundColor,parseFloat(c(b).minHeight)>=44]}""")
    assert all(look), f"backup buttons should match the app's own buttons: {look}"
    assert not pg.errors


def test_R1_export_import_round_trip_is_lossless(app):
    a = app(state=RICH, hash_="record")
    a.evaluate(POPUPS_JS)
    txt = copy_backup(a)
    assert "copied" in text(a, "#bkMsg").lower()
    out = json.loads(txt)
    assert out["app"] == "The Guitar Lab" and out["version"] == "0.9" and out["format"] == 1 and out["saved"]
    assert out["state"] == RICH, "export must carry the full saved state unchanged"
    with a.expect_download() as dl:
        a.click("#bkDown")
    assert re.fullmatch(r"guitar-lab-backup-\d{4}-\d\d-\d\d\.json", dl.value.suggested_filename)
    assert json.loads(pathlib.Path(dl.value.path()).read_text(encoding="utf-8"))["state"] == RICH
    assert a.evaluate("()=>window.__pop") == []

    b = app(state={}, hash_="record")
    b.evaluate(POPUPS_JS)
    before = raw(b)
    offer(b, txt)
    ask = b.locator("#bkAsk")
    assert "Replace your progress with this backup?" in ask.inner_text()
    assert b.locator("#bkYes").is_visible() and b.locator("#bkNo").is_visible()
    assert raw(b) == before, "nothing may change before the confirm is answered"
    b.click("#bkYes")
    assert state(b) == RICH, "import must restore the full state"
    rec = text(b, "#v-record")
    assert "Your path: Keys" in rec and "B string buzzes" in rec, "page should re-render from the imported state"
    assert "imported" in text(b, "#bkMsg").lower() and b.locator("#bkYes").count() == 0
    assert json.loads(copy_backup(b))["state"] == RICH, "second export differs from the first"
    b.reload()
    b.wait_for_selector("#backup")
    assert state(b) == RICH and "Your path: Keys" in text(b, "#v-record"), "imported state must survive a reload"
    go(b, "gig")
    assert state(b) == RICH, "the gig plan came back in normal form"
    assert b.evaluate("()=>window.__pop||[]") == [] and not a.errors and not b.errors


def test_R1_import_accepts_a_raw_saved_state_and_old_saves(app):
    old = {"finish": "flam", "stage": "am-e7", "lv": {"a-e:0": 2}, "bpm": 84, "inst": "guitar",
           "changes": [{"d": TS, "st": "a-e", "pair": "A-E", "n": 20}], "journal": [{"d": TS, "st": "a-e", "h": "x", "o": "", "w": ""}],
           "gig": {"songs": ["g-boogie"], "bands": [{"name": "Band 1", "m": {}}], "block": 20, "rotate": True}}
    pg = app(state={}, hash_="record")
    offer(pg, json.dumps(old))            # exactly what an older build left in localStorage
    pg.click("#bkYes")
    s = state(pg)
    assert s["finish"] == "flam" and s["stage"] == "am-e7" and s["lv"] == {"a-e:0": 2} and s["bpm"] == 84
    assert s["changes"][0]["inst"] == "guitar" and s["journal"][0]["inst"] == "guitar", "pre-0.6 entries are guitar's"
    assert s["gig"]["songs"] == ["g-boogie"] and s["gig"]["useFin"] is False, "new field gets its default"
    assert not pg.errors
    # and the same old save still loads straight from storage
    pg2 = app(state=old, hash_="gig")
    s2 = state(pg2)
    assert s2["lv"] == {"a-e:0": 2} and s2["gig"]["useFin"] is False and s2["gig"]["songs"] == ["g-boogie"]
    assert not pg2.errors


BAD = [
    ("", r"nothing to import"),
    ("   ", r"nothing to import"),
    ("{not json", r"can't be read as JSON"),
    (json.dumps({"app": "The Guitar Lab", "format": 1, "state": RICH})[:-40], r"can't be read as JSON"),   # cut short
    ("[1,2,3]", r"isn't a Guitar Lab backup"),
    ('"hello"', r"isn't a Guitar Lab backup"),
    ("42", r"isn't a Guitar Lab backup"),
    ("null", r"isn't a Guitar Lab backup"),
    ('{"foo":1,"bar":[]}', r"none of the things this app saves"),
    ('{"lv":[1,2],"journal":[]}', r'damaged: "lv"'),
    ('{"lv":{},"journal":"none","bpm":"fast"}', r"damaged"),
    ('{"journal":[1,2]}', r"damaged"),
    (json.dumps({"app": "The Guitar Lab", "format": 99, "state": {"lv": {}}}), r"newer version"),
]


@pytest.mark.parametrize("bad,why", BAD)
def test_R1_bad_backup_is_rejected_and_changes_nothing(app, bad, why):
    pg = app(state=RICH, hash_="record")
    pg.evaluate(POPUPS_JS)
    before, shown = raw(pg), text(pg, "#v-record .card")
    offer(pg, bad)
    msg = pg.locator("#bkMsg .bkmsg.bad")
    assert msg.is_visible() and re.search(why, msg.inner_text(), re.I), msg.inner_text()
    assert "nothing has been changed" in msg.inner_text().lower() or "nothing to import" in msg.inner_text().lower()
    assert pg.locator("#bkYes").count() == 0, "no confirm for a bad backup"
    assert raw(pg) == before and text(pg, "#v-record .card") == shown
    assert json.loads(copy_backup(pg))["state"] == RICH, "state in memory changed"
    assert pg.evaluate("()=>window.__pop") == [] and not pg.errors


def test_R1_confirm_box_cancel_changes_nothing(app):
    pg = app(state=RICH, hash_="record")
    pg.evaluate(POPUPS_JS)
    before = raw(pg)
    other = dict(RICH, inst="bass", lv={}, journal=[])
    offer(pg, json.dumps(other))
    box = pg.locator("#bkAsk .bkask")
    assert box.is_visible() and "Replace your progress with this backup?" in box.inner_text()
    assert "can't be undone" in box.inner_text()
    assert pg.evaluate("()=>document.activeElement&&document.activeElement.id") == "bkNo", "Cancel should hold the focus"
    pg.click("#bkNo")
    assert pg.locator("#bkAsk .bkask").count() == 0
    assert raw(pg) == before and "Your path: Keys" in text(pg, "#v-record")
    assert "unchanged" in text(pg, "#bkMsg").lower()
    assert json.loads(copy_backup(pg))["state"] == RICH
    # a bad paste after a good one withdraws the question
    offer(pg, json.dumps(other))
    offer(pg, "{oops")
    assert pg.locator("#bkYes").count() == 0 and raw(pg) == before
    # leaving the tab withdraws it too
    offer(pg, json.dumps(other))
    go(pg, "path")
    go(pg, "record")
    assert pg.locator("#bkYes").count() == 0 and raw(pg) == before
    assert pg.evaluate("()=>window.__pop") == [] and not pg.errors


def test_R1_import_by_file_pick(app):
    pg = app(state={}, hash_="record")
    pg.evaluate(POPUPS_JS)
    payload = json.dumps({"app": "The Guitar Lab", "format": 1, "version": "0.7", "saved": "2026-11-27T01:00:00.000Z", "state": RICH})
    pg.set_input_files("#bkFile", {"name": "guitar-lab-backup-2026-11-27.json", "mimeType": "application/json", "buffer": payload.encode("utf-8")})
    pg.wait_for_selector("#bkYes")
    assert "27 Nov 2026" in text(pg, "#bkAsk"), "confirm should say when the backup was made"
    assert state(pg) != RICH
    pg.click("#bkYes")
    assert state(pg) == RICH
    pg.set_input_files("#bkFile", {"name": "notes.txt", "mimeType": "text/plain", "buffer": b"these are not the droids"})
    pg.wait_for_selector("#bkMsg .bkmsg.bad")
    assert state(pg) == RICH and pg.locator("#bkYes").count() == 0
    assert pg.evaluate("()=>window.__pop") == [] and not pg.errors


def test_R1_copy_falls_back_to_a_visible_textarea(app):
    pg = app(state=RICH, hash_="record")
    assert not pg.locator("#bkOut").is_visible()
    pg.evaluate(CLIP_BLOCKED_JS)
    pg.click("#bkCopy")
    pg.wait_for_selector("#bkOut", state="visible")
    assert json.loads(pg.input_value("#bkOut"))["state"] == RICH
    assert re.search(r"box above", text(pg, "#bkMsg"))
    sel = pg.evaluate("()=>{const t=document.getElementById('bkOut');return [document.activeElement===t,t.selectionStart,t.selectionEnd===t.value.length]}")
    assert sel == [True, 0, True], "the fallback text should be focused and selected"
    pg.evaluate("()=>{Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined})}")   # no clipboard API at all
    pg.click("#bkCopy")
    assert pg.locator("#bkOut").is_visible() and not pg.errors


def test_R1_download_uses_the_viewer_capability_when_present(app):
    pg = app(state=RICH, hash_="record")
    pg.evaluate("""()=>{window.__saves=[];window.__mode='ok';window.claude={use:async n=>n==='downloads'?Object.freeze({save:async r=>{window.__saves.push(r);
       if(window.__mode!=='ok')throw {code:window.__mode,message:'no'};return {status:'saved'}}}):null};
      window.__anch=0;const c=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){if(this.download)window.__anch++;return c.call(this)}}""")
    pg.click("#bkDown")
    pg.wait_for_function("()=>window.__saves.length===1")
    sv = pg.evaluate("()=>window.__saves[0]")
    assert re.fullmatch(r"guitar-lab-backup-\d{4}-\d\d-\d\d\.json", sv["filename"]) and json.loads(sv["data"])["state"] == RICH
    pg.wait_for_function("()=>/saved as/i.test(document.getElementById('bkMsg').textContent)")
    assert pg.evaluate("()=>window.__anch") == 0, "capability present: no blob link needed"
    pg.evaluate("()=>{window.__mode='declined'}")
    pg.click("#bkDown")
    pg.wait_for_function("()=>/cancelled/i.test(document.getElementById('bkMsg').textContent)")
    assert pg.evaluate("()=>window.__anch") == 0, "a declined save must not download behind the viewer's back"
    pg.evaluate("()=>{window.__mode='unavailable'}")
    with pg.expect_download() as dl:          # capability refuses: fall back to the plain link
        pg.click("#bkDown")
    assert dl.value.suggested_filename.endswith(".json") and not pg.errors


def test_R1_works_in_a_sandboxed_frame(browser, tmp_path):
    """Sandboxed iframe, no same-origin: storage, clipboard and downloads are all blocked. The panel must still export and import."""
    host = tmp_path / "host.html"
    host.write_text(f'<!doctype html><meta charset="utf-8"><iframe id="f" sandbox="allow-scripts" src="{URL}#record" style="width:1100px;height:1400px;border:0"></iframe>', encoding="utf-8")
    ctx = browser.new_context(viewport={"width": 1200, "height": 1500})
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(host.as_uri())
    fr = pg.frames[1]
    fr.wait_for_selector("#backup")
    assert fr.evaluate("()=>{try{localStorage.getItem('x');return 'open'}catch(e){return 'blocked'}}") == "blocked", "frame is not sandboxed"
    fr.evaluate(POPUPS_JS)
    fr.click("#bkDown")                      # blocked or not, it must not throw and must say something
    fr.wait_for_function("()=>document.getElementById('bkMsg').textContent.length>10")
    assert re.search(r"Copy backup", fr.inner_text("#bkMsg"))
    fr.click("#bkCopy")
    fr.wait_for_selector("#bkOut", state="visible")
    empty = json.loads(fr.input_value("#bkOut"))
    assert empty["state"]["lv"] == {} and empty["state"]["inst"] == "guitar"
    fr.fill("#bkIn", json.dumps({"app": "The Guitar Lab", "format": 1, "state": RICH}))
    fr.click("#bkImport")
    assert "Replace your progress with this backup?" in fr.inner_text("#bkAsk")
    fr.click("#bkYes")
    assert "Your path: Keys" in fr.inner_text("#v-record") and "B string buzzes" in fr.inner_text("#v-record")
    fr.click("#bkCopy")
    fr.wait_for_function("()=>{try{return JSON.parse(document.getElementById('bkOut').value).state.inst==='keys'}catch(e){return false}}")
    assert json.loads(fr.input_value("#bkOut"))["state"] == RICH, "round trip inside the sandbox is not lossless"
    fr.set_input_files("#bkFile", {"name": "b.json", "mimeType": "application/json", "buffer": json.dumps(dict(RICH, inst="drums")).encode()})
    fr.wait_for_selector("#bkYes")
    fr.click("#bkYes")
    assert "Your path: Drums" in fr.inner_text("#v-record")
    assert fr.evaluate("()=>window.__pop") == [] and not errs, errs
    ctx.close()


def test_R1_no_browser_popups_in_source():
    src = pathlib.Path(URL.replace("file://", "")).read_text(encoding="utf-8")
    assert not re.search(r"(?<![\w.$])(alert|confirm|prompt)\s*\(", src), "alert/confirm/prompt call in index.html"
    assert "'shredder'" in src and len(re.findall(r"localStorage\.(get|set)Item\('([^']+)'", src)) == 2
    assert {m[1] for m in re.findall(r"localStorage\.(get|set)Item\('([^']+)'", src)} == {"shredder"}
    assert not re.search(r"\b(fetch|XMLHttpRequest|WebSocket|sendBeacon|importScripts)\b", src), "network call in index.html"
    assert not re.search(r"<script[^>]+src=|<link[^>]+href=", src), "external script or stylesheet"


def test_version_label_is_0_9(app):
    pg = app(state={})
    assert pg.title() == "The Guitar Lab 0.9"
    assert "version 0.9" in text(pg, "header .sub")
    assert "0.6" not in pg.evaluate("()=>document.body.innerText")


# --------------------------------------------------------------------- R2

def hat_gaps(pg):
    """Play the open gig song for a moment and return the gaps between drum hits after the count-in."""
    n0 = len(starts(pg))
    pg.click("#playGig")
    pg.wait_for_timeout(5800)      # two bars of count-in at 120, then a bar and a bit of the song
    pg.click("#playGig")
    t = sorted({round(s["when"], 4) for s in starts(pg)[n0:] if s["kind"] == "buf" and s["dur"] and s["dur"] < 1})
    assert len(t) >= 4, "no drums scheduled"
    return [b - a for a, b in zip(t, t[1:])]


def test_R2_gig_song_keeps_its_own_feel(app):
    """Path set to the Flamenco feel (Tangos in 4/4): the gig boogie still plays its swung shuffle."""
    tangos = next(f for f in D["FIN"] if f["k"] == "flam")["p"]["4"]["n"]
    pg = app(state={"useFin": True, "finish": "flam", "stage": "twelve-bar", "gig": {"bpm": 120}}, hash_="gig")
    assert "12-bar boogie" in text(pg, "#gigSong .pd")
    assert pg.inner_text(".mbar .m-name") == PAT["shuffle"]["n"]
    assert pg.get_attribute('[data-gpat="0"]', "aria-pressed") == "true" and pg.get_attribute('[data-gpat="1"]', "aria-pressed") == "false"
    assert "Flamenco feel" not in text(pg, "#gigSong .rm"), "chart says the band plays the Path's feel"
    gaps = hat_gaps(pg)
    beat = 60 / 120
    assert min(gaps) < beat / 3 + 0.02 and any(abs(g - beat * 2 / 3) < 0.02 for g in gaps), f"boogie is not swung: {gaps[:8]}"
    go(pg, "twelve-bar")
    assert pg.inner_text(".mbar .m-name") == tangos, "Path keeps its Finish feel"
    s = state(pg)
    assert s["useFin"] is True and s["gig"]["useFin"] is False
    assert not pg.errors


def test_R2_gig_feel_switch_changes_gig_only(app):
    rock = next(f for f in D["FIN"] if f["k"] == "rock")["p"]["4"]["n"]
    tangos = next(f for f in D["FIN"] if f["k"] == "flam")["p"]["4"]["n"]
    pg = app(state={"useFin": False, "finish": "flam", "stage": "twelve-bar", "gig": {"bpm": 120}}, hash_="gig")
    assert "Flamenco feel" in text(pg, '[data-gpat="1"]')
    pg.click('[data-gpat="1"]')
    assert pg.get_attribute('[data-gpat="1"]', "aria-pressed") == "true"
    assert pg.inner_text(".mbar .m-name") == tangos
    assert "Flamenco feel" in text(pg, "#gigSong .rm")
    s = state(pg)
    assert s["gig"]["useFin"] is True and s["useFin"] is False, "the Gig switch must not move the Path's"
    gaps = hat_gaps(pg)
    assert min(gaps) > 0.45, f"Tangos is four to the bar at 120: {gaps[:8]}"
    go(pg, "twelve-bar")
    assert pg.inner_text(".mbar .m-name") == PAT["shuffle"]["n"]
    assert pg.get_attribute('#side [data-pat="0"]', "aria-pressed") == "true"
    pg.click('#side [data-pat="1"]')                 # and the Path's switch must not move the Gig's
    pg.click('[data-fin="rock"]')
    s = state(pg)
    assert s["useFin"] is True and s["gig"]["useFin"] is True
    go(pg, "gig")
    assert pg.inner_text(".mbar .m-name") == rock and "Rock and roll feel" in text(pg, '[data-gpat="1"]')
    pg.click('[data-gpat="0"]')
    s = state(pg)
    assert s["gig"]["useFin"] is False and s["useFin"] is True
    assert pg.inner_text(".mbar .m-name") == PAT["shuffle"]["n"]
    pg.click("#playGig")                             # switching feel mid-song stops the band
    pg.wait_for_timeout(400)
    pg.click('[data-gpat="1"]')
    assert text(pg, "#playGig") == "Play the chart" and "stopped" in toast(pg)
    assert not pg.errors


# --------------------------------------------------------------------- R3

PRESENT_JS = r"""()=>{const h=e=>e?e.getBoundingClientRect().height:0;
 const chord=[...document.querySelectorAll('#v-gig .rmap text')].filter(t=>/^[A-G][♯♭]?m?7?$/.test(t.textContent.trim()));
 const ph=[...document.querySelectorAll('#gigRun h3')].filter(e=>/^Phase \d/.test(e.textContent.trim()));
 const svg=document.querySelector('#v-gig .rmap');
 return {chord:Math.max(0,...chord.map(h)),nchord:document.querySelectorAll('#v-gig .rmap .rm-bar').length,phase:ph.length?parseFloat(getComputedStyle(ph[0]).fontSize):0,nphase:ph.length,
  sub:ph.length&&ph[0].querySelector('.note')?parseFloat(getComputedStyle(ph[0].querySelector('.note')).fontSize):0,
  svgW:svg?svg.getBoundingClientRect().width:0,cardW:svg?svg.closest('.card').getBoundingClientRect().width:0}}"""


@pytest.mark.parametrize("song", ["g-boogie", "g-bamba"])
@pytest.mark.parametrize("width", [360, 768, 1280])
def test_R3_present_mode_enlarges_chart_and_phase_headings(app, width, song):
    pg = app(width=width, state={"gig": {"open": song, "bands": [{"name": "Band 1", "m": {"guitar": "Player One", "bass": "Player Two"}}, {"name": "Band 2", "m": {}}]}}, hash_="gig")
    a = pg.evaluate(PRESENT_JS)
    assert a["nchord"] and a["nphase"] == 4
    pg.click("#present")
    b = pg.evaluate(PRESENT_JS)
    assert b["nchord"] == a["nchord"] and b["nphase"] == 4, "Present mode lost part of the chart or run sheet"
    assert b["chord"] >= a["chord"] * 1.5, f"chart chords {a['chord']:.1f}px -> {b['chord']:.1f}px"
    assert b["phase"] >= a["phase"] * 1.35, f"phase heading {a['phase']}px -> {b['phase']}px"
    assert b["sub"] > a["sub"]
    if width >= 768:
        assert b["chord"] >= 26 and b["phase"] >= 22, "not readable from the back of a room"
    assert b["svgW"] <= b["cardW"] + 1
    over = pg.evaluate(OVERFLOW_JS)
    assert not over, over
    assert pg.get_attribute("#present", "aria-pressed") == "true"
    pg.click("#playGig")                     # the enlarged chart still follows the band
    pg.wait_for_function("()=>document.querySelector('#v-gig .rm-bar.now')", timeout=8000)
    pg.click("#playGig")
    pg.click("#present")
    c = pg.evaluate(PRESENT_JS)
    assert abs(c["chord"] - a["chord"]) < 0.5 and c["phase"] == a["phase"], "leaving Present mode should restore the sizes"
    assert not pg.evaluate(OVERFLOW_JS) and not pg.errors


def test_R3_present_mode_does_not_touch_the_path_chart(app):
    pg = app(width=1280, state={}, hash_="gig")
    go(pg, "path")
    before = pg.evaluate("()=>document.querySelectorAll('#stage .rmap .rm-bar').length+':'+document.querySelector('#stage .rmap').getAttribute('viewBox')")
    go(pg, "gig")
    pg.click("#present")
    go(pg, "path")
    assert not pg.evaluate("()=>document.body.classList.contains('present')")
    assert pg.evaluate("()=>document.querySelectorAll('#stage .rmap .rm-bar').length+':'+document.querySelector('#stage .rmap').getAttribute('viewBox')") == before


# --------------------------------------------------------------------- R4

SEEN_JS = "()=>document.body.innerText+' '+[...document.querySelectorAll('[aria-label],[title],[placeholder]')].map(e=>(e.getAttribute('aria-label')||'')+' '+(e.getAttribute('title')||'')+' '+(e.getAttribute('placeholder')||'')).join(' ')"


def walk(pg):
    """Every stage on the Path, then every other tab (each gig song opened): yields (where, visible text + labels)."""
    for s in ST:
        go(pg, s["id"])
        yield s["id"], pg.evaluate(SEEN_JS)
    for tab in TABS[1:]:
        go(pg, tab)
        yield tab, pg.evaluate(SEEN_JS)
        if tab == "gig":
            for g in GIGS:
                pg.click(f'[data-gopen="{g["id"]}"][data-gview]')
                yield "gig/" + g["id"], pg.evaluate(SEEN_JS)


@pytest.mark.parametrize("inst", INSTS)
def test_R4_quavers_not_eighths(app, inst):
    bad = []
    for fin in [f["k"] for f in D["FIN"]]:
        pg = app(state={"inst": inst, "finish": fin, "useFin": True, "gig": {"useFin": True}})
        for where, t in walk(pg):
            for m in re.finditer(r".{0,30}\b(eighth|sixteenth|quarter note|half note)s?\b.{0,20}", t, re.I):
                bad.append(f"{inst}/{fin}/{where}: {m.group(0)!r}")
        assert not pg.errors
        pg.context.close()
    assert not bad, "\n".join(bad[:20])
    names = [p["n"] for p in PAT.values()] + [p["n"] for f in D["FIN"] for p in f["p"].values()]
    assert not [n for n in names if re.search(r"eighth", n, re.I)], names
    assert PAT["eighths"]["n"] == "Straight quavers"


# --------------------------------------------------------------------- R5

def changes_card(pg):
    return pg.evaluate("()=>{const c=[...document.querySelectorAll('#side .card')].find(c=>/One-minute changes/.test(c.textContent));return c?c.innerText:''}")


@pytest.mark.parametrize("inst", ["bass", "keys"])
def test_R5_changes_card_follows_capo(app, inst):
    pg = app(state={"inst": inst, "stage": "a-e"})
    assert "A ↔ E" in changes_card(pg)
    for capo, pair in [(1, "B♭ ↔ F"), (2, "B ↔ F♯"), (3, "C ↔ G")]:
        pg.click('[data-capo="1"]')
        card = changes_card(pg)                       # read straight away: no tab change, no reload
        assert pair in card and "A ↔ E" not in card, f"capo {capo}: card reads {card[:60]!r}"
    for _ in range(3):
        pg.click('[data-capo="-1"]')
    assert "A ↔ E" in changes_card(pg)
    go(pg, "beyond")
    pg.click('[data-capo="1"]')
    assert "Cm ↔ G" in changes_card(pg), "B minor / F♯ up one fret is C minor / G"
    assert not pg.errors


def test_R5_guitar_changes_card_keeps_shapes(app):
    pg = app(state={"stage": "a-e"})
    pg.click('[data-capo="1"]')
    assert "A ↔ E" in changes_card(pg), "the guitarist still fingers A and E with a capo on"
    pg.fill("#cnt", "33")
    pg.click("#logChg")
    pg.click('[data-capo="1"]')
    assert "Best: 33" in changes_card(pg), "logged changes lost on capo change"


# --------------------------------------------------------------------- R7

COL_JS = r"""()=>{const p=document.createElement('i');document.body.appendChild(p);const v=n=>{p.style.color='var('+n+')';return getComputedStyle(p).color};
 const out={dom:v('--dom'),sub:v('--sub'),ton:v('--ton'),pre:v('--pre'),sec:v('--sec'),card:getComputedStyle(document.querySelector('.card')).backgroundColor,box:{},map:{},rows:[]};p.remove();
 document.querySelectorAll('#stage .cb[data-strum]').forEach(b=>{out.box[b.dataset.strum]={rn:getComputedStyle(b.querySelector('.rn')).color,name:getComputedStyle(b.querySelector('svg text')).fill,dot:getComputedStyle(b.querySelector('svg circle[r="5.6"]')||b.querySelector('svg text')).fill,label:b.querySelector('.rn').innerText}});
 document.querySelectorAll('#stage .rmap text').forEach(t=>{const s=t.textContent.trim();if(/^[A-G][♯♭]?m?7?$/.test(s))out.map[s]=getComputedStyle(t).fill});
 document.querySelectorAll('#side .fk > div').forEach(d=>out.rows.push([d.innerText.trim(),getComputedStyle(d.querySelector('.sw')).backgroundColor]));return out}"""


@pytest.mark.parametrize("scheme,dom", [("dark", "rgb(208, 87, 75)"), ("light", "rgb(168, 53, 43)")])
@pytest.mark.parametrize("stage,sub,dominant", [("six-eight", "G", "E"), ("beyond", "A", "F#")])
def test_R7_subtonic_not_coloured_dominant(app, scheme, dom, stage, sub, dominant):
    pg = app(scheme=scheme, state={"stage": stage}, hash_=stage)
    c = pg.evaluate(COL_JS)
    assert c["dom"] == dom, "the dominant colour itself must not change (Q2 is still open)"
    assert c["sub"] not in (c["dom"], c["ton"], c["pre"], c["sec"])
    b = c["box"][sub]
    assert b["rn"] == b["name"] == b["dot"] == c["sub"], f"{sub} (VII) should be the subtonic colour everywhere on its box: {b}"
    assert "VII" in b["label"] and "subtonic" in b["label"] and "dominant" not in b["label"]
    d = c["box"][dominant]
    assert d["rn"] == d["name"] == d["dot"] == c["dom"] and "dominant" in d["label"], f"{dominant} is the true dominant: {d}"
    pretty = lambda n: n.replace("#", "♯")
    assert c["map"][pretty(sub)] == c["sub"] and c["map"][pretty(dominant)] == c["dom"], "chart colours disagree with the boxes"
    rows = dict((r[0].split(":")[0], r) for r in c["rows"])
    assert rows["Subtonic"][0] == "Subtonic: " + pretty(sub) and rows["Subtonic"][1] == c["sub"]
    assert pretty(dominant) in pretty(rows["Dominant"][0]) and pretty(sub) not in rows["Dominant"][0].split(":")[1] and rows["Dominant"][1] == c["dom"]
    assert contrast(c["sub"], c["card"]) >= 4.5, "subtonic colour too faint"
    assert not pg.errors


def test_R7_true_dominant_E7_still_dominant(app):
    pg = app(state={"stage": "am-e7"}, hash_="am-e7")
    c = pg.evaluate(COL_JS)
    assert c["box"]["E7"]["rn"] == c["dom"] and c["map"]["E7"] == c["dom"]
    assert not [r for r in c["rows"] if r[0].startswith("Subtonic")]


def test_R6_greensleeves_chart_and_band_agree(app):
    """Bar 3 of the verse reads Am on the chart, and the band's bass plays A (not F) in that bar."""
    bpm = 120
    pg = app(state={"stage": "six-eight", "bpm": bpm}, hash_="six-eight")
    label = pg.get_attribute("#stage .rmap", "aria-label")
    assert "Verse, 8 bars: Am G Am E Am G Am E Am" in label
    shown = pg.evaluate("()=>[...document.querySelectorAll('#stage .rmap text')].map(t=>t.textContent.trim()).filter(s=>/^[A-G][♯♭]?m?7?$/.test(s))")
    assert shown[:4] == ["Am", "G", "Am", "E"] and "F" not in shown
    boxes = pg.evaluate("()=>[...document.querySelectorAll('#stage .cb[data-strum]')].map(b=>b.dataset.strum)")
    assert boxes == ["Am", "G", "E", "C"], "the stage should teach exactly the chords on its chart"
    pg.click("#playMap")
    pg.wait_for_timeout(3600)
    pg.click("#playMap")
    beat = 60 / bpm
    bass = sorted((s["when"], s["freq"]) for s in starts(pg) if s["type"] == "triangle")
    t0 = bass[0][0]
    by_bar = {}
    for when, f in bass:
        by_bar.setdefault(int((when - t0) / (2 * beat) + 0.05), f)
    a1, g1, f1, e1 = 55.0, 48.999, 43.654, 41.203
    assert abs(by_bar[0] - a1) < 0.3 and abs(by_bar[1] - g1) < 0.3
    assert abs(by_bar[2] - a1) < 0.3, f"bar 3 bass is {by_bar[2]:.2f} Hz (F would be {f1})"
    assert abs(by_bar[3] - e1) < 0.3
    go(pg, "technique")
    assert pg.locator('#v-technique .cb[data-strum="F"]').count() >= 1, "the Andalusian cadence keeps its F"
    assert not pg.errors


# --------------------------------------------------------------------- R8

DRUM_JS = "()=>[...document.querySelectorAll('#stage .dg, #stage .dgw + p.note, #gigPart .dg, #gigPart .dgw + p.note')].map(e=>(e.getAttribute('aria-label')||'')+' '+e.innerText).join(' ')"
STRUM_WORDS = r"\bstrum|\bdowns?\b|\bups?\b|\bDU\b|\bUDU\b|D ·|thumb|palm|\bchords (on|between)|\bbass, |\beighth|compás"


def test_R8_drum_panel_uses_drum_words(app):
    bad, seen = [], set()
    for fin, use in [("bossa", False)] + [(f["k"], True) for f in D["FIN"]]:
        pg = app(state={"inst": "drums", "finish": fin, "useFin": use, "gig": {"useFin": use}})
        spots = [s["id"] for s in ST] + ["gig"]
        for where in spots:
            go(pg, where)
            t = pg.evaluate(DRUM_JS)
            seen.add(t)
            if not re.search(r"\bhats\b", t) or not re.search(r"\bkick on 1\b", t):
                bad.append(f"{fin}/{use}/{where}: groove not described in drum words: {t[-200:]!r}")
            for m in re.finditer(STRUM_WORDS, t, re.I):
                bad.append(f"{fin}/{use}/{where}: {m.group(0)!r} in {t[max(0, m.start() - 40):m.end() + 20]!r}")
        assert not pg.errors
        pg.context.close()
    assert not bad, "\n".join(bad[:20])
    pg = app(state={"inst": "drums"})
    want = {"a-e": "hats on every beat, snare on 2 and 4, kick on 1 and 3",
            "twelve-bar": "hats in swung quavers, snare on 2 and 4, kick on 1 and 3",
            "c-g-f": "hats on every beat, rim click on 2 and 3, kick on 1",
            "six-eight": "hats on all six quavers, snare on 4, kick on 1"}
    for sid, words in want.items():
        go(pg, sid)
        assert words in pg.evaluate(DRUM_JS), f"{sid}: {pg.evaluate(DRUM_JS)[-220:]!r}"
        assert words in pg.get_attribute("#stage .dg", "aria-label")


# --------------------------------------------------------------------- R9

def test_R9_f_sharp_uses_the_proper_sign(app):
    bad = []
    for inst in ["guitar", "bass"]:
        pg = app(state={"inst": inst, "stage": "beyond"}, hash_="beyond")
        fk = text(pg, "#side .fk")
        assert "Dominant: F♯" in fk, fk
        for where, t in walk(pg):
            if where == "invent":
                assert re.search(r"Pool: .*F♯", t), "Invent pool should list F♯"
            for m in re.finditer(r".{0,25}[A-G]#.{0,10}", t):
                bad.append(f"{inst}/{where}: {m.group(0)!r}")
        pg.context.close()
    assert not bad, "\n".join(bad[:20])
    pg = app(state={"stage": "beyond"}, hash_="invent")
    for _ in range(40):                                     # roll until F♯ comes up, then save the loop
        pg.click("#roll")
        if pg.locator('#v-invent .cb[data-strum="F#"]').count():
            break
    assert pg.locator('#v-invent .cb[data-strum="F#"]').count(), "F♯ never rolled"
    pg.click("#keepLoop")
    go(pg, "record")
    j = text(pg, "#v-record .log")
    assert "F♯" in j and "#" not in j, j


def test_R9_la_bamba_bar_reference_fits_its_loop(app):
    pg = app(state={}, hash_="gig")
    pg.click('[data-gopen="g-bamba"][data-gview]')
    t = text(pg, "#gigSong")
    assert "Loop, 4 bars" in pg.get_attribute("#gigSong .rmap", "aria-label")
    assert not re.search(r"bars? (10|12)|bars 10 and 12", t), "La Bamba's loop has four bars"
    assert re.search(r"same four bars", t)
    for g in [x for x in GIGS if x["id"] != "g-bamba"]:     # the 12-bar songs keep their real caveat
        pg.click(f'[data-gopen="{g["id"]}"][data-gview]')
        assert "bars 10 and 12" in text(pg, "#gigSong"), g["id"]
    assert not pg.errors


@pytest.mark.parametrize("inst", INSTS)
def test_R9_bpm_label_is_tidy(app, inst):
    pg = app(state={"inst": inst})
    for sid in ["six-eight", "hallelujah", "a-e"]:
        go(pg, sid)
        t = pg.evaluate("()=>document.body.innerText")
        assert "(bpm (" not in t and "))" not in t, sid
        nested = re.findall(r"\([^()\n]*\([^()\n]*\)[^()\n]*\)", t)
        assert not nested, f"{sid}: nested brackets {nested[:3]}"
        row = pg.evaluate("()=>document.getElementById('playMap').parentElement.innerText")
        if sid == "a-e":
            assert "dotted crotchet" not in row
        else:
            assert "counts the dotted crotchet" in row, row
            assert "bpm (dotted crotchet)" in pg.inner_text(".mbar"), "the metronome bar still names the unit"


# --------------------------------------------------------------------- R10

def lit_black(pg, chord):
    k = pg.evaluate(KBD_JS, chord)
    lb = [x for x in k["labels"] if not x["white"] and re.fullmatch(r"[A-G][♯♭]", x["s"])]
    assert lb, "no lit black key on " + chord
    return lb[0], k


@pytest.mark.parametrize("chord", ["A", "E"])
def test_R10_lit_black_key_contrast_in_light_mode(app, chord):
    light = app(scheme="light", state={"inst": "keys"})
    dark = app(scheme="dark", state={"inst": "keys"})
    l, kl = lit_black(light, chord)
    d, kd = lit_black(dark, chord)
    # 0.8 (T1): the keyboard is drawn cream in both themes, so dark mode now uses the darker gold too.
    assert l["key"] == d["key"], "the keyboard looks the same in both themes, so the lit black keys should too"
    assert _lum([float(x) for x in re.findall(r"[\d.]+", l["key"])[:3]]) < _lum([240, 212, 138])
    assert l["key"] != kl["unlitWhite"]
    cw = contrast(l["key"], kl["unlitWhite"])
    assert cw >= 3, f"lit black key {l['key']} vs cream white key {kl['unlitWhite']}: contrast {cw:.2f} < 3"
    assert contrast(l["key"], kl["unlitBlack"]) >= 3, "lit black key must still stand out from the unlit black keys"
    assert contrast(l["fill"], l["key"]) >= 4.5, "note name on the lit black key"
    was = contrast("rgb(240, 212, 138)", kl["unlitWhite"])
    assert cw > was * 2, f"contrast against the white keys should be clearly better than 0.6's {was:.2f}"


def test_R10_follows_the_page_theme_not_just_the_os(app):
    pg = app(scheme="dark", state={"inst": "keys"})
    pg.evaluate("()=>{document.documentElement.dataset.theme='light'}")
    l, _ = lit_black(pg, "A")
    assert l["key"] != "rgb(240, 212, 138)"


# --------------------------------------------------------------------- R11

ODD_NOTES = {"C♭": "B", "F♭": "E", "B♯": "C", "E♯": "F"}
SPELL_JS = r"""()=>{const st=document.getElementById('stage'),n=[...st.querySelectorAll('.spell-note')].filter(e=>e.getClientRects().length);
 const shown=[...st.querySelectorAll('svg.kb')].map(s=>s.getAttribute('aria-label')).join(' ')+' '+[...st.querySelectorAll('.bcard, .solfa')].map(e=>e.innerText).join(' ');
 return {notes:n.map(e=>e.innerText),count:n.length,lines:n.map(e=>Math.round(e.getBoundingClientRect().height/parseFloat(getComputedStyle(e).lineHeight))),shown}}"""


@pytest.mark.parametrize("inst", ["keys", "bass", "vocals"])
def test_R11_spelling_note_only_when_needed(app, inst):
    bad, hits = [], 0
    for capo in range(0, 8):
        pg = app(width=1280, state={"inst": inst, "capo": {s["id"]: capo for s in ST} if capo else {}})
        for s in ST:
            go(pg, s["id"])
            r = pg.evaluate(SPELL_JS)
            odd = sorted(set(re.findall(r"C♭|F♭|B♯|E♯", r["shown"])))
            where = f"{inst} {s['id']} capo {capo}"
            if odd and r["count"] != 1:
                bad.append(f"{where}: {odd} shown but {r['count']} notes")
            elif not odd and r["count"]:
                bad.append(f"{where}: note with nothing to explain: {r['notes']}")
            elif odd:
                hits += 1
                for o in odd:
                    if f"{o} is the same pitch as {ODD_NOTES[o]}" not in r["notes"][0]:
                        bad.append(f"{where}: note does not explain {o}: {r['notes'][0]!r}")
                if inst == "keys" and r["lines"][0] > 2:
                    bad.append(f"{where}: note runs to {r['lines'][0]} lines")
        assert not pg.errors
        pg.context.close()
    assert not bad, "\n".join(bad[:20])
    assert hits, "no case exercised"


def test_R11_b_minor_capo_4_explains_c_flat(app):
    pg = app(state={"inst": "keys", "stage": "beyond", "capo": {"beyond": 4}}, hash_="beyond")
    assert "sounds in E♭ minor" in text(pg, "#stage")
    note = text(pg, "#stage .spell-note")
    assert "C♭ is the same pitch as B" in note and "E♭ minor" in note
    for _ in range(4):
        pg.click('[data-capo="-1"]')
    assert pg.locator("#stage .spell-note").count() == 0, "no note in plain B minor"
    pg2 = app(state={"stage": "beyond", "capo": {"beyond": 4}}, hash_="beyond")
    assert pg2.locator("#stage .spell-note").count() == 0, "guitar shows shapes, so no spelling note"


# ===================================================================== 0.8 register (SPEC_08): T1-T5

def _rgb(c):
    return [float(x) for x in re.findall(r"[\d.]+", c)[:3]]


def _hue(c):
    import colorsys
    r, g, b = [v / 255 for v in _rgb(c)]
    h, s_, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s_


def css_colour(pg, var):
    return pg.evaluate("v=>{const e=document.createElement('i');e.style.color='var('+v+')';document.body.appendChild(e);const c=getComputedStyle(e).color;e.remove();return c}", var)


# --------------------------------------------------------------------- T1

@pytest.mark.parametrize("scheme", ["light", "dark"])
@pytest.mark.parametrize("chord", ["A", "E"])
def test_T1_lit_black_key_stands_out_in_both_themes(app, scheme, chord):
    pg = app(scheme=scheme, state={"inst": "keys"})
    lb, k = lit_black(pg, chord)
    key = lb["key"]
    assert k["unlitWhite"] == "rgb(236, 226, 200)", "white keys are cream in both themes"
    cw = contrast(key, k["unlitWhite"])
    assert cw >= 3, f"{scheme}: lit black key {key} vs white key {k['unlitWhite']}: {cw:.2f} < 3"
    assert key != k["unlitBlack"] and contrast(key, k["unlitBlack"]) >= 3, "lit black key must stand out from the unlit black keys"
    assert contrast(lb["fill"], key) >= 4.5, "note name on the lit black key"
    dom, sub = css_colour(pg, "--dom"), css_colour(pg, "--sub")
    assert dom == ("rgb(168, 53, 43)" if scheme == "light" else "rgb(208, 87, 75)"), "Q2: dominant colour must not change"
    assert key not in (dom, sub), "lit black key must not be the dominant or subtonic colour"
    h, sat = _hue(key)
    assert 30 <= h <= 55 and sat >= 0.6, f"lit black key should read as gold, got hue {h:.0f} saturation {sat:.2f}"
    assert abs(h - _hue(dom)[0]) >= 25, "too close to the dominant red"
    assert sat - _hue(sub)[1] >= 0.4, "too close to the muted subtonic ivory-brown"


def test_T1_lit_black_key_follows_a_forced_theme(app):
    pg = app(scheme="light", state={"inst": "keys"})
    pg.evaluate("()=>{document.documentElement.dataset.theme='dark'}")
    lb, k = lit_black(pg, "A")
    assert contrast(lb["key"], k["unlitWhite"]) >= 3


# --------------------------------------------------------------------- T2

DG_JS = r"""()=>{const w=document.querySelector('#v-gig .dgw'),t=w&&w.querySelector('table');if(!t||!t.getClientRects().length)return null;
 const td=t.querySelector('td'),r=t.getBoundingClientRect();
 return {sw:w.scrollWidth,cw:w.clientWidth,tw:r.width,th:r.height,fs:parseFloat(getComputedStyle(td).fontSize),cell:td.getBoundingClientRect().width,
   heads:[...t.rows[0].cells].map(c=>c.textContent.trim()),rows:[...t.rows].slice(1).map(x=>x.cells[0].textContent.trim()),
   lines:[...t.rows].map(x=>{const c=x.cells[0],r=document.createRange();r.selectNodeContents(c);return r.getClientRects().length})}}"""


@pytest.mark.parametrize("width", [320, 360, 390, 480, 481, 500, 600, 601, 768, 1280])
def test_T2_present_drum_grid_fits_without_sideways_scroll(app, width):
    pg = app(width=width, state={"inst": "drums"}, hash_="gig")
    before = pg.evaluate(DG_JS)
    assert before, "no drum grid on the Gig tab"
    pg.click("#present")
    g = pg.evaluate(DG_JS)
    assert g["sw"] <= g["cw"] + 1, f"{width}px Present: drum grid scrolls sideways in its card ({g['sw']} > {g['cw']})"
    assert not pg.evaluate(OVERFLOW_JS), "page overflows"
    assert g["heads"] == before["heads"] and g["rows"] == before["rows"] and "Kick" in g["rows"], "grid lost a column or row"
    assert max(g["lines"]) <= 1, "row labels should stay on one line"
    assert g["fs"] >= 12, f"grid text too small to read ({g['fs']}px)"
    assert g["tw"] >= min(before["tw"], g["cw"]) - 1, "Present mode should only shrink the grid as far as it must to fit"
    if width >= 768:
        assert g["fs"] >= before["fs"] * 1.3 and g["tw"] >= before["tw"] * 1.3, "larger screens keep the enlarged look"
    assert not pg.errors


def test_T2_present_drum_grid_still_enlarged_at_1280(app):
    pg = app(width=1280, state={"inst": "drums"}, hash_="gig")
    before = pg.evaluate(DG_JS)
    pg.click("#present")
    g = pg.evaluate(DG_JS)
    assert g["fs"] > before["fs"] * 1.5 and g["cell"] > before["cell"] * 1.3 and g["th"] > before["th"] * 1.3, (before, g)
    pg.click("#present")
    assert pg.evaluate(DG_JS)["fs"] == before["fs"], "leaving Present restores the normal grid"


# --------------------------------------------------------------------- T4

T4_STRUM = re.compile(r"\bdowns\b|down-up|strum|\bD down\b|\bU up\b", re.I)
SIDE_JS = "()=>[...document.querySelectorAll('#side .card')].map(c=>[(c.querySelector('h3')||{textContent:''}).textContent.trim(),c.innerText])"


def metro_card(pg):
    return next(t for h, t in pg.evaluate(SIDE_JS) if h == "Metronome")


def fn_card(pg):
    return next(t for h, t in pg.evaluate(SIDE_JS) if h == "Function in this stage")


@pytest.mark.parametrize("use_fin", [False, True])
def test_T4_drums_never_see_strum_names(app, use_fin):
    pg = app(state={"inst": "drums", "useFin": use_fin})
    bad = []
    for s in ST:
        go(pg, s["id"])
        bar, card = pg.inner_text(".mbar"), metro_card(pg)
        for where, t in (("metronome bar", bar), ("metronome card", card)):
            m = T4_STRUM.search(t)
            if m:
                bad.append(f"{s['id']} {where}: {m.group(0)!r}")
        name = pg.inner_text(".mbar .m-name")
        if not re.search(r"groove", name, re.I) or not re.search(r"hats", name) or not re.search(r"kick", name):
            bad.append(f"{s['id']}: bar should name the groove, got {name!r}")
        if name not in card:
            bad.append(f"{s['id']}: card and bar disagree")
        for n in {PAT[s["pat"]]["n"]}:
            if n in bar or n in card:
                bad.append(f"{s['id']}: still shows {n!r}")
        cells = pg.evaluate("()=>[...document.querySelectorAll('#side .grid .cell')].map(c=>c.textContent.trim())")
        if not cells or any(not re.fullmatch(r"\d+|&", c) for c in cells):
            bad.append(f"{s['id']}: metronome cells should be counts, got {cells}")
    go(pg, "gig")
    if T4_STRUM.search(pg.inner_text(".mbar")) or "Groove" not in pg.inner_text(".mbar .m-name"):
        bad.append("gig bar: " + pg.inner_text(".mbar .m-name"))
    assert not bad, bad
    assert not pg.errors


def test_T4_drum_wording_matches_the_grid_and_follows_the_instrument(app):
    pg = app(state={"inst": "guitar", "stage": "a-e"}, hash_="a-e")
    assert pg.inner_text(".mbar .m-name") == PAT[ST[0]["pat"]]["n"], "guitar keeps its strum name"
    assert "D down" in metro_card(pg)
    pg.click('#stage [data-inst="drums"]')
    pg.wait_for_function("()=>/Groove/.test(document.querySelector('.mbar .m-name').textContent)")
    name = pg.inner_text(".mbar .m-name")
    label = pg.get_attribute("#stage table.dg", "aria-label")
    assert name.split(": ", 1)[1] in label, f"bar {name!r} should use the same words as the drum grid ({label!r})"
    go(pg, "rudiments")
    assert pg.inner_text(".mbar .m-name") == "Plain click"
    go(pg, "a-e")
    pg.click('#stage [data-inst="guitar"]')
    assert pg.inner_text(".mbar .m-name") == PAT[ST[0]["pat"]]["n"]


@pytest.mark.parametrize("inst", ["bass", "keys"])
def test_T4_function_card_shows_sounding_names_with_a_capo(app, inst):
    pg = app(state={"inst": inst, "stage": "a-e", "capo": {"a-e": 2}}, hash_="a-e")
    card = fn_card(pg)
    rows = pg.evaluate("()=>[...document.querySelectorAll('#side .fk > div')].map(d=>{const c=d.cloneNode(true);c.querySelectorAll('.note').forEach(n=>n.remove());return [c.textContent.trim(),(d.querySelector('.note')||{}).textContent||'']})")
    main = " | ".join(r[0] for r in rows)
    assert re.search(r"Tonic: B\b", main) and re.search(r"Dominant: F♯", main), f"{inst} capo 2 should read B and F♯, got {main!r}"
    assert not re.search(r":\s*(A|E)\b", main), f"guitar shape names still lead the rows: {main!r}"
    notes = [r[1] for r in rows]
    assert notes == ["Chart shows A", "Chart shows E"], notes
    assert "Chart shows" in card
    pg.click('#stage [data-inst="guitar"]')
    g = fn_card(pg)
    assert re.search(r"Tonic: A\b", g) and re.search(r"Dominant: E\b", g) and "Chart shows" not in g, "guitar keeps its shapes: " + g


@pytest.mark.parametrize("inst", ["bass", "keys", "guitar", "drums"])
def test_T4_function_card_unchanged_without_a_capo(app, inst):
    pg = app(state={"inst": inst, "stage": "a-e"}, hash_="a-e")
    card = fn_card(pg)
    assert re.search(r"Tonic: A\b", card) and re.search(r"Dominant: E\b", card) and "Chart shows" not in card, card


# --------------------------------------------------------------------- T3, T5 (sandboxed frame)

def sandbox(browser, tmp_path, hash_="record", sel="#backup"):
    """The app inside <iframe sandbox="allow-scripts">: storage, clipboard and downloads are all blocked. Returns (ctx, page, frame, log)."""
    host = tmp_path / "host.html"
    host.write_text(f'<!doctype html><meta charset="utf-8"><iframe id="f" sandbox="allow-scripts" src="{URL}#{hash_}" style="width:1100px;height:1400px;border:0"></iframe>', encoding="utf-8")
    ctx = browser.new_context(viewport={"width": 1200, "height": 1500})
    pg = ctx.new_page()
    log = []
    pg.on("console", lambda m: log.append(m.type + ": " + m.text) if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: log.append("pageerror: " + str(e)))
    pg.goto(host.as_uri())
    fr = pg.frames[1]
    fr.wait_for_selector(sel)
    assert fr.evaluate("()=>{try{localStorage.getItem('x');return 'open'}catch(e){return 'blocked'}}") == "blocked", "frame is not sandboxed"
    return ctx, pg, fr, log


MADE = re.compile(r"file (was |has been |is )?(made|saved|downloaded|created)|saved as|downloaded", re.I)


def test_T3_sandbox_import_does_not_claim_it_was_saved(browser, tmp_path):
    ctx, pg, fr, log = sandbox(browser, tmp_path)
    fr.evaluate(POPUPS_JS)
    fr.fill("#bkIn", json.dumps({"app": "The Guitar Lab", "format": 1, "version": "0.7", "state": RICH}))
    fr.click("#bkImport")
    fr.click("#bkYes")
    msg = fr.inner_text("#bkMsg")
    assert "Backup imported" in msg and "Your path: Keys" in fr.inner_text("#v-record"), "the import itself must still work"
    assert "saved in this browser" not in msg, msg
    assert re.search(r"this visit only", msg) and re.search(r"Keep your backup file", msg) and "Download backup" in msg, msg
    assert fr.evaluate("()=>window.__pop") == []
    ctx.close()


def test_T3_sandbox_download_does_not_claim_a_file_was_made(browser, tmp_path):
    ctx, pg, fr, log = sandbox(browser, tmp_path)
    fr.click("#bkDown")
    fr.wait_for_function("()=>document.getElementById('bkMsg').textContent.length>10")
    msg = fr.inner_text("#bkMsg")
    assert "Copy backup" in msg and re.search(r"If no file appeared", msg), msg
    lead = msg.split("If no file appeared")[0]
    assert not MADE.search(lead) and "Look in your downloads" not in lead, f"claims a file before the fallback hint: {lead!r}"
    assert re.search(r"guitar-lab-backup-\d{4}-\d\d-\d\d\.json", msg), "still names the file to look for"
    ctx.close()


def test_T3_normal_page_messages_still_correct(app):
    pg = app(state={}, hash_="record")
    offer(pg, json.dumps({"app": "The Guitar Lab", "format": 1, "version": "0.7", "state": RICH}))
    pg.click("#bkYes")
    msg = text(pg, "#bkMsg")
    assert "saved in this browser" in msg and "this visit only" not in msg, msg
    assert state(pg) == RICH, "and it really was saved"
    with pg.expect_download() as dl:
        pg.click("#bkDown")
    assert re.fullmatch(r"guitar-lab-backup-\d{4}-\d\d-\d\d\.json", dl.value.suggested_filename)
    m2 = text(pg, "#bkMsg")
    assert dl.value.suggested_filename in m2 and "Copy backup" in m2
    assert not MADE.search(m2.split("If no file appeared")[0]), m2
    assert json.loads(pathlib.Path(dl.value.path()).read_text(encoding="utf-8"))["version"] == "0.9"
    assert not pg.errors


def test_T3_storage_blocked_on_a_normal_page_is_also_honest(app):
    pg = app(state={}, hash_="record")
    pg.evaluate("()=>{Storage.prototype.setItem=function(){throw new DOMException('full','QuotaExceededError')}}")
    offer(pg, json.dumps(RICH))
    pg.click("#bkYes")
    msg = text(pg, "#bkMsg")
    assert "saved in this browser" not in msg and "this visit only" in msg, msg
    assert not pg.errors


def test_T5_sandbox_copy_is_quiet(browser, tmp_path):
    ctx, pg, fr, log = sandbox(browser, tmp_path)
    blocked = fr.evaluate("()=>{const p=document.permissionsPolicy||document.featurePolicy;return !!p&&!p.allowsFeature('clipboard-write')}")
    assert blocked, "this frame should have the clipboard blocked by policy"
    n = len(log)
    fr.click("#bkCopy")
    fr.wait_for_selector("#bkOut", state="visible")
    assert json.loads(fr.input_value("#bkOut"))["app"] == "The Guitar Lab"
    assert len(fr.inner_text("#bkMsg")) > 10
    pg.wait_for_timeout(300)
    assert log[n:] == [], f"Copy backup left console messages: {log[n:]}"
    fr.click("#bkCopy")                       # a second press is just as quiet
    pg.wait_for_timeout(200)
    assert log[n:] == [], log[n:]
    ctx.close()


def test_T5_sandbox_gig_copy_is_quiet(browser, tmp_path):
    ctx, pg, fr, log = sandbox(browser, tmp_path, hash_="gig", sel="#copyGig")
    n = len(log)
    fr.click("#copyGig")
    fr.wait_for_selector("#gigTxt", state="visible")
    pg.wait_for_timeout(300)
    assert log[n:] == [], f"Copy gig list left console messages: {log[n:]}"
    ctx.close()


def test_T5_rejected_and_missing_clipboard_stay_quiet(app):
    pg = app(state=RICH, hash_="record")
    log = []
    pg.on("console", lambda m: log.append(m.type + ": " + m.text) if m.type in ("error", "warning") else None)
    for js in (CLIP_BLOCKED_JS,
               "()=>{Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:()=>{throw new Error('sync')}}})}",
               "()=>{Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined})}"):
        pg.evaluate(js)
        pg.evaluate("()=>{document.getElementById('bkOut').classList.add('hide')}")
        pg.click("#bkCopy")
        pg.wait_for_selector("#bkOut", state="visible")
    pg.wait_for_timeout(200)
    assert log == [] and not pg.errors, log + pg.errors


def test_T5_clipboard_still_used_when_allowed(app):
    pg = app(state=RICH, hash_="record")
    pg.evaluate("()=>{window.__clip=[];Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:t=>{window.__clip.push(t);return Promise.resolve()}}})}")
    pg.click("#bkCopy")
    pg.wait_for_function("()=>window.__clip.length===1")
    assert json.loads(pg.evaluate("()=>window.__clip[0]"))["state"] == RICH
    pg.wait_for_function("()=>/Backup copied/.test(document.getElementById('bkMsg').textContent)")
    assert not pg.locator("#bkOut").is_visible()


# ===================================================================== 0.9 register (SPEC_09): U1, U3

# --------------------------------------------------------------------- U1 (wording where storage is blocked)

U1_BROWSER = re.compile(r"saved in this browser|lives in this browser", re.I)
U1_BACKUP = '{"app":"The Guitar Lab","format":1,"version":"0.8","state":' + json.dumps(RICH) + "}"
U1_INTRO_08 = ("Your progress lives in this browser only. A backup holds all of it: every instrument's levels, gates and marks, the journal, "
               "the gig plan (with any names typed there) and your settings. Keep one somewhere safe, and use it to move to another device.")
U1_FOOT_08 = "Progress is saved in this browser only: keep a backup from the Record tab."
U1_ASK_08 = re.compile(r"Everything saved in this browser now \(.+\) will be replaced, and that can't be undone\.")


def test_U1_sandbox_wording_does_not_promise_storage(browser, tmp_path):
    ctx, pg, fr, log = sandbox(browser, tmp_path)
    fr.evaluate(POPUPS_JS)
    intro = fr.inner_text("#backup > p.note")
    foot = fr.inner_text(".foot")
    fr.fill("#bkIn", U1_BACKUP)
    fr.click("#bkImport")
    ask = fr.inner_text("#bkAsk")
    for name, t in (("Backup intro", intro), ("footer", foot), ("import question", ask)):
        assert not U1_BROWSER.search(t), f"{name} still promises browser storage: {t!r}"
        assert re.search(r"\bbackup\b", t, re.I), f"{name} doesn't mention a backup: {t!r}"
    assert re.search(r"can't keep your progress here", intro) and "Download backup" in intro and "Copy backup" in intro, intro
    assert re.search(r"can't keep your progress here", foot) and re.search(r"backup \(Download or Copy\) is the only way to keep it", foot), foot
    assert fr.get_attribute(".foot a", "href") == "#record", "the footer still links to the Record tab"
    assert "A backup holds all of it" in intro and "move to another device" in intro, "the rest of the intro is unchanged"
    assert "Replace your progress with this backup?" in ask and re.search(r"The progress loaded on this page now \(.+\) will be replaced, and that can't be undone\.", ask), ask
    fr.click("#bkNo")
    assert fr.inner_text("#bkAsk").strip() == "" and not U1_BROWSER.search(fr.inner_text("#backup")), "the card keeps the honest wording after a re-render"
    fr.fill("#bkIn", U1_BACKUP)
    fr.click("#bkImport")
    fr.click("#bkYes")
    after = fr.inner_text("#backup") + fr.inner_text(".foot")
    assert "Backup imported" in after and "Your path: Keys" in fr.inner_text("#v-record"), "the import itself must still work"
    assert not U1_BROWSER.search(after), after
    assert fr.evaluate("()=>window.__pop") == []
    assert not [m for m in log if m.startswith("pageerror")], log
    ctx.close()


@pytest.mark.parametrize("seed", [None, {}, RICH], ids=["first-visit", "empty", "rich"])
def test_U1_normal_page_wording_unchanged_from_0_8(app, seed):
    pg = app(state=seed, hash_="record")
    if seed is None:
        assert raw(pg) is None, "checking for storage must not write anything on a first visit"
    else:
        assert json.loads(raw(pg)) == seed, "checking for storage must not change what is stored"
    assert text(pg, "#backup > p.note") == U1_INTRO_08
    assert U1_FOOT_08 in " ".join(text(pg, ".foot").split())
    assert pg.get_attribute(".foot a", "href") == "#record"
    offer(pg, U1_BACKUP)
    ask = text(pg, "#bkAsk")
    assert U1_ASK_08.search(ask) and "loaded on this page" not in ask, ask
    assert "can't keep your progress here" not in pg.evaluate("()=>document.body.innerText")
    assert pg.evaluate("()=>Object.keys(localStorage)") in ([], ["shredder"]), "only the app's own key may exist"
    pg.click("#bkYes")
    assert "saved in this browser" in text(pg, "#bkMsg") and state(pg) == RICH
    assert not pg.errors


def test_U1_sandbox_footer_is_honest_on_another_tab(browser, tmp_path):
    ctx, pg, fr, log = sandbox(browser, tmp_path, hash_="gig", sel="#present")
    foot = fr.inner_text(".foot")
    assert not U1_BROWSER.search(foot) and "can't keep your progress here" in foot, foot
    assert "Lyrics and scores are not reproduced".lower() in foot.lower() and "SIL Open Font License" in foot, "the rest of the footer is unchanged"
    ctx.close()


# --------------------------------------------------------------------- U3 (every drum grid fits its card on narrow phones)

U3_JS = r"""()=>{const w=[...document.querySelectorAll('.dgw')].filter(e=>e.getClientRects().length);if(w.length!==1)return {count:w.length};
 const t=w[0].querySelector('table'),td=t.querySelector('td'),cs=getComputedStyle(td),r=t.getBoundingClientRect();
 return {count:1,sw:w[0].scrollWidth,cw:w[0].clientWidth,tw:Math.round(r.width*10)/10,fs:parseFloat(cs.fontSize),minw:cs.minWidth,cell:td.getBoundingClientRect().width,n:t.rows[0].cells.length-1,
   heads:[...t.rows[0].cells].map(c=>c.textContent.trim()),rows:[...t.rows].slice(1).map(x=>x.cells[0].textContent.trim()),
   lines:[...t.rows].map(x=>{const c=x.cells[0],g=document.createRange();g.selectNodeContents(c);return g.getClientRects().length})}}"""
U3_FEELS = [None] + [f["k"] for f in D["FIN"]]          # the stage's or song's own pattern (straight, quaver, shuffle, 3/4, 6/8), then each Finish feel
U3_PATH_1280 = {3: 208.0, 4: 238.7, 6: 300.2, 8: 361.6}   # table widths by cells in the bar, measured on 0.8 (a51db99) at 1280 px, 15 px text
U3_GIG_1280 = {4: 238.7, 8: 361.6}
U3_PRESENT_1280 = {4: 432.1, 8: 624.4}                  # 34 px text


def u3_state(feel, **kw):
    return dict({"inst": "drums", "useFin": bool(feel), "finish": feel or "bossa"}, **kw)


def u3_grid(pg):
    pg.wait_for_function("()=>[...document.querySelectorAll('.dgw')].some(e=>e.getClientRects().length)")
    g = pg.evaluate(U3_JS)
    assert g["count"] == 1, f"expected one visible drum grid, found {g['count']}"
    return g


def u3_fits(g, where):
    assert g["sw"] <= g["cw"] + 1, f"{where}: drum grid scrolls inside its card ({g['sw']} > {g['cw']})"
    assert g["tw"] <= g["cw"] + 1, f"{where}: drum grid is wider than its card ({g['tw']} > {g['cw']})"
    assert g["fs"] >= 12 and g["cell"] >= 16, f"{where}: grid too small to read (text {g['fs']}px, cell {g['cell']}px)"
    assert max(g["lines"]) <= 1, f"{where}: a row label wraps"
    assert g["heads"][0] == "Count" and len(g["heads"]) == g["n"] + 1 and "Kick" in g["rows"] and g["rows"][0].startswith("Hi-hat"), f"{where}: grid lost a row or column"


@pytest.mark.parametrize("feel", U3_FEELS, ids=lambda f: f or "own")
@pytest.mark.parametrize("width", [320, 360])
def test_U3_path_drum_grids_fit_their_card(app, width, feel):
    pg = app(width=width, state=u3_state(feel))
    seen = set()
    for s in D["ST"]:
        go(pg, s["id"])
        g = u3_grid(pg)
        u3_fits(g, f"{width}px Path {s['id']} ({feel or 'own'} feel)")
        assert not pg.evaluate(OVERFLOW_JS), f"page overflows on {s['id']}"
        if feel is None:
            assert g["n"] == D["PAT"][s["pat"]]["b"] * D["PAT"][s["pat"]]["s"], f"{s['id']}: the grid shown is not this stage's bar"
        seen.add(g["n"])
    if feel is None:
        assert seen == {3, 4, 6, 8}, f"expected straight, quaver, 3/4 and 6/8 bars across the Path, got {sorted(seen)}"
    assert not pg.errors


@pytest.mark.parametrize("feel", U3_FEELS, ids=lambda f: f or "own")
@pytest.mark.parametrize("width", [320, 360])
def test_U3_gig_drum_grids_fit_their_card_present_off_and_on(app, width, feel):
    seen = set()
    for song in D["GIG"]:
        pg = app(width=width, state=u3_state(feel, gig={"songs": [song["id"]], "useFin": bool(feel)}), hash_="gig")
        off = u3_grid(pg)
        u3_fits(off, f"{width}px Gig {song['id']} ({feel or 'own'} feel)")
        assert not pg.evaluate(OVERFLOW_JS), f"page overflows on {song['id']}"
        pg.click("#present")
        on = u3_grid(pg)
        u3_fits(on, f"{width}px Gig {song['id']} ({feel or 'own'} feel), Present")
        assert not pg.evaluate(OVERFLOW_JS), f"page overflows on {song['id']} in Present"
        assert on["heads"] == off["heads"] and on["rows"] == off["rows"]
        seen.add(off["n"])
        assert not pg.errors
        pg.context.close()
    assert seen == ({4} if feel == "flam" else {8}), f"unexpected bar lengths on the Gig tab: {sorted(seen)}"


def test_U3_narrow_gig_grid_shrinks_only_as_far_as_it_must(app):
    """The 0.8 finding: a quaver groove at 320 px was ~269 px in a ~250 px card. It now fills the card exactly; a grid that already fits keeps its size."""
    pg = app(width=320, state=u3_state(None, gig={"songs": ["g-bamba"]}), hash_="gig")
    g = u3_grid(pg)
    assert g["n"] == 8 and abs(g["tw"] - g["cw"]) <= 1 and g["fs"] == 13, g
    pg = app(width=320, state=u3_state("flam", gig={"songs": ["g-bamba"], "useFin": True}), hash_="gig")
    g4 = u3_grid(pg)
    assert g4["n"] == 4 and abs(g4["tw"] - 180.8) <= 0.6, f"a four-cell grid has room, so it stays at its 0.8 width: {g4}"
    pg = app(width=320, state=u3_state(None, stage="am-e7"), hash_="am-e7")
    g8 = u3_grid(pg)
    assert g8["n"] == 8 and abs(g8["tw"] - 268.8) <= 0.6, f"the Path card is wide enough, so its grid stays at its 0.8 width: {g8}"


@pytest.mark.parametrize("width,minw", [(320, "0px"), (340, "0px"), (341, "22px"), (360, "22px"), (481, "30px"), (1280, "30px")])
def test_U3_rule_applies_only_below_about_340(app, width, minw):
    pg = app(width=width, state=u3_state(None, gig={"songs": ["g-bamba"]}), hash_="gig")
    g = u3_grid(pg)
    assert g["minw"] == minw, f"{width}px: cell min-width {g['minw']}, expected {minw}"
    u3_fits(g, f"{width}px Gig")
    if width > 340:
        assert abs(g["tw"] - (268.8 if width <= 480 else 361.6)) <= 0.6, f"{width}px: grid width changed from 0.8 ({g['tw']})"


def test_U3_sizes_at_1280_unchanged_from_0_8(app):
    for feel in U3_FEELS:
        pg = app(width=1280, state=u3_state(feel))
        for s in D["ST"]:
            go(pg, s["id"])
            g = u3_grid(pg)
            assert g["fs"] == 15 and g["minw"] == "30px" and abs(g["tw"] - U3_PATH_1280[g["n"]]) <= 0.6, (feel, s["id"], g)
        pg.context.close()
        for song in D["GIG"]:
            pg = app(width=1280, state=u3_state(feel, gig={"songs": [song["id"]], "useFin": bool(feel)}), hash_="gig")
            g = u3_grid(pg)
            assert g["fs"] == 15 and abs(g["tw"] - U3_GIG_1280[g["n"]]) <= 0.6, (feel, song["id"], g)
            pg.click("#present")
            p = u3_grid(pg)
            assert p["fs"] == 34 and abs(p["tw"] - U3_PRESENT_1280[p["n"]]) <= 0.6, (feel, song["id"], p)
            pg.context.close()


# --------------------------------------------------------------------- 0.9 version label and older backups

@pytest.mark.parametrize("wrap", ["0.7", "0.8", "0.9", None], ids=["0.7", "0.8", "0.9", "bare-state"])
def test_version_0_9_still_imports_older_backups_and_bare_state(app, wrap):
    pg = app(state={}, hash_="record")
    offer(pg, json.dumps(RICH if wrap is None else {"app": "The Guitar Lab", "format": 1, "version": wrap, "saved": "2026-11-20T03:00:00.000Z", "state": RICH}))
    pg.click("#bkYes")
    assert "Backup imported" in text(pg, "#bkMsg") and state(pg) == RICH
    assert json.loads(copy_backup(pg))["version"] == "0.9", "a new backup is stamped 0.9"
    assert not pg.errors


def test_version_0_9_newer_backup_message_names_this_version(app):
    pg = app(state=RICH, hash_="record")
    before = raw(pg)
    offer(pg, json.dumps({"app": "The Guitar Lab", "format": 2, "version": "1.0", "state": RICH}))
    msg = text(pg, "#bkMsg")
    assert "newer version of The Guitar Lab than this one (0.9)" in msg and "Nothing has been changed" in msg and "0.8" not in msg, msg
    assert raw(pg) == before and not pg.errors
