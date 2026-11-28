"""Independent check, items 5, 6, 9: returning students, backups, other instruments, and Path/Gig/Record against 0.9 (git 90719f9)."""
import sys, json, re, os, hashlib
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import common
from common import *
from playwright.sync_api import sync_playwright
R = []
def rec(k, ok, ev): R.append((k, bool(ok), ev)); print(('PASS ' if ok else 'FAIL ') + k + ' :: ' + str(ev)[:330], flush=True)
ALL7 = ['Path', 'Warm-up', 'Rudiments', 'Technique', 'Invent', 'Gig', 'Record']
OLD = {'0.9': '/tmp/v09/index.html', '0.8': '/tmp/v08/index.html', '0.7': '/tmp/v07/index.html'}
STAGES = ['a-e', 'twelve-bar', 'am-e7', 'c-g-f', 'four-chords', 'six-eight', 'hallelujah', 'beyond']

def old_page(b, ver, **kw):
    u = common.URL; common.URL = 'file://' + OLD[ver]
    try: return open_page(b, **kw)
    finally: common.URL = u
def backup(pg):
    with pg.expect_download() as d: pg.click('#bkDown')
    return open(d.value.path(), encoding='utf-8').read()
def view(pg): return pg.evaluate("()=>[...document.querySelectorAll('[id^=\"v-\"]')].filter(e=>!e.classList.contains('hide')).map(e=>e.id).join()")
def raw(pg): return pg.evaluate("()=>localStorage.getItem('shredder')")

NORM = r"""()=>{const d=document.body.cloneNode(true);for(const s of ['script','#v-first-steps','#tabs a[href="#first-steps"]','#tabMsg','#fsLink','#fsSoon','style'])d.querySelectorAll(s).forEach(e=>e.remove());
 return d.innerHTML.replace(/0\.11/g,'0.9').replace(/ class=""/g,'').replace(/\n\s*\n+/g,'\n')}"""

