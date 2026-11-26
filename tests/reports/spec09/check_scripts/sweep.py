"""Regression sweep: 7 tabs x 5 instruments x 360/1280 x dark/light on 0.9, with the same views on 0.8 (main) alongside.
Console errors/warnings, page-level overflow, dialogs, off-host requests, version labels, American spellings,
and the visible text of every view compared with 0.8 character for character (only '0.9' for '0.8' may differ)."""
import json, re
from playwright.sync_api import sync_playwright
from common import *

TABS = ["path", "warm-up", "rudiments", "technique", "invent", "gig", "record"]
INST = ["guitar", "bass", "drums", "keys", "vocals"]
US = re.compile(r"\b(color|colors|colored|center|centered|favorite|behavior|organize[ds]?|recognize[ds]?|realize[ds]?|analyze[ds]?|gray|meter|meters|program|practicing|practiced|quarter[- ]notes?|eighth[- ]notes?|half[- ]notes?|whole[- ]notes?|sixteenth[- ]notes?|measures?|labeled|traveling|canceled|fulfill|skillful|jewelry|license[ds]?|defense|catalog)\b", re.I)
bad, us, n, labels, textdiff, sized = [], {}, 0, set(), [], []
GEO = "()=>[...document.querySelectorAll('.view:not(.hide) .card, .view:not(.hide) .dg, header, p.foot')].map(e=>{const r=e.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]})"
with sync_playwright() as p:
    b = p.chromium.launch(); _, base = serve(); _, base8 = serve(main08())
    for scheme in ("dark", "light"):
        for w in (360, 1280):
            for inst in INST:
                st = {"inst": inst, "capo": {"a-e": 2}}
                pg = open_app(b, base, width=w, height=800, scheme=scheme, state=st); pg8 = open_app(b, base8, width=w, height=800, scheme=scheme, state=st)
                for tab in TABS:
                    key = "%s %d %s %s" % (scheme, w, inst, tab); n += 1
                    for q in (pg, pg8):
                        q.click('#tabs a[href="#%s"]' % tab); q.wait_for_selector('#tabs a[href="#%s"][aria-current=page]' % tab); q.wait_for_timeout(60)
                    sw, cw, bw = pg.evaluate(OVERFLOW)
                    if sw > cw + 1 or bw > cw + 1: bad.append((key, "page overflow", sw, bw, cw))
                    if not pg.is_visible("#v-" + tab): bad.append((key, "view not visible"))
                    txt, txt8 = pg.inner_text("body"), pg8.inner_text("body"); labels.add(pg.title() + " | " + pg.inner_text("header .sub"))
                    if txt.replace("0.9", "0.8") != txt8: textdiff.append(key)
                    if pg.evaluate(GEO) != pg8.evaluate(GEO): sized.append(key)
                    for m in US.finditer(txt): us.setdefault(m.group(0).lower(), set()).add(txt[max(0, m.start() - 40):m.end() + 30].replace("\n", " "))
                    if re.search(r"\b0\.8\b", txt): bad.append((key, "0.8 shown"))
                    for g in pg.evaluate("()=>[...document.querySelectorAll('.dgw')].filter(e=>e.getClientRects().length).map(e=>[e.scrollWidth,e.clientWidth])"):
                        if g[0] > g[1] + 1: bad.append((key, "drum grid scrolls", g))
                if bad_msgs(pg): bad.append(("%s %d %s" % (scheme, w, inst), "console", bad_msgs(pg)))
                if pg.dialogs: bad.append(("dialog", pg.dialogs))
                if off_host(pg, base): bad.append(("off-host request", off_host(pg, base)))
                pg.context.close(); pg8.context.close()
    b.close()
src = (ROOT / "index.html").read_text(); old = (main08() / "index.html").read_text()
import difflib
added = [l[1:] for l in difflib.unified_diff(old.splitlines(), src.splitlines(), lineterm="", n=0) if l.startswith("+") and not l.startswith("+++")]
res = {"views checked": n, "problems": bad, "version labels": sorted(labels), "views whose visible text differs from 0.8 (beyond the version number)": textdiff,
       "views where a card, drum grid, header or footer has a different size from 0.8": sized,
       "US spellings in rendered text": {k: sorted(v)[:3] for k, v in us.items()}, "US spellings in the lines 0.9 added to the source": sorted(set(m.group(0) for l in added for m in US.finditer(l))), "lines added in 0.9": len(added)}
json.dump(res, open(RES / "sweep.json", "w"), indent=1, ensure_ascii=False, default=str); print(json.dumps(res, indent=1, ensure_ascii=False, default=str))
