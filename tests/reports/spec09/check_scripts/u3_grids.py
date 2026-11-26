"""U3: no drum grid scrolls inside its card at 320/340/360 (Present off and on), wider layouts unchanged from 0.8.
Path: 8 stages x (own feel + 4 Finish feels). Gig: 6 songs x the same 5 feels, Present off and on.
Every combination is measured on this branch and on 0.8 (main) so sizes can be compared like for like."""
import json, sys
from playwright.sync_api import sync_playwright
from common import *

STAGES = ["a-e", "twelve-bar", "am-e7", "c-g-f", "four-chords", "six-eight", "hallelujah", "beyond"]
SONGS = ["g-boogie", "g-clock", "g-johnny", "g-hound", "g-shoes", "g-bamba"]
FEELS = [(False, "bossa"), (True, "rock"), (True, "flam"), (True, "bossa"), (True, "metal")]
WIDTHS = [300, 320, 330, 340, 341, 350, 360, 480, 768, 1280]
JS = """(view)=>{const d=document.documentElement,r1=x=>Math.round(x*10)/10;const out={page:[d.scrollWidth,d.clientWidth,document.body.scrollWidth],grids:[]};
 document.querySelectorAll(view+' .dg').forEach(t=>{if(!t.getClientRects().length)return;const w=t.closest('.dgw'),r=t.getBoundingClientRect(),card=t.closest('.card')||(w||t).parentElement,kr=card.getBoundingClientRect(),cs=getComputedStyle(card);
  let clipped=0,minCell=1e9,minH=1e9;t.querySelectorAll('th,td').forEach(x=>{if(x.scrollWidth>x.clientWidth+1)clipped++});
  [...t.rows[1].cells].slice(1).forEach(x=>{const b=x.getBoundingClientRect();minCell=Math.min(minCell,b.width);minH=Math.min(minH,b.height)});
  out.grids.push({hasWrap:!!w,sw:w?w.scrollWidth:null,cw:w?w.clientWidth:null,tableW:r1(r.width),tableH:r1(r.height),over:r1(r.right-(kr.right-parseFloat(cs.paddingRight)-parseFloat(cs.borderRightWidth))),
   cardSW:card.scrollWidth,cardCW:card.clientWidth,font:parseFloat(getComputedStyle(t).fontSize),cellW:r1(minCell),cellH:r1(minH),headW:r1(t.rows[0].cells[0].getBoundingClientRect().width),cols:t.rows[0].cells.length,rows:t.rows.length,clipped})});return out}"""


def run(b, base):
    res = {}
    for w in WIDTHS:
        for useFin, fin in FEELS:
            feel = fin if useFin else "own"
            for sid in STAGES:
                pg = open_app(b, base, width=w, height=800, state={"inst": "drums", "stage": sid, "useFin": useFin, "finish": fin}, hash_="path")
                m = pg.evaluate(JS, "#v-path"); m["console"] = bad_msgs(pg); res["%d|path|%s|%s|off" % (w, sid, feel)] = m; pg.context.close()
            for song in SONGS:
                pg = open_app(b, base, width=w, height=800, state={"inst": "drums", "finish": fin, "gig": {"open": song, "songs": SONGS, "useFin": useFin}}, hash_="gig")
                m = pg.evaluate(JS, "#v-gig"); res["%d|gig|%s|%s|off" % (w, song, feel)] = m
                pg.click("#present"); pg.wait_for_function("document.body.classList.contains('present')")
                m2 = pg.evaluate(JS, "#v-gig"); m2["console"] = bad_msgs(pg); m["console"] = []; res["%d|gig|%s|%s|on" % (w, song, feel)] = m2; pg.context.close()
    return res


if "reuse" in sys.argv:  # re-run the analysis on the saved measurements
    d = json.load(open(RES / "u3_raw.json")); new, old = d["0.9"], d["0.8"]
else:
    with sync_playwright() as p:
        b = p.chromium.launch()
        _, base9 = serve(); _, base8 = serve(main08())
        new, old = run(b, base9), run(b, base8)
        b.close()
    json.dump({"0.9": new, "0.8": old}, open(RES / "u3_raw.json", "w"))