with sync_playwright() as p:
    b = p.chromium.launch(args=ARGS)
    # --- make genuine 0.9 saves with 0.9 itself
    pg = old_page(b, '0.9', state={'journal': [{'d': 1795000000000, 't': 'A and E felt steadier today', 'inst': 'guitar'}]})
    for sid in ['a-e', 'twelve-bar']:
        pg.evaluate("h=>{location.hash=h}", sid); pg.wait_for_timeout(60)
        for i in range(5):
            for _ in range(2): pg.click(f'[data-lv="{sid}:{i}"][data-dir="1"]')
    pg.evaluate("()=>{location.hash='am-e7'}"); pg.wait_for_timeout(60); pg.click('[data-lv="am-e7:0"][data-dir="1"]')
    saveA = raw(pg); A = json.loads(saveA)
    pg.evaluate("()=>{location.hash='record'}"); pg.wait_for_timeout(60); bk = {'0.9': backup(pg)}
    pg2 = old_page(b, '0.9'); pg2.click('[data-lv="a-e:0"][data-dir="1"]'); saveB = raw(pg2); B = json.loads(saveB)
    print('0.9 save A: levels', len(A['lv']), 'gates', list(A['gates']), 'journal', len(A['journal']), '| save B lv', B['lv'], 'keys', sorted(B.keys()))
    for ver in ['0.8', '0.7']:
        q = old_page(b, ver, raw=saveA); q.evaluate("()=>{location.hash='record'}"); q.wait_for_timeout(80); bk[ver] = backup(q)
    print({v: (json.loads(t).get('version'), len(t)) for v, t in bk.items()})

    # --- 5a returning with levels/gates/journal
    for name, sv, S0 in [('(a) levels+gates+journal', saveA, A), ('(b) one level only', saveB, B), ('(b2) bare {"lv":{"a-e:0":1}}', '{"lv":{"a-e:0":1}}', {'lv': {'a-e:0': 1}}), ('(c) journal entry only', json.dumps({'journal': A['journal']}), {'journal': A['journal']})]:
        pg = open_page(b, raw=sv)
        same = raw(pg) == sv
        rec(f'5 returning {name}: First Steps skipped, all 7 tabs, save untouched at start-up', view(pg) == 'v-path' and tabs(pg) == ALL7 and same and pg.evaluate("()=>!!document.querySelector('#fsLink')") and 'is open' not in pg.evaluate("()=>document.querySelector('#tabMsg').innerText"), (view(pg), tabs(pg), 'bytes identical' if same else 'rewritten'))
        reach = []
        for h in ['warm-up', 'rudiments', 'technique', 'invent', 'gig', 'record']:
            pg.evaluate("h=>{location.hash=h}", h); pg.wait_for_timeout(50); reach.append(view(pg))
        rec(f'5 returning {name}: every tab opens', reach == ['v-warm-up', 'v-rudiments', 'v-technique', 'v-invent', 'v-gig', 'v-record'], reach)
        # visit First Steps, pass a check, come back: nothing lost, tabs kept
        pg.evaluate("()=>{location.hash='path'}"); pg.wait_for_timeout(50); pg.click('#fsLink'); pg.wait_for_timeout(60); pg.click('[data-fgo="2"]'); pg.check('[data-ftick="2"]')
        s = st(pg); lost = [k for k in S0 if json.dumps(s.get(k), sort_keys=True) != json.dumps(S0[k], sort_keys=True) and k != 'gig']
        pg.reload(); pg.wait_for_selector('#tabs a[aria-current=page]', state='attached'); pg.evaluate("()=>{location.hash='path'}"); pg.wait_for_timeout(60)
        rec(f'5 returning {name}: after passing a First Steps check and reloading, nothing lost and all tabs kept', not lost and tabs(pg) == ALL7 and s['fs'].get('complete') is True and view(pg) == 'v-path', (lost, s['fs'], tabs(pg)))
        rec(f'5 returning {name}: no console errors', not pg.errors, pg.errors)
    # (b3) the one level is lowered back to nothing, then reload
    pg = open_page(b, raw='{"lv":{"a-e:0":1}}'); pg.click('[data-lv="a-e:0"][data-dir="-1"]'); pg.wait_for_timeout(60)
    if st(pg)['lv'].get('a-e:0'): pg.click('[data-lv="a-e:0"][data-dir="-1"]'); pg.wait_for_timeout(60)
    lv = st(pg)['lv']; t_now = tabs(pg); v_now = view(pg); pg.reload(); pg.wait_for_selector('#tabs a[aria-current=page]', state='attached')
    rec('5 returning (b3): a 0.9 student who lowers their only level to nothing keeps their tabs', tabs(pg) == ALL7 and view(pg) == 'v-path', {'lv after lowering': lv, 'fs': st(pg).get('fs'), 'tabs straight after': t_now, 'view straight after': v_now, 'tabs after reload': tabs(pg), 'view after reload': view(pg)})
    # (d) only fs set
    pg = open_page(b, state={'fs': {'done': [1, 2, 3, 4, 5, 6, 7], 'complete': True, 'placed': False}})
    rec('5 a save with only fs complete: Path + Record', view(pg) == 'v-path' and tabs(pg) == ['Path', 'Record'], tabs(pg))
    # hostile fs values
    for bad in ['{"fs":"yes"}', '{"fs":{"done":"all","complete":"true"}}', '{"fs":{"done":[9,"x",1,1],"complete":1,"seen":[3,"gig"]}}', '{"fs":null}', '{"fs":[]}', 'not json']:
        pg = open_page(b, raw=bad); rec(f'5 odd fs value {bad} loads as a first visit without errors', view(pg) == 'v-first-steps' and tabs(pg) == ['First Steps'] and not pg.errors, (view(pg), tabs(pg), pg.errors))

    # --- imports from a fresh page
    def imp(text, start=None):
        pg = open_page(b, state=start); 
        if view(pg) == 'v-first-steps': pg.click('a.lk[href="#record"]')
        else: pg.evaluate("()=>{location.hash='record'}")
        pg.wait_for_timeout(80); v0 = view(pg); pg.fill('#bkIn', text); pg.click('#bkImport'); pg.wait_for_timeout(60)
        ask = pg.evaluate("()=>document.querySelector('#bkAsk').innerText")
        if pg.query_selector('#bkYes'): pg.click('#bkYes'); pg.wait_for_timeout(100)
        return pg, v0, ask
    for ver in ['0.7', '0.8', '0.9']:
        pg, v0, ask = imp(bk[ver]); s = st(pg)
        ok = v0 == 'v-record' and all(json.dumps(s[k], sort_keys=True) == json.dumps(A[k], sort_keys=True) for k in ['lv', 'gates', 'journal']) and tabs(pg) == ALL7
        pg.evaluate("()=>{location.hash='path'}"); pg.wait_for_timeout(60)
        rec(f'5 a {ver} backup imports on a first visit: progress restored, First Steps skipped, all tabs', ok and view(pg) == 'v-path' and not pg.errors and pg.evaluate("()=>window.__dlg") == [], (v0, tabs(pg), view(pg), ask[:90].replace('\n', ' '), pg.errors))
    pg, v0, ask = imp(saveA); s = st(pg); pg.evaluate("()=>{location.hash='path'}"); pg.wait_for_timeout(60)
    rec('5 bare 0.9 state imports: progress restored, all tabs', s['lv'] == A['lv'] and tabs(pg) == ALL7 and view(pg) == 'v-path', (tabs(pg), view(pg)))
    # 0.11 backup carries fs
    fs11 = {'done': [1, 2, 3, 4, 5, 6, 7], 'complete': True, 'placed': False, 'ear': True, 'line': 'Eggs And Dates Go Bad Early', 'seen': ['path', 'record']}
    pg = open_page(b, state={'fs': fs11}, hash_='record'); b11 = backup(pg); o = json.loads(b11)
    rec('5 0.11 backup: version 0.11 and state.fs included', o.get('version') == '0.11' and o['state'].get('fs') == fs11 and o.get('app') == 'The Guitar Lab', {k: o[k] for k in ['app', 'format', 'version']} | {'fs': o['state'].get('fs')})
    pg, v0, ask = imp(b11); s = st(pg); pg.reload(); pg.wait_for_selector('#tabs a[aria-current=page]', state='attached')
    rec('5 0.11 backup imported on a first visit: fs restored, Path + Record, survives reload', s.get('fs') == fs11 and st(pg).get('fs') == fs11 and tabs(pg) == ['Path', 'Record'], (s.get('fs'), tabs(pg), view(pg)))
    # half-way fs survives backup
    half = {'done': [1, 2, 3], 'complete': False, 'placed': False, 'line': 'x y'}
    pg = open_page(b, state={'fs': half}); pg.click('[data-fgo="1"]'); pg.click('a.lk[href="#record"]'); pg.wait_for_timeout(80); hb = backup(pg)
    pg, v0, ask = imp(hb); pg.click('#tabs a[href="#first-steps"]'); pg.wait_for_timeout(80)
    rec('5 half-way First Steps backup: resumes at step 4 after import', st(pg).get('fs') == half and 'step 4 of 7' in pg.evaluate("()=>document.querySelector('#v-first-steps .fst-eye').textContent"), st(pg).get('fs'))
    # a newer-format backup is refused with 0.11 named
    pg, v0, ask = imp(json.dumps({'app': 'The Guitar Lab', 'format': 2, 'version': '0.12', 'state': {'lv': {'a-e:0': 2}}}))
    msg = pg.evaluate("()=>document.querySelector('#bkMsg').innerText"); rec('5 newer-version message names 0.11', '0.11' in msg and st(pg) is None, msg)
    rec('5 key is only "shredder" after imports', pg.evaluate("()=>Object.keys(localStorage)") in ([], ['shredder']), pg.evaluate("()=>Object.keys(localStorage)"))
    # the import replaced a first-visit: empty 0.9 backup (no progress)
    q = old_page(b, '0.9', hash_='record'); empty = backup(q)
    pg, v0, ask = imp(empty); pg.evaluate("()=>{location.hash='path'}"); pg.wait_for_timeout(60)
    print('NOTE empty 0.9 backup imported on a first visit ->', view(pg), tabs(pg))

    # --- 6 other instruments
    for inst in ['bass', 'drums', 'keys', 'vocals']:
        sv = json.dumps({'inst': inst}); pg = open_page(b, raw=sv); o9 = old_page(b, '0.9', raw=sv)
        note = pg.evaluate("()=>(document.querySelector('#fsSoon')||{}).innerText||''"); n11 = pg.evaluate(NORM); n09 = o9.evaluate(NORM)
        rec(f'6 {inst} on a first visit: 0.9 Path, all tabs, "coming" note, no First Steps', view(pg) == 'v-path' and tabs(pg) == ALL7 and note == f'First Steps for {inst} is coming. Until then, every tab is open.' and n11 == n09 and not pg.errors, (tabs(pg), note, 'page body equals 0.9' if n11 == n09 else 'body differs from 0.9'))
        diffs = []
        for h in ['warm-up', 'rudiments', 'technique', 'invent', 'gig', 'record']:
            for x in (pg, o9): x.evaluate("h=>{location.hash=h}", h); x.wait_for_timeout(50)
            if pg.evaluate(NORM) != o9.evaluate(NORM): diffs.append(h)
        rec(f'6 {inst}: the other six tabs equal 0.9', not diffs, diffs)
    pg = open_page(b, raw='{"inst":"bass"}'); pg.click('[data-inst="guitar"]'); pg.wait_for_timeout(80); g = (view(pg), tabs(pg))
    pg.evaluate("()=>{location.hash='path'}"); pg.wait_for_timeout(60)
    print('NOTE new bass student switches to guitar ->', g, '; picker visible there:', pg.evaluate("()=>[...document.querySelectorAll('[data-inst]')].filter(e=>e.offsetParent).length"))
    # guitar student with full progress switches to bass and back
    pg = open_page(b, state={'fs': fs11}); pg.click('[data-inst="bass"]'); pg.wait_for_timeout(80); tb = tabs(pg); nt = pg.evaluate("()=>(document.querySelector('#fsSoon')||{}).innerText||''"); pg.click('[data-inst="guitar"]'); pg.wait_for_timeout(80)
    rec('6 guitar student (Path + Record) switches to bass: all tabs + note; back to guitar: Path + Record again', tb == ALL7 and 'bass is coming' in nt and tabs(pg) == ['Path', 'Record'] and pg.evaluate("()=>!document.querySelector('#fsSoon')"), (tb, nt, tabs(pg)))

    # --- 9 Path / Gig / Record against 0.9, same save, same moment
    for scheme in ['dark', 'light']:
        for w in [1280, 360]:
            n = open_page(b, raw=saveA, width=w, scheme=scheme); o = old_page(b, '0.9', raw=saveA, width=w, scheme=scheme); bad = []; shots = 0; shotbad = []
            for h in STAGES + ['gig', 'record', 'warm-up', 'rudiments', 'technique', 'invent']:
                for x in (n, o): x.evaluate("h=>{location.hash=h}", h); x.wait_for_timeout(70)
                if n.evaluate(NORM) != o.evaluate(NORM): bad.append(h)
                if h in ('a-e', 'hallelujah', 'gig', 'record'):
                    sel = '#v-path' if h in STAGES else '#v-' + h
                    for x in (n, o): x.evaluate("()=>{document.activeElement&&document.activeElement.blur();window.scrollTo(0,0);const l=document.querySelector('#fsLink');if(l)l.remove()}")
                    a_, b_ = n.locator(sel).screenshot(animations='disabled'), o.locator(sel).screenshot(animations='disabled'); shots += 1
                    if a_ != b_: shotbad.append(h)
            link = None
            n.evaluate("()=>{location.hash='a-e'}"); n.wait_for_timeout(60); link = n.evaluate("()=>{const a=document.querySelector('#fsLink');return a?[a.textContent,a.getAttribute('href'),a.parentElement.id||a.parentElement.className]:null}")
            rec(f'9 [{w} {scheme}] 8 stages of the Path, Gig, Record and the other tabs: page body equals 0.9 once version, First Steps link/tab are set aside', not bad, bad or '14 views identical')
            rec(f'9 [{w} {scheme}] element screenshots of Path (stages 1 and 7), Gig, Record pixel-identical to 0.9 with the First Steps link taken out', not shotbad, shotbad or f'{shots} identical')
            rec(f'9 [{w} {scheme}] the only addition on the Path is the First Steps link', link and link[:2] == ['First Steps', '#first-steps'], link)
    # stylesheet: rules that existed in 0.9 unchanged?
    def css(path):
        t = open(path, encoding='utf-8').read(); return t[t.index('<style>'):t.index('</style>')]
    c9, c11 = css(OLD['0.9']), css(str(ROOT / 'index.html'))
    l9, l11 = c9.split('\n'), c11.split('\n'); gone = [l for l in l9 if l not in l11]; new = [l for l in l11 if l not in l9]
    rec('9 every line of the 0.9 stylesheet is still present unchanged', not gone, [g[:140] for g in gone][:6])
    print('NOTE new stylesheet lines:', len(new), '; ones not starting with a First Steps selector:', [l[:110] for l in new if not re.match(r'\s*(/\*|\.fst|\.fsmode|#v-first-steps|#fs|\.tabnote|#tabMsg)', l)][:8])
    b.close()
json.dump(R, open(OUT / 'result_saves.json', 'w'), indent=1, default=str)
bad = [r for r in R if not r[1]]; print(f'\n{len(R) - len(bad)}/{len(R)} pass'); [print('FAIL', r[0], str(r[2])[:600]) for r in bad]
