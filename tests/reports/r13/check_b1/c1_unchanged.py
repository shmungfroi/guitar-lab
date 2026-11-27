"""Checks 1+2: guitar, drums, keys, vocals rendered output vs 0.9 (innerHTML and innerText)."""
import json, sys
from lib import *
def snap(b, url, inst, st):
    out = {}
    base = dict(st); base["inst"] = inst
    pg = open_page(b, url, state=base)
    for sid in IDS:
        go(pg, sid)
        out["side:" + sid] = pg.evaluate("()=>[side.innerHTML,side.innerText]")
        out["stage:" + sid] = pg.evaluate("()=>[stage.innerHTML,stage.innerText]")
        out["tab:" + sid] = pg.evaluate("()=>[[...document.querySelectorAll('#stage .tab')].map(e=>e.textContent).join('\\n@@\\n'),'']")
    go(pg, "twelve-bar")
    for v in ['warm-up','rudiments','technique','invent','gig','record']:
        go(pg, v)
        out["view:" + v] = pg.evaluate("v=>{const e=document.getElementById('v-'+v);return [e.innerHTML,e.innerText]}", v)
    go(pg, "invent"); pg.click("#roll")
    out["invent-rolled"] = pg.evaluate("()=>[document.getElementById('v-invent').innerHTML,document.getElementById('v-invent').innerText]")
    out["header"] = pg.evaluate("()=>[document.querySelector('header')?document.querySelector('header').innerText:'',document.title]")
    out["_msgs"] = [pg.msgs, []]
    pg.context.close(); return out
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for inst in ['guitar','drums','keys','vocals']:
        for label, st in [("fresh", {}), ("allpassed", passed_state(inst))]:
            o = snap(b, OLD, inst, st); n = snap(b, NEW, inst, st)
            diffs = []
            for k in o:
                if k in ("header", "_msgs"): continue
                if o[k][0] != n[k][0]: diffs.append((k, "html" if o[k][1] == n[k][1] else "text+html"))
            res[inst + "/" + label] = {"keys": len(o) - 2, "diffs": diffs, "header_old": o["header"], "header_new": n["header"], "msgs": n["_msgs"][0]}
            # show first diff detail
            for k, kind in diffs[:3]:
                a, c = o[k][0], n[k][0]
                i = next((i for i in range(min(len(a), len(c))) if a[i] != c[i]), min(len(a), len(c)))
                print("DIFF", inst, label, k, kind, "\n old:", a[max(0,i-80):i+160], "\n new:", c[max(0,i-80):i+160])
    b.close()
for k, v in res.items(): print(k, v["keys"], "compared;", len(v["diffs"]), "differ", v["diffs"], v["msgs"])
print(res["guitar/fresh"]["header_old"], res["guitar/fresh"]["header_new"])