fails, outside = [], []  # 300 px is below the spec's widths: reported, not failed
print("combinations per version:", len(new), "| grids measured:", sum(len(v["grids"]) for v in new.values()))
empty = [k for k, v in new.items() if not v["grids"]]
print("combinations with no drum grid:", len(empty), empty[:5])
print("\nwidth | where/present | grids | cols | 0.9 worst sw-cw | 0.9 worst past card | 0.8 worst sw-cw | 0.9 font | 0.9 min cell w | clipped cells | page overflow")
for w in WIDTHS:
    for where, pres in (("path", "off"), ("gig", "off"), ("gig", "on")):
        ks = [k for k in new if k.startswith("%d|%s|" % (w, where)) and k.endswith("|" + pres)]
        g9 = [(k, g) for k in ks for g in new[k]["grids"]]; g8 = [(k, g) for k in ks for g in old[k]["grids"]]
        worst9 = max(g["sw"] - g["cw"] for _, g in g9); worst8 = max(g["sw"] - g["cw"] for _, g in g8); past = max(g["over"] for _, g in g9)
        pov = [k for k in ks if new[k]["page"][0] > new[k]["page"][1] + 1 or new[k]["page"][2] > new[k]["page"][1] + 1]
        clipped = sum(g["clipped"] for _, g in g9)
        print("%4d | %s/%s | %d | %s | %d | %.1f | %d | %s | %.1f | %d | %d" % (w, where, pres, len(g9), sorted(set(g["cols"] for _, g in g9)), worst9, past, worst8,
              sorted(set(g["font"] for _, g in g9)), min(g["cellW"] for _, g in g9), clipped, len(pov)))
        for k, g in g9:
            if g["sw"] > g["cw"] + 1 or g["over"] > 1: (fails if w >= 320 else outside).append(("grid scrolls / passes card", k, g))
        if pov: fails.append(("page overflow", pov))
        if clipped: fails.append(("clipped cell text", w, where, pres, clipped))
        if not all(g["hasWrap"] for _, g in g9): fails.append(("grid without .dgw wrapper", w, where))
    con = [(k, v["console"]) for k, v in new.items() if k.startswith("%d|" % w) and v.get("console")]
    if con: fails.append(("console", con[:3]))
# like-for-like with 0.8
print("\nwidth | combos whose grid measurements differ from 0.8 (any of sw, cw, table w/h, font, cell w/h, first column) | example")
for w in WIDTHS:
    ks = [k for k in new if k.startswith("%d|" % w)]
    diff = [k for k in ks if json.dumps(new[k]["grids"], sort_keys=True) != json.dumps(old[k]["grids"], sort_keys=True) or new[k]["page"] != old[k]["page"]]
    ex = ""
    if diff:
        k = max(diff, key=lambda k: max(abs(a["tableW"] - c["tableW"]) for a, c in zip(new[k]["grids"], old[k]["grids"])))
        a, c = new[k]["grids"][0], old[k]["grids"][0]
        ex = "%s: table %.1f -> %.1f, cell %.1f -> %.1f, font %s -> %s, sw/cw %s/%s -> %s/%s" % (k, c["tableW"], a["tableW"], c["cellW"], a["cellW"], c["font"], a["font"], c["sw"], c["cw"], a["sw"], a["cw"])
    print("%4d | %d of %d | %s" % (w, len(diff), len(ks), ex))
    if w > 340 and diff: fails.append(("differs from 0.8 above 340", w, diff[:3]))
print("\nwhat changed from 0.8 at 340 and below, by place (table width / narrowest cell / first column / table height, 0.8 -> 0.9, ranges over the combos that changed)")
for w in [x for x in WIDTHS if x <= 340]:
    for where, pres in (("path", "off"), ("gig", "off"), ("gig", "on")):
        ks = [k for k in new if k.startswith("%d|%s|" % (w, where)) and k.endswith("|" + pres)]
        ch = [(old[k]["grids"][0], new[k]["grids"][0]) for k in ks if json.dumps(new[k]["grids"], sort_keys=True) != json.dumps(old[k]["grids"], sort_keys=True)]
        rng = lambda f, i: "%s..%s" % (min(x[i][f] for x in ch), max(x[i][f] for x in ch))
        print("%4d | %s/%s | %d of %d changed%s" % (w, where, pres, len(ch), len(ks), "" if not ch else " | cols %s | table %s -> %s | cell %s -> %s | first col %s -> %s | height %s -> %s | sw-cw %s -> %s" % (
            sorted(set(x[1]["cols"] for x in ch)), rng("tableW", 0), rng("tableW", 1), rng("cellW", 0), rng("cellW", 1), rng("headW", 0), rng("headW", 1), rng("tableH", 0), rng("tableH", 1),
            max(x[0]["sw"] - x[0]["cw"] for x in ch), max(x[1]["sw"] - x[1]["cw"] for x in ch))))
# Present enlargement at 1280
big = [(k, g["font"], new[k.replace("|on", "|off")]["grids"][i]["font"]) for k in new if k.startswith("1280|gig") and k.endswith("|on") for i, g in enumerate(new[k]["grids"])]
print("\n1280 Present font vs not:", sorted(set((a, c) for _, a, c in big)))
if not all(a > c for _, a, c in big): fails.append(("Present not larger at 1280",))
print("\nbelow the spec widths (300 px): %d combos still scroll inside the card, e.g. %s" % (len(outside), json.dumps(outside[0])[:300] if outside else None))
print("\nFAILS:", len(fails))
for f in fails: print("FAIL", json.dumps(f)[:600])
