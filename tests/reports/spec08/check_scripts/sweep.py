"""Regression sweep: 7 tabs x 5 instruments x 360/1280 x dark/light. Console errors/warnings, page-level horizontal overflow,
dialogs, off-host requests, version labels, American spellings in rendered text, inner scroll of drum grids. Also saves a few screenshots."""
import json, re, pathlib, sys
from playwright.sync_api import sync_playwright
from common import *

TABS = ["path", "warm-up", "rudiments", "technique", "invent", "gig", "record"]
INST = ["guitar", "bass", "drums", "keys", "vocals"]
US = re.compile(r"\b(color|colors|colored|center|centered|favorite|behavior|organi[zs]e[ds]?|recogni[z]e[ds]?|reali[z]e[ds]?|analy[z]e[ds]?|gray|meter|meters|program|practicing|practiced|quarter[- ]notes?|eighth[- ]notes?|half[- ]notes?|whole[- ]notes?|sixteenth[- ]notes?|measures?|labeled|traveling|canceled|fulfill|skillful|jewelry|license[ds]?|defense|catalog)\b", re.I)
shots = pathlib.Path(__file__).parent / "shots"; shots.mkdir(exist_ok=True)
bad, us, n, labels, inner = [], {}, 0, set(), []
with sync_playwright() as p:
    b = p.chromium.launch(); srv, base = serve()
    for scheme in ("dark", "light"):
        for w in (360, 1280):
            for inst in INST:
                pg = open_app(b, base, width=w, height=800, scheme=scheme, state={"inst": inst, "capo": {"a-e": 2}})
                for tab in TABS:
                    pg.click('#tabs a[href="#%s"]' % tab); pg.wait_for_selector('#tabs a[href="#%s"][aria-current=page]' % tab); pg.wait_for_timeout(60); n += 1
                    sw, cw, bw = pg.evaluate(OVERFLOW); key = "%s %d %s %s" % (scheme, w, inst, tab)
                    if sw > cw + 1 or bw > cw + 1: bad.append((key, "page overflow", sw, bw, cw))
                    if not pg.is_visible("#v-" + tab): bad.append((key, "view not visible"))
                    txt = pg.inner_text("body"); labels.add(pg.title() + " | " + pg.inner_text("header .sub"))
                    for m in US.finditer(txt): us.setdefault(m.group(0).lower(), set()).add(txt[max(0, m.start() - 40):m.end() + 30].replace("\n", " "))
                    if re.search(r"\b0\.7\b", txt): bad.append((key, "0.7 shown"))
                    for g in pg.evaluate("()=>[...document.querySelectorAll('.dgw')].filter(e=>e.getClientRects().length).map(e=>[e.scrollWidth,e.clientWidth])"):
                        if g[0] > g[1] + 1: inner.append((key, g))
                    if (inst, tab) in (("keys", "path"), ("drums", "gig"), ("guitar", "record"), ("bass", "path")) : pg.screenshot(path=str(shots / ("%s_%d_%s_%s.png" % (scheme, w, inst, tab))), full_page=(w == 1280 and tab == "path"))
                if bad_msgs(pg): bad.append(("%s %d %s" % (scheme, w, inst), "console", bad_msgs(pg)))
                if pg.dialogs: bad.append(("dialog", pg.dialogs))
                off = [u for u in pg.reqs if not u.startswith(base) and not u.startswith("blob:") and not u.startswith("data:")]
                if off: bad.append(("off-host request", off))
                pg.context.close()
    # drum grids on every Path stage at 360 (inner scroll), each feel
    for sid in ["a-e", "twelve-bar", "am-e7", "c-g-f", "four-chords", "six-eight", "hallelujah", "beyond"]:
        for useFin, fin in [(False, "bossa"), (True, "rock"), (True, "flam"), (True, "bossa"), (True, "metal")]:
            pg = open_app(b, base, width=360, height=800, state={"inst": "drums", "stage": sid, "useFin": useFin, "finish": fin})
            for g in pg.evaluate("()=>[...document.querySelectorAll('.dgw')].filter(e=>e.getClientRects().length).map(e=>[e.scrollWidth,e.clientWidth,e.querySelector('tr').cells.length])"):
                if g[0] > g[1] + 1: inner.append(("path 360 drums %s %s" % (sid, fin if useFin else "own"), g))
            sw, cw, bw = pg.evaluate(OVERFLOW)
            if sw > cw + 1: bad.append(("path 360 drums " + sid, "page overflow", sw, cw))
            pg.context.close()
    b.close()
print(json.dumps({"views checked": n, "problems": bad, "version labels": sorted(labels), "US spellings": {k: sorted(v)[:3] for k, v in us.items()}, "drum grid inner scroll": inner}, indent=1, ensure_ascii=False, default=str))
