"""Small follow-ups: which tab makes the first save on a first visit (0.9 against 0.8), and any other wording that promises saving where storage is blocked."""
import re, json
from playwright.sync_api import sync_playwright
from common import *
TABS = ["path", "warm-up", "rudiments", "technique", "invent", "gig", "record"]
src = (ROOT / "index.html").read_text()
print("'import (' in source:", [src[max(0, m.start() - 70):m.end() + 40] for m in re.finditer(r"\bimport\s*\(", src)])
with sync_playwright() as p:
    b = p.chromium.launch(); _, base = serve(); _, base8 = serve(main08())
    for nm, bs in (("0.9", base), ("0.8", base8)):
        ctx = b.new_context(); pg = ctx.new_page(); pg.goto(bs + "/index.html"); pg.wait_for_selector("#tabs a[aria-current=page]", state="attached"); seq = [("load", pg.evaluate("()=>localStorage.getItem('shredder')"))]
        for t in TABS:
            pg.click('#tabs a[href="#%s"]' % t); pg.wait_for_selector('#tabs a[href="#%s"][aria-current=page]' % t); seq.append((t, pg.evaluate("()=>localStorage.getItem('shredder')")))
        print(nm, "first visit, stored after each step:", [(t, None if v is None else len(v)) for t, v in seq]); 
        if nm == "0.9": s9 = seq
        else: print("same stored text as 0.8 at every step:", [a[1] for a in s9] == [a[1] for a in seq])
        ctx.close()
    ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = watch(ctx.new_page()); pg.goto(base + "/__wrap?sb=allow-scripts&h=path"); fr = pg.wait_for_selector("#f").content_frame(); fr.wait_for_selector("#tabs a[aria-current=page]", state="attached")
    hits = set()
    for inst in ("guitar", "drums"):
        fr.click('#tabs a[href="#path"]'); fr.click('[data-inst="%s"]' % inst)
        for t in TABS:
            fr.click('#tabs a[href="#%s"]' % t); fr.wait_for_selector('#tabs a[href="#%s"][aria-current=page]' % t)
            for m in re.finditer(r"[^.\n]{0,70}\b(saved?|saves|kept|keeps|remember\w*|stored?)\b[^.\n]{0,60}", fr.inner_text("body"), re.I): hits.add(t + ": " + m.group(0).strip())
    print("storage blocked, wording about saving/keeping on any tab:"); [print("  ", h) for h in sorted(hits)]
    # journal entry and sign-off in the blocked frame: what does the page say?
    fr.click('#tabs a[href="#record"]'); print("record tab controls:", fr.evaluate("()=>[...document.querySelectorAll('#v-record button,#v-record textarea,#v-record input')].map(e=>e.id||e.getAttribute('aria-label')||e.textContent.trim()).slice(0,20)"))
    print("console:", bad_msgs(pg)); b.close()
