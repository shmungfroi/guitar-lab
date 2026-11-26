"""T1: lit black keys vs white keys, both themes, measured from computed styles."""
import json, colorsys
from playwright.sync_api import sync_playwright
from common import *

JS = """()=>{const cs=(el,p)=>getComputedStyle(el)[p];const out={lb:new Set(),ub:new Set(),lw:new Set(),uw:new Set(),txt:new Set()};
 document.querySelectorAll('svg.kb rect').forEach(r=>{const blk=r.getAttribute('height')==='40',on=r.classList.contains('k-on');out[(on?'l':'u')+(blk?'b':'w')].add(cs(r,'fill'))});
 document.querySelectorAll('svg.kb').forEach(s=>{[...s.querySelectorAll('rect')].forEach(r=>{if(r.getAttribute('height')==='40'&&r.classList.contains('k-on')){const t=r.nextElementSibling;if(t&&t.tagName==='text')out.txt.add(cs(t,'fill'))}})});
 const root=getComputedStyle(document.documentElement);const probe=v=>{const d=document.createElement('i');d.style.color='var('+v+')';document.body.appendChild(d);const c=getComputedStyle(d).color;d.remove();return c};
 const o={};for(const k in out)o[k]=[...out[k]];o.dom=probe('--dom');o.sub=probe('--sub');o.hi=probe('--hi');o.n=document.querySelectorAll('svg.kb').length;return o}"""
res = {}
with sync_playwright() as p:
    b = p.chromium.launch(); srv, base = serve()
    for scheme in ("dark", "light"):
        for where, st, h in (("path a-e capo0", {"inst": "keys", "stage": "a-e"}, ""), ("path a-e capo2", {"inst": "keys", "stage": "a-e", "capo": {"a-e": 2}}, ""), ("gig", {"inst": "keys"}, "gig")):
            pg = open_app(b, base, scheme=scheme, state=st, hash_=h)
            r = pg.evaluate(JS)
            hx = {k: ([rgb2hex(x) for x in v] if isinstance(v, list) else rgb2hex(v)) for k, v in r.items() if k != "n"}
            hx["n_keyboards"] = r["n"]
            if hx["lb"]:
                lb = hx["lb"][0]
                hh, ll, ss = colorsys.rgb_to_hls(*[int(lb[i:i + 2], 16) / 255 for i in (1, 3, 5)])
                hx["m"] = {"lit_black_vs_white_key": round(contrast(lb, hx["uw"][0]), 2), "lit_black_vs_unlit_black": round(contrast(lb, hx["ub"][0]), 2),
                           "lit_black_vs_lit_white": round(contrast(lb, hx["lw"][0]), 2) if hx["lw"] else None,
                           "label_on_lit_black": round(contrast(lb, hx["txt"][0]), 2) if hx["txt"] else None,
                           "lit_black_vs_dom": round(contrast(lb, hx["dom"]), 2), "lit_black_vs_sub": round(contrast(lb, hx["sub"]), 2),
                           "hue_deg": round(hh * 360), "sat": round(ss, 2), "light": round(ll, 2)}
            hx["console"] = bad_msgs(pg)
            res[scheme + " | " + where] = hx
            pg.context.close()
    b.close()
print(json.dumps(res, indent=1))
