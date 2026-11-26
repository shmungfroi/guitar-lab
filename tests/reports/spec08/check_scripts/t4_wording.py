"""T4: drums never see strum names in the metronome bar / metronome card / stage card; bass+keys at capo 2 show sounding names."""
import json, re
from playwright.sync_api import sync_playwright
from common import *

STRUM = re.compile(r"downs?\b|down-up|\bstrum|\bD down\b|thumb bass|palm-muted|\bthumb\b", re.I)
JS = """()=>{const t=s=>{const e=document.querySelector(s);return e?e.innerText.replace(/\\s+/g,' ').trim():null};
 const cards=[...document.querySelectorAll('#side .card')].map(c=>({h:(c.querySelector('h3')||{innerText:''}).innerText,t:c.innerText.replace(/\\s+/g,' ').trim()}));
 return {mbar:t('.mbar'),mname:t('.mbar .m-name'),metro:(cards.find(c=>/^Metronome/.test(c.h))||{}).t||null,fn:(cards.find(c=>/^Function/.test(c.h))||{}).t||null,stage:t('#stage'),gig:t('#v-gig'),
  cells:[...document.querySelectorAll('#side .grid .cell')].map(c=>c.innerText).join(' ')}}"""
out = {"drums_hits": {}, "stage_panel_mentions": {}, "samples": {}}
with sync_playwright() as p:
    b = p.chromium.launch(); srv, base = serve()
    pg = open_app(b, base, state={"inst": "drums"})
    pg.context.close()
    # the app's script is block-scoped, so the strum names and stage ids are copied from index.html (PAT, FIN, ST)
    pats = ["Four downs", "Boogie shuffle, swung", "Straight quavers", "Bass, strum, strum", "D · DU · UDU", "Six-eight sway", "Backbeat quavers", "Rock waltz quavers", "Rock and roll ballad triplets",
            "Tangos: four", "12-beat compás", "Simplified bossa", "Bossa waltz", "Thumb on 1", "Palm-muted quavers"]
    stages = ["a-e", "twelve-bar", "am-e7", "c-g-f", "four-chords", "six-eight", "hallelujah", "beyond"]
    out["stages"] = stages; n = 0
    for sid in stages:
        for useFin, fin in [(False, "bossa"), (True, "rock"), (True, "flam"), (True, "bossa"), (True, "metal")]:
            for h in ("", "gig", "rudiments", "warm-up"):
                if h and sid != stages[0]: continue
                pg = open_app(b, base, state={"inst": "drums", "stage": sid, "useFin": useFin, "finish": fin, "gig": {"useFin": useFin}}, hash_=h)
                r = pg.evaluate(JS); n += 1
                for part in ("mbar", "metro", "cells") + (("stage",) if not h else ()) :
                    txt = r[part] or ""
                    hits = STRUM.findall(txt) + [q for q in pats if q in txt]
                    if part == "cells" and re.search(r"\b[DUBC]\b", txt): hits.append("letters:" + txt)
                    if hits:
                        ctx = sorted(set(txt[max(0, m.start() - 70):m.end() + 50] for m in STRUM.finditer(txt)))
                        (out["stage_panel_mentions"] if part == "stage" else out["drums_hits"]).setdefault(part + " | " + " || ".join(ctx), []).append("%s/%s/%s" % (sid, fin if useFin else "own", h or "path"))
                if sid in (stages[0], "a-e") and not h: out["samples"]["drums %s %s" % (sid, fin if useFin else "own")] = {"mbar": r["mbar"], "metro": r["metro"][:230], "cells": r["cells"]}
                if h == "gig" and not useFin: out["samples"]["drums gig"] = {"mbar": r["mbar"]}
                if bad_msgs(pg): out["drums_hits"]["console"] = bad_msgs(pg)
                pg.context.close()
    out["drum_pages_checked"] = n
    # capo
    for inst in ("guitar", "bass", "keys", "vocals", "drums"):
        for cap in (0, 2):
            for scheme in ("dark",):
                pg = open_app(b, base, state={"inst": inst, "stage": "a-e", "capo": ({"a-e": cap} if cap else {})})
                r = pg.evaluate(JS); out["samples"]["%s capo %d Function card" % (inst, cap)] = r["fn"]
                pg.context.close()
    # 360 px check of the Function card with the chart note
    pg = open_app(b, base, width=360, state={"inst": "keys", "stage": "a-e", "capo": {"a-e": 2}})
    out["fn_360_overflow"] = pg.evaluate(OVERFLOW); pg.context.close()
    # via the UI: press capo + twice as bass
    pg = open_app(b, base, state={"inst": "bass", "stage": "a-e"})
    pg.click('[data-capo="1"]'); pg.click('[data-capo="1"]')
    out["samples"]["bass after two clicks of Capo up"] = pg.evaluate(JS)["fn"]; out["dialogs"] = pg.dialogs; pg.context.close()
    b.close()
out["stage_panel_mentions"] = {k: "%d pages, e.g. %s" % (len(v), v[0]) for k, v in out["stage_panel_mentions"].items()}
print(json.dumps(out, indent=1, ensure_ascii=False))
