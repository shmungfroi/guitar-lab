"""T2: Present mode, drums: drum grid must not scroll sideways; still larger at 1280 Present than non-Present.
All 6 gig songs x (song feel + 4 finish feels) x widths 320/360/768/1280."""
import json
from playwright.sync_api import sync_playwright
from common import *

SONGS = ["g-boogie", "g-clock", "g-johnny", "g-hound", "g-shoes", "g-bamba"]
FEELS = [(False, "bossa"), (True, "rock"), (True, "flam"), (True, "bossa"), (True, "metal")]
JS = """()=>{const d=document.documentElement;const out={page:[d.scrollWidth,d.clientWidth],present:document.body.classList.contains('present'),grids:[]};
 document.querySelectorAll('#v-gig .dg').forEach(t=>{const w=t.closest('.dgw')||t.parentElement,r=t.getBoundingClientRect(),c=t.querySelector('td'),cr=c.getBoundingClientRect();
  let clipped=0;t.querySelectorAll('th,td').forEach(x=>{if(x.scrollWidth>x.clientWidth+1)clipped++});
  const card=t.closest('.card'),kr=card.getBoundingClientRect();
  out.grids.push({wrapSW:w.scrollWidth,wrapCW:w.clientWidth,tableW:Math.round(r.width*10)/10,right:Math.round(r.right),cardRight:Math.round(kr.right),cardSW:card.scrollWidth,cardCW:card.clientWidth,font:parseFloat(getComputedStyle(t).fontSize),cellW:Math.round(cr.width*10)/10,cellH:Math.round(cr.height*10)/10,cols:t.rows[0].cells.length,clipped})});return out}"""
rows, fails, small = [], [], []
with sync_playwright() as p:
    b = p.chromium.launch(); srv, base = serve()
    for w in (320, 360, 768, 1280):
        for song in SONGS:
            for useFin, fin in FEELS:
                st = {"inst": "drums", "finish": fin, "gig": {"open": song, "songs": SONGS[:4], "useFin": useFin}}
                pg = open_app(b, base, width=w, height=800, state=st, hash_="gig")
                non = pg.evaluate(JS)
                pg.click("#present"); pg.wait_for_function("document.body.classList.contains('present')")
                pre = pg.evaluate(JS)
                assert pre["grids"], "no drum grid"
                for i, g in enumerate(pre["grids"]):
                    n = non["grids"][i]
                    row = dict(w=w, song=song, feel=(fin if useFin else "own"), cols=g["cols"], wrapSW=g["wrapSW"], wrapCW=g["wrapCW"], font=g["font"], cellW=g["cellW"], nonFont=n["font"], nonCellW=n["cellW"], nonSW=n["wrapSW"], nonCW=n["wrapCW"], page=pre["page"], clipped=g["clipped"])
                    rows.append(row)
                    if g["wrapSW"] > g["wrapCW"] + 1: fails.append(("grid scrolls (present)", row))
                    if n["wrapSW"] > n["wrapCW"] + 1: (fails if w >= 360 else small).append(("grid scrolls (non-present)", row))
                    if pre["page"][0] > pre["page"][1] + 1: fails.append(("page overflow", row))
                    if g["right"] > g["cardRight"] + 1: fails.append(("grid past card", row))
                    if g["clipped"]: fails.append(("cell text clipped", row))
                    if w == 1280 and not (g["font"] > n["font"] and g["cellW"] > n["cellW"]): fails.append(("not larger at 1280", row))
                if bad_msgs(pg): fails.append(("console", bad_msgs(pg)))
                pg.context.close()
    b.close()
print("combos", len(rows), "fails", len(fails))
for f in fails: print("FAIL", f)
print("outside the spec widths (320, not Present): %d combos scroll inside the card, e.g. %s" % (len(small), small[0] if small else None))
for w in (320, 360, 768, 1280):
    rs = [r for r in rows if r["w"] == w]
    print(w, "cols", sorted(set(r["cols"] for r in rs)), "maxSW-CW", max(r["wrapSW"] - r["wrapCW"] for r in rs), "present font", min(r["font"] for r in rs), "-", max(r["font"] for r in rs),
          "non-present font", sorted(set(r["nonFont"] for r in rs)), "present cellW", min(r["cellW"] for r in rs), "-", max(r["cellW"] for r in rs), "non cellW", min(r["nonCellW"] for r in rs), "-", max(r["nonCellW"] for r in rs))
    worst = max(rs, key=lambda r: r["cols"]); print("   widest:", worst)
