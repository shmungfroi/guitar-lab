"""Checks 3-6: bass content, gates, old saves, Invent."""
import json, re, math
from lib import *
html = (ROOT / "index.html").read_text(encoding="utf-8")
D = json.loads(re.search(r'id="instData">(.*?)</script>', html, re.S).group(1))
B = D["bass"]
R = []
def rec(id_, ok, ev): R.append((id_, "PASS" if ok else "FAIL", ev)); print(id_, "PASS" if ok else "FAIL", ev)
names = lambda pg, v: pg.evaluate("v=>[...document.querySelectorAll('#v-'+v+' .card > h3')].map(h=>h.childNodes[0].textContent.trim())", v)
DENY = ['palm mut','rasgueado','golpe','chord box','pendulum','strum','six-line','six line','guitar book','written for guitar','guitar technique','plectrum','barre','p i m a','e|-','B|-','down-up','tremolo','power chord']
with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    # ---- 3 content
    g = open_page(b, state=passed_state('guitar'), hash_="rudiments"); gr = names(g, 'rudiments'); go(g, 'technique'); gt = names(g, 'technique'); g.context.close()
    pg = open_page(b, state=passed_state('bass', finish='flam'), hash_="rudiments")
    br = names(pg, 'rudiments'); ids = pg.evaluate("()=>[...document.querySelectorAll('#v-rudiments [data-lv][data-dir=\"1\"]')].map(b=>b.dataset.lv)")
    rec("3a rudiments = bass list", br == [x["n"] for x in B["rud"]] and ids == ['r:'+x["id"]+'@bass' for x in B["rud"]] and all(x["id"].startswith('bs-') for x in B["rud"]+B["tech"]), f"{len(br)} cards, all ids bs-; names shared with guitar's list: {sorted(set(br)&set(gr))} (same name, different id and text)")
    fins = pg.evaluate("()=>[...document.querySelectorAll('#finishes button')].map(b=>[b.dataset.finish||b.dataset.fin||'',b.textContent.trim()])")
    go(pg, 'technique')
    filt = {}
    for key, label in [('rock','Rock and roll'),('flam','Flamenco'),('bossa','Bossa'),('metal','Hair metal')]:
        pg.click(f"#finishes button:has-text('{label}')")
        heads = pg.evaluate("()=>[...document.querySelectorAll('#v-technique > h3')].map(h=>h.textContent.trim())")
        nm = names(pg, 'technique')
        exp = [x["n"] for x in B["tech"] if x["f"] in ('core','rock',key)]
        filt[label] = (heads, sorted(nm) == sorted(exp), len(nm))
        if key == 'flam':
            opt = pg.evaluate("()=>[...document.querySelectorAll('#v-technique .card h3')].filter(h=>/Optional/.test(h.textContent)).map(h=>h.textContent)")
            tg = pg.evaluate("()=>{const c=[...document.querySelectorAll('#v-technique .card')].find(c=>/Tangos/.test(c.textContent));return c?[c.innerText,[...c.querySelectorAll('.tab')].map(t=>t.textContent)]:null}")
    rec("3b Finish filter core+rock+current", all(v[1] for v in filt.values()) and all(len(v[0]) == (2 if k == 'Rock and roll' else 3) for k, v in filt.items()), json.dumps({k: v[0] for k, v in filt.items()}, ensure_ascii=False))
    rec("3c flamenco marked optional", len(opt) == 1 and 'Tangos' in opt[0], str(opt))
    tangos_ok = tg and '12' not in re.sub(r'1 2 3 4', '', tg[0]) and 'counted in four' in tg[0]
    rec("3d tangos binary", bool(tangos_ok), (tg[1][-1] if tg else 'missing').replace('\n', ' / '))
    gset = set(gt)
    rec("3e technique has no guitar names", not (set(sum([names(pg,'technique')],[])) & gset), "0 overlap with guitar's %d" % len(gt))
    # stage cards + TAB
    cards = {}; hits = []
    def scan(where):
        t = pg.evaluate("()=>[...document.querySelectorAll('section[id^=v-]:not(.hide), [id^=v-]:not(.hide)')].map(e=>e.innerText).join('\\n')")
        for d in DENY:
            for m in re.finditer((r'\b' if d[0].isalpha() else '') + re.escape(d), t, re.I if d not in ('e|-','B|-') else 0):
                hits.append((where, d, t[max(0, m.start()-60):m.end()+40].replace('\n', ' ')))
    GK = ['Six strings','Parts of the guitar','chord box','Reading TAB','One fret','Barre']
    for sid in IDS:
        go(pg, sid)
        cards[sid] = pg.evaluate("()=>[...document.querySelectorAll('#side details summary, #side .card h3')].map(e=>e.textContent.trim())")
        scan("path:" + sid)
    tabs2 = (go(pg, 'twelve-bar'), pg.evaluate("()=>[...document.querySelectorAll('#stage .tab')].map(e=>e.textContent)"))[1]
    for v in VIEWS[1:]:
        go(pg, v); scan(v)
    go(pg, 'invent'); pg.click('#roll'); scan('invent-rolled')
    side_know = {}
    for sid in IDS:
        go(pg, sid)
        side_know[sid] = pg.evaluate("()=>[...document.querySelectorAll('#side details')].map(d=>d.querySelector('summary').textContent.trim())")
    exp_ok = all(all(k["t"] in side_know[sid] for k in B["know"][sid]) and len(B["know"][sid]) >= 1 for sid in IDS)
    rec("3f bass cards on all 8 stages", exp_ok, json.dumps({s: len(B["know"][s]) for s in IDS}) + " bass cards; rendered details per stage " + json.dumps({s: len(v) for s, v in side_know.items()}))
    print("   side cards:", json.dumps(side_know, ensure_ascii=False))
    lines = tabs2[0].split('\n') if tabs2 else []
    rec("3g stage-2 four-line TAB", len(tabs2) == 1 and len(lines) == 4 and [l[0] for l in lines] == ['G','D','A','E'], repr(tabs2))
    by = {}
    for w, d, ctx in hits: by.setdefault(d, []).append((w, ctx))
    print("   DENY hits:")
    for d, v in by.items():
        seen = {}
        for w, c in v: seen.setdefault(c, []).append(w)
        for c, ws in seen.items(): print("    ", repr(d), "|", c, "|", sorted(set(ws)))
    R.append(("3h denylist", "INFO", {d: len(v) for d, v in by.items()}))
    pg.context.close()

    # ---- 4 gates
    pg = open_page(b, state={"inst": "bass"}, hash_="technique")
    locked = lambda: pg.evaluate("()=>[...document.querySelectorAll('.card h3')].filter(h=>/Opens with stage/.test(h.textContent)).length")
    go(pg, 'rudiments'); r0 = locked(); go(pg, 'technique'); t0 = locked()
    go(pg, 'a-e')
    for i in range(5):
        for _ in range(2): pg.click(f'[data-lv="a-e@bass:{i}"][data-dir="1"]')
    toast = pg.inner_text('#toast')
    go(pg, 'rudiments'); r1 = locked(); go(pg, 'technique'); t1 = locked()
    st = store(pg)
    go(pg, 'a-e'); pg.click('[data-inst="guitar"]'); go(pg, 'rudiments'); gl = locked(); gdone = pg.evaluate("()=>document.querySelectorAll('.tag.ok').length")
    go(pg, 'a-e'); gsteps = pg.evaluate("()=>document.querySelector('#stage .title .note').textContent")
    pg.click('[data-inst="drums"]'); go(pg, 'rudiments'); dl = locked()
    gfresh = open_page(b, state={}, hash_="rudiments"); gl0 = gfresh.evaluate("()=>[...document.querySelectorAll('.card h3')].filter(h=>/Opens with stage/.test(h.textContent)).length"); gfresh.context.close()
    exp_r = sum(1 for x in B["rud"] if x["st"] > 1); exp_t = None
    rec("4 gates per instrument", r0 > r1 == exp_r and gl == gl0 and dl == gl0 and 'guitar' not in json.dumps(list(st["gates"].keys())) and list(st["gates"].keys()) == ['a-e@bass'],
        f"bass locked rudiments {r0}->{r1} (expected {exp_r}), technique {t0}->{t1}; guitar locked {gl} (fresh guitar {gl0}), drums locked {dl}; gates={list(st['gates'].keys())}; guitar header '{gsteps}'; toast '{toast}'")
    pg.context.close()

    # ---- 5 old saves
    old = {"finish":"rock","stage":"a-e","nsw":False,"teacher":False,"lv":{"r:pulse@bass":3,"t:power@bass":2,"r:cross@drums":2,"r:spider@bass":3,"r:pulse":2,"a-e:0":2,"t:boogie@bass":3},
           "sign":{},"marks":{},"changes":[],"journal":[],"bpm":70,"useFin":False,"gates":{},"warm":{},"best":{"r:pulse@bass":96,"r:pulse":88},"capo":{},"mute":{},"inst":"bass","gig":{}}
    pg = open_page(b, state=old, hash_="rudiments")
    d_r = pg.evaluate("()=>document.querySelectorAll('#v-rudiments .tag.ok').length"); lv_r = pg.evaluate("()=>[...document.querySelectorAll('#v-rudiments .lvname')].map(e=>e.textContent)")
    bests = pg.evaluate("()=>[...document.querySelectorAll('[data-best]')].map(e=>e.value).filter(Boolean)")
    go(pg, 'technique'); d_t = pg.evaluate("()=>document.querySelectorAll('#v-technique .tag.ok').length")
    go(pg, 'record'); recs = pg.evaluate("()=>[...document.querySelectorAll('#v-record .card')].slice(1,3).map(c=>c.innerText)")
    go(pg, 'rudiments'); pg.click('[data-lv="r:bs-pulse@bass"][data-dir="1"]')
    s2 = store(pg); kept = all(s2["lv"].get(k) == v for k, v in old["lv"].items()) and s2["best"] == old["best"]
    keys = pg.evaluate("()=>Object.keys(localStorage)")
    go(pg, 'a-e'); pg.click('[data-inst="guitar"]'); go(pg, 'rudiments'); gd = pg.evaluate("()=>[...document.querySelectorAll('#v-rudiments .card')].filter(c=>c.querySelector('.tag.ok')).map(c=>c.querySelector('h3').childNodes[0].textContent)")
    rec("5a stray keys hidden, not deleted", d_r == 0 and d_t == 0 and not bests and set(lv_r) == {'Not started'} and 'None yet' in recs[0] and 'None logged' in recs[1] and kept and s2["lv"].get("r:bs-pulse@bass") == 1,
        f"bass Done tags r={d_r} t={d_t}, best inputs filled={len(bests)}, Record: {recs[0]!r} / {recs[1][:60]!r}; after a level change all {len(old['lv'])} old lv keys + best kept={kept}; guitar Done={gd}")
    rec("5b storage key only 'shredder'", keys == ['shredder'], str(keys))
    msgs5 = list(pg.msgs); pg.context.close()
    # backups
    imp = {}
    rich = dict(old); rich["journal"] = [{"d": 1730000000000, "st": "a-e", "h": "x", "o": "y", "w": "z"}]; rich["inst"] = "guitar"
    for label, txt in [("0.7", json.dumps({"app":"The Guitar Lab","format":1,"version":"0.7","saved":"2026-11-20T01:00:00.000Z","state":rich})),
                       ("0.8", json.dumps({"app":"The Guitar Lab","format":1,"version":"0.8","saved":"2026-11-22T01:00:00.000Z","state":rich})),
                       ("0.9", json.dumps({"app":"The Guitar Lab","format":1,"version":"0.9","saved":"2026-11-25T01:00:00.000Z","state":rich})),
                       ("bare", json.dumps(rich)), ("format2", json.dumps({"app":"The Guitar Lab","format":2,"version":"0.11","state":rich}))]:
        pg = open_page(b, state={}, hash_="record")
        pg.fill('#bkIn', txt); pg.click('#bkImport')
        if pg.locator('#bkYes').count():
            pg.click('#bkYes'); s = store(pg); imp[label] = (s["lv"] == rich["lv"] and len(s["journal"]) == 1 and s["best"] == rich["best"], pg.inner_text('#bkMsg')[:70])
        else: imp[label] = (False, pg.inner_text('#bkMsg')[:120])
        out = None
        if label == "0.9":
            pg.evaluate("()=>{window.__clip='';Object.defineProperty(navigator,'clipboard',{value:{writeText:t=>{window.__clip=t;return Promise.resolve()}},configurable:true})}")
            pg.click('#bkCopy'); pg.wait_for_timeout(200)
            out = pg.evaluate("()=>{try{return JSON.parse(window.__clip).version}catch(e){return String(e)}}")
            ver = out
        pg.context.close()
    rec("5c 0.7/0.8/0.9 + bare import", all(imp[k][0] for k in ("0.7","0.8","0.9","bare")) and not imp["format2"][0] and '0.10' in imp["format2"][1], json.dumps(imp, ensure_ascii=False))
    vers = re.findall(r"0\.10", html); stale = [m for m in re.findall(r"version[^<\n]{0,12}0\.9|\(0\.9\)|Lab 0\.9", html)]
    rec("5d version 0.10 everywhere", ver == '0.10' and '<title>The Guitar Lab 0.10</title>' in html and 'version 0.10 ·' in html and "than this one (0.10)" in html and not re.search(r'version 0\.9|Lab 0\.9|version:.0\.9', html),
        f"backup version {ver}; title/header/newer-version message all 0.10; '(0.9)' appears only in {len(stale)} code comments")

    # ---- 6 Invent (the app's script is block-scoped, so only real oscillator starts are read: the bass voice is the only triangle wave during playback)
    PC = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
    def midi(name):
        pc = PC[name[0]] + name.count('♯') - name.count('♭'); return 28 + ((pc - 4) % 12)
    for sid, capo in [('a-e', 0), ('twelve-bar', 0), ('c-g-f', 0), ('six-eight', 0), ('beyond', 0), ('a-e', 2)]:
        st = passed_state('bass'); st["stage"] = sid; st["bpm"] = 200
        if capo: st["capo"] = {sid: capo}
        pg = open_page(b, state=st, hash_="invent", audio=True)
        pre = pg.inner_text('#v-invent')
        pg.click('#roll')
        n = pg.locator('[data-bcell]').count()
        loopn = pg.evaluate("()=>[...document.querySelectorAll('#v-invent .bcard .bname')].map(e=>e.textContent)")
        cardtxt = pg.evaluate("()=>[...document.querySelectorAll('#v-invent .bcard')].map(e=>e.innerText.replace(/\\n/g,' | '))")
        cyc = []
        for _ in range(5):
            pg.click(f'[data-bcell="{n-1}"]'); cyc.append(pg.inner_text(f'[data-bcell="{n-1}"] b'))
        for _ in range(4): pg.click(f'[data-bcell="{n-1}"]')  # round again to the approach note
        mid = []
        for _ in range(4): pg.click('[data-bcell="1"]'); mid.append(pg.inner_text('[data-bcell="1"] b'))
        cellsnow = pg.evaluate("()=>[...document.querySelectorAll('[data-bcell] b')].map(e=>e.textContent)")
        aria = pg.get_attribute('.bbar', 'aria-label')
        pg.click('#playLoop'); pg.wait_for_timeout(9500)
        starts = pg.evaluate("()=>window.__aud.starts"); acst = pg.evaluate("()=>window.__aud.starts.length")
        btn = pg.inner_text('#playLoop'); pg.click('#playLoop')
        tri = sorted([s for s in starts if s["osc"] and s["type"] == 'triangle'], key=lambda s: s["when"])
        notes = [round(69 + 12 * math.log2(s["freq"] / 440)) for s in tri]
        hitsper = sum(1 for v in cellsnow if v != '·')
        bars = [notes[i:i+hitsper] for i in range(0, len(notes), hitsper)]; bars = [x for x in bars if len(x) == hitsper]
        roots = [midi(x.rstrip('m7').replace('maj','')) if False else midi(re.match(r'[A-G][♯♭]?', x).group(0)) for x in loopn]
        roots = [28 + ((r - 28 - capo) % 12) for r in roots] if capo else roots   # what the band actually plays in Invent (see finding on capo)
        bad = []; pairs = []
        for i, bar in enumerate(bars):
            cur = roots[i % 4]; nxt = roots[(i + 1) % 4]; ap = bar[-1]; pairs.append((cur, ap, nxt))
            if bar[0] != cur: bad.append(("root", i, bar[0], cur))
            if abs(ap - nxt) != 1: bad.append(("approach not a semitone", i, ap, nxt))
            if nxt == 28 and ap != 29: bad.append(("into E not F", i, ap))
            if nxt != 28 and ap != nxt - 1: bad.append(("not from below", i, ap, nxt))
            if min(bar) < 28: bad.append(("below low E", i, bar))
        intoE = [q for q in pairs if q[2] == 28]
        rec(f"6a Invent play {sid} capo {capo}", len(bars) >= 5 and not bad and btn == 'Stop',
            f"loop shown {loopn}; cells={n}, last-cell cycle {cyc}, 2nd-cell cycle {mid}; bar now {cellsnow}; {len(tri)} bass (triangle) oscillator starts of {len(starts)} sources, {len(bars)} whole bars read; (root,approach,next) midi first 4 bars {pairs[:4]}; bars into open E: {len(intoE)} {intoE[:1]}; bad={bad[:3]}")
        print("   cards:", cardtxt, "\n   aria:", aria)
        if sid == 'a-e' and not capo:
            pg.click('#keepLoop'); j = store(pg)["journal"][-1]; go(pg, 'record'); li = pg.inner_text('#v-record .log li')
            jt = json.dumps(j, ensure_ascii=False)
            rec("6b Invent save", j["inst"] == 'bass' and j["tag"] == 'Invent' and not re.search(r'strum|voicing|chord box|guitar', jt, re.I), jt + " || Record shows: " + li.replace('\n', ' '))
            badp = [q for q in B["invent"]["prompts"] if re.search(r'strum|voicing|chord box|guitar|Fmaj7', q, re.I)]
            rec("6c prompts have no guitar wording", not badp, f"{len(B['invent']['prompts'])} prompts, {len(badp)} flagged")
        dl = pg.evaluate("()=>window.__dlg"); print("   msgs", pg.msgs, "dialogs", dl, "| pre-roll:", pre.replace('\n', ' | ')[:200])
        pg.context.close()
    b.close()
json.dump(R, open("c2_results.json", "w"), ensure_ascii=False, indent=1)
