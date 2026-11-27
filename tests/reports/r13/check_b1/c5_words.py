"""Check 7 words: British terms, lyrics, method names, guitar wording in everything a bass player can read (whole Path side + stage for 8 stages, and 6 other tabs, all Finishes)."""
import re, json
from lib import *
html = (ROOT / "index.html").read_text(encoding="utf-8")
D = json.loads(re.search(r'id="instData">(.*?)</script>', html, re.S).group(1))
blob = json.dumps(D, ensure_ascii=False)
US = r"\b(eighth[- ]notes?|quarter[- ]notes?|half[- ]notes?|whole[- ]notes?|sixteenth|measures?|half[- ]steps?|whole[- ]steps?|whole tone|color|favorite|center|practice[sd]?\b(?= (it|the|your) )|practicing)\b"
METH = r"Hal Leonard|Essential Elements|Rockschool|Trinity|AMEB|Suzuki|Kod[aá]ly|Orff|Dalcroze|Simandl|Musical Futures|Music EDnet|Gig Based|Little Kids Rock|Fender Play|Yousician|Justin ?Guitar|Rocksmith|Scott'?s Bass|Rufus|Berklee"
print("instData size", len(blob), "| US terms:", re.findall(US, blob, re.I), "| method names:", re.findall(METH, blob, re.I))
print("quoted runs of 6+ words in instData:", [q for q in re.findall(r'[“"\']([^“”"\']{30,})[”"\']', " ".join(x["w"] for x in D["bass"]["rud"] + D["bass"]["tech"]) + " ".join(k["b"] for v in D["bass"]["know"].values() for k in v))][:5])
words = sum(len(x["w"].split()) for x in D["bass"]["rud"] + D["bass"]["tech"]); print("item text lengths (words):", {x["id"]: len(x["w"].split()) for x in D["bass"]["rud"] + D["bass"]["tech"]})
GW = r"\b(guitar\w*|strum\w*|chord box\w*|shapes?|barre|capo|pick\b|plectrum|voicing)"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = open_page(b, state=passed_state('bass', gates={s + '@bass': 1 for s in IDS}))
    seen = {}
    for sid in IDS:
        go(pg, sid); pg.evaluate("()=>document.querySelectorAll('#side details').forEach(d=>d.open=true)")
        t = pg.evaluate("()=>document.getElementById('side').innerText+'\\n'+document.getElementById('stage').innerText")
        for m in re.finditer(GW, t, re.I): seen.setdefault(re.sub(r'\s+', ' ', t[max(0, m.start()-70):m.end()+50]), []).append(sid)
        for m in re.finditer(US + "|" + METH, t, re.I): print("  US/method on path", sid, t[max(0, m.start()-40):m.end()+40])
        if sid in ('am-e7', 'four-chords', 'six-eight', 'hallelujah'):
            print("  shared theory cards on", sid, ":", pg.evaluate("()=>[...document.querySelectorAll('#side details')].map(d=>d.innerText.replace(/\\n+/g,' | '))")[-2:])
    print("guitar-ish wording a bass player reads on the Path (context -> stages):")
    for c, ss in seen.items(): print("   ", sorted(set(ss)), "|", c)
    for v in ('warm-up', 'rudiments', 'technique', 'invent', 'record'):
        go(pg, v); t = pg.inner_text('#v-' + v)
        for m in re.finditer(GW, t, re.I): print("  ", v, "|", re.sub(r'\s+', ' ', t[max(0, m.start()-70):m.end()+50]))
    b.close()
