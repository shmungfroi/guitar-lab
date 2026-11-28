"""Independent check, items 1-4, 8, 10 (dialogs, network): a first visit worked through by hand-derived answers."""
import sys, json, re, math
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from common import *
from playwright.sync_api import sync_playwright

R = []
def rec(k, ok, ev): R.append((k, bool(ok), ev)); print(('PASS ' if ok else 'FAIL ') + k + ' :: ' + str(ev)[:300], flush=True)

# my own tables (from the booklet terms and standard guitar facts, not from the app)
PARTS = {'headstock': 'headstock', 'machine heads': 'machineHeads', 'nut': 'nut', 'neck': 'neck', 'fingerboard': 'fingerboard', 'frets': 'frets',
         'position markers': 'positionMarkers', 'body': 'body', 'sound hole': 'soundHole', 'pickguard': 'pickguard', 'saddle': 'saddle', 'bridge': 'bridge',
         'strings': 'strings', 'pickups': 'pickups'}
SN = {6: 'low e', 5: 'a', 4: 'd', 3: 'g', 2: 'b', 1: 'high e'}
# chord: frets by string 6..1, fingers by string
CHD = {'D': ('xx0232', {3: 1, 2: 3, 1: 2}), 'Am': ('x02210', {4: 2, 3: 3, 2: 1}), 'C': ('x32010', {5: 3, 4: 2, 2: 1}), 'A': ('x02220', {4: 1, 3: 2, 2: 3})}
HZ = {6: 82.41, 5: 110.0, 4: 146.83, 3: 196.0, 2: 246.94, 1: 329.63}

def nxt_disabled(pg):
    return pg.evaluate("()=>{const b=document.querySelector('#fsNext');return b?b.disabled:null}")
def step_no(pg):
    return pg.evaluate("()=>document.querySelector('#v-first-steps .fst-eye').textContent")
def q(pg):
    return pg.evaluate("()=>{const z=document.querySelector('#fsQuiz');return {ask:z.dataset.ask||'',pass:z.dataset.pass||'',q:document.querySelector('#fsAsk').textContent,fb:(document.querySelector('#fsFb')||{}).textContent||'',eye:(z.querySelector('.fst-eye')||{}).textContent||'',opts:[...z.querySelectorAll('[data-fa]')].map(b=>[b.dataset.fa,b.textContent])}}")

def tap_point(pg, part, kind=None):
    """a point on a drawing where the top element belongs to this part"""
    return pg.evaluate("""([part])=>{const out=[];for(const g of document.querySelectorAll('.fst-plates [data-part="'+part+'"]')){for(const h of g.querySelectorAll('.hit')){const r=h.getBoundingClientRect();
      for(const [fx,fy] of [[.5,.5],[.5,.25],[.5,.75],[.25,.5],[.75,.5],[.2,.2],[.8,.8],[.1,.5],[.9,.5],[.5,.1],[.5,.9]]){const x=r.left+r.width*fx,y=r.top+r.height*fy;const e=document.elementFromPoint(x,y);
        if(e&&e.closest('[data-part]')&&e.closest('[data-part]').dataset.part===part&&e.closest('.fst-plates'))return [x,y]}}}return null}""", [part])

def answer_for(pg, d):
    """work the right answer out from what is on screen"""
    ask, text = d['ask'], d['q']
    if ask == 'lit':
        hl = pg.evaluate("()=>[...document.querySelectorAll('.fst-fig [data-part].hl')].map(e=>e.dataset.part)")
        assert len(set(hl)) == 1, hl
        return hl[0]
    if ask.startswith('part:'):
        m = re.match(r'Tap the (.+) on either guitar\.', text); return PARTS[m.group(1)]
    if ask.startswith('str-hl'):
        hl = pg.evaluate("()=>[...document.querySelectorAll('.fst-fig [data-string].hl')].map(e=>e.dataset.string)"); assert len(set(hl)) == 1, hl; return hl[0]
    if ask.startswith('str-num'):
        return re.search(r'number (\d)', text).group(1)
    if ask.startswith('str-name'):
        nm = re.search(r'number is the (.+) string', text).group(1).lower(); return str([k for k, v in SN.items() if v == nm][0])
    if ask.startswith('dia-'):
        ch = ask.split(':')[1]; fr, fg = CHD[ch]; at = lambda n: fr[6 - n]
        if 'Which finger' in text: return str(fg[int(re.search(r'string (\d)', text).group(1))])
        if 'which fret' in text: return at(int(re.search(r'string (\d)', text).group(1)))
        want = '0' if 'open' in text else 'x'
        return ','.join(str(n) for n in [6, 5, 4, 3, 2, 1] if at(n) == want)
    if ask.startswith('tab:'):
        i = int(ask.split(':')[1]); lines = pg.evaluate("()=>document.querySelector('.fst-fig .tab').textContent").split('\n')
        assert len(lines) == 6, lines
        ev = sorted((m.start(), ln + 1, m.group()) for ln, l in enumerate(lines) for m in re.finditer(r'\d+', l[2:]))
        col, string, fret = ev[i]; return f'{string}:{fret}'   # top line = string 1
    raise Exception('unknown ' + ask)

def give(pg, d, val):
    if d['ask'].startswith('part:'):
        pt = tap_point(pg, val)
        if not pt: return False
        pg.mouse.click(*pt)
    else:
        pg.click(f'#fsQuiz [data-fa="{val}"]')
    return True

def run_quiz(pg, step, label, wrong_first=True):
    pg.click('#fsQuizGo'); seen = []; wrong_done = not wrong_first; n = 0
    while n < 40:
        n += 1; d = q(pg)
        if d['pass']: break
        ans = answer_for(pg, d)   # the app's script is block-scoped, so its answer can't be read: agreement shows as the check passing in exactly the expected number of questions
        seen.append(d['ask'].split(':')[0] + ('' if d['ask'] != 'lit' else ':' + ans))
        if not wrong_done:
            if d['ask'].startswith('part:'):
                w = 'body' if ans != 'body' else 'headstock'
            else:
                w = [o[0] for o in d['opts'] if o[0] != str(ans)][0]
            eye0 = d['eye']; give(pg, d, w); d2 = q(pg)
            rec(f'{label} wrong answer explained, not counted, Next still blocked', d2['fb'].strip() != '' and d2['eye'] == eye0 and d2['q'] == d['q'] and nxt_disabled(pg) is True, f"fb={d2['fb']!r} eye={d2['eye']!r}")
            wrong_done = True; d = d2
        ok = give(pg, d, ans)
        if not ok: rec(f'{label} part {ans} can be tapped', False, 'no tappable point'); return seen
    d = q(pg); rec(f'{label} check passes after retry ({n-1} questions asked, {FQ[step]}+1 expected with one miss)', d['pass'] == '1' and (n - 1 == FQ[step] + (1 if wrong_first else 0)), seen)
    pg.click('#fsQuizEnd'); return seen
FQ = {1: 5, 3: 5, 5: 4, 6: 3}

def raise_stage(pg, sid):
    pg.evaluate("h=>{location.hash=h}", sid); pg.wait_for_timeout(80)
    for i in range(5):
        for _ in range(2): pg.click(f'[data-lv="{sid}:{i}"][data-dir="1"]')
    pg.evaluate("()=>{location.hash='path'}"); pg.wait_for_timeout(80)

def freqs(pg): return pg.evaluate("()=>window.__osc.map(o=>o.f)")

def main(width):
    L = f'[{width}] '
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS); pg = open_page(b, width=width, height=800 if width < 500 else 900)
        # 1 fresh visit
        vis = pg.evaluate("""()=>{const v=e=>{const s=getComputedStyle(e);return e.offsetParent!==null&&s.display!=='none'&&s.visibility!=='hidden'};
          return {views:[...document.querySelectorAll('[id^="v-"]')].filter(v).map(e=>e.id),mbar:[...document.querySelectorAll('.mbar')].filter(v).length,fin:v(document.querySelector('#finishes')),nsw:v(document.querySelector('#nswBtn')),
          inst:[...document.querySelectorAll('[data-inst]')].filter(v).length,next:v(document.querySelector('#next')),foot:[...document.querySelectorAll('.foot')].filter(v).length,tch:v(document.querySelector('#tchBtn')),neck:document.querySelector('#neck')?v(document.querySelector('#neck')):null,
          msg:document.querySelector('#tabMsg').textContent}}""")
        rec(L + '1 fresh: only First Steps view, step 1', vis['views'] == ['v-first-steps'] and 'step 1 of 7' in step_no(pg) and tabs(pg) == ['First Steps'] and not vis['mbar'] and not vis['fin'] and not vis['nsw'] and not vis['inst'] and not vis['next'], {**vis, 'tabs': tabs(pg), 'ls': st(pg)})
        rec(L + '1 fresh: nothing saved before the student does anything', st(pg) is None, st(pg))
        # dots 2-7 disabled, hash jumps blocked
        dis = pg.evaluate("()=>[...document.querySelectorAll('.fst-dots button')].map(b=>b.disabled)")
        blocked = []
        for h in ['path', 'gig', 'warm-up', 'rudiments', 'technique', 'invent', 'a-e', 'hallelujah']:
            pg.evaluate("h=>{location.hash=h}", h); pg.wait_for_timeout(60); blocked.append(pg.evaluate("()=>[...document.querySelectorAll('[id^=\"v-\"]')].filter(e=>!e.classList.contains('hide')).map(e=>e.id).join()"))
        pg.evaluate("()=>{location.hash='first-steps'}"); pg.wait_for_timeout(60)
        rec(L + '1 dots 2-7 locked; typing #path, #gig etc. stays on First Steps', dis == [False] + [True] * 6 and set(blocked) == {'v-first-steps'}, (dis, set(blocked)))
        rec(L + '1 step 1: Next disabled before the check', nxt_disabled(pg) is True, nxt_disabled(pg))
        # step 1 lesson: tap a part shows its words
        names = pg.evaluate("()=>[...document.querySelectorAll('[data-fname]')].map(b=>b.textContent)")
        caps = {}
        for nm in pg.evaluate("()=>[...document.querySelectorAll('[data-fname]')].map(b=>b.dataset.fname)"):
            pg.click(f'[data-fname="{nm}"]'); caps[nm] = pg.evaluate("()=>document.querySelector('#fsCap').innerText")
        rec(L + '2 step 1 names = booklet terms (+2 electric extras)', [n.lower() for n in names[:14]] == list(PARTS.keys()), names)
        need = {'machineHeads': 'tuning pegs', 'headstock': 'head', 'fingerboard': 'fretboard'}
        rec(L + '2 step 1 alternative names given (tuning pegs, head, fretboard)', all(v in caps[k].lower() for k, v in need.items()), {k: caps[k] for k in need})
        if width >= 600:
            # every part can be tapped on a drawing in the lesson
            miss = [pid for pid in PARTS.values() if not tap_point(pg, pid)]
            rec(L + '1 every booklet part has a tappable spot on a drawing', not miss, miss)
            pt = tap_point(pg, 'nut'); pg.mouse.click(*pt); rec(L + '1 tapping the drawing names the part', 'Nut' in pg.evaluate("()=>document.querySelector('#fsCap').innerText"), pg.evaluate("()=>document.querySelector('#fsCap').innerText"))
        s1 = run_quiz(pg, 1, L + 'step 1')
        if width >= 600:
            rec(L + 'step 1 at this width asks by tapping the drawing', all(x.startswith('part') for x in s1), s1)
        else:
            rec(L + 'step 1 on a phone asks with a lit part and four name buttons', all(x.startswith('lit') for x in s1), s1)
        rec(L + '1 step 1 passed: Next enabled, fs.done=[1]', nxt_disabled(pg) is False and st(pg)['fs']['done'] == [1], st(pg))
        pg.click('#fsNext')
        # step 2
        t2 = pg.evaluate("()=>document.querySelector('#v-first-steps').innerText")
        rec(L + '2 step 2 content: three cards, T 1 2 3 4, picking signs, left-hander', all(x in t2 for x in ['Sit tall', 'Hold the pick', 'Fret it cleanly', 'T thumb, 1 index, 2 middle, 3 ring, 4 little', 'downstroke', 'upstroke', 'Left-handed?', 'waist', 'right leg', 'thumb behind the neck']) and nxt_disabled(pg) is True, 'Next disabled=%s' % nxt_disabled(pg))
        hand = pg.evaluate("()=>[...document.querySelectorAll('.fst-card svg text')].map(t=>t.textContent).join(' ')")
        rec(L + '2 step 2 hand drawing carries T 1 2 3 4', hand == 'T 1 2 3 4', hand)
        pg.check('[data-ftick="2"]'); rec(L + '1 step 2 tick enables Next', nxt_disabled(pg) is False, '')
        pg.uncheck('[data-ftick="2"]'); rec(L + '1 step 2 untick blocks Next again', nxt_disabled(pg) is True and 2 not in st(pg)['fs']['done'], st(pg)['fs'])
        pg.check('[data-ftick="2"]'); pg.click('#fsNext')
        # step 3
        t3 = pg.evaluate("()=>document.querySelector('#v-first-steps').innerText")
        rec(L + '2 step 3 content', all(x in t3 for x in ['E A D G B E', 'String 6 is the thickest', 'low E', 'String 1 is the thinnest', 'high E', 'memory line']) and nxt_disabled(pg) is True, '')
        pg.fill('#fsLine', 'Every Australian Dog Goes Barking Early'); rec(L + '2 step 3 own memory line saved in fs.line', st(pg)['fs'].get('line') == 'Every Australian Dog Goes Barking Early', st(pg)['fs'])
        n0 = pg.evaluate("()=>window.__buf.length"); pg.click('[data-fpl="6"]'); pg.wait_for_timeout(150)
        rec(L + '8 step 3 string buttons sound (pluck sample)', pg.evaluate("()=>window.__buf.length") > n0, '')
        s3 = run_quiz(pg, 3, L + 'step 3'); rec(L + '2 step 3 quiz mixes lit string / number / name', {x for x in s3} >= {'str-hl', 'str-num', 'str-name'}, s3)
        pg.reload(); pg.wait_for_selector('#v-first-steps h2')
        rec(L + '5 reload mid-way resumes at the first unpassed step with the memory line kept', 'step 4 of 7' in step_no(pg) and st(pg)['fs']['done'] == [1, 2, 3], (step_no(pg), st(pg)['fs']))
        # step 4
        t4 = pg.evaluate("()=>document.querySelector('#v-first-steps').innerText"); title = pg.evaluate("()=>document.querySelector('#v-first-steps h2').textContent")
        home = pg.evaluate("()=>document.querySelector('#fsHome').innerText"); outside = t4.replace(home, '')
        peg = re.findall(r'[^.]*\b(?:[Tt]urn|[Tt]ighten|[Ll]oosen|[Tt]une up|[Tt]wist)\b[^.]*\.', outside)
        rec(L + '2 step 4 is "Hear the open strings"; no peg-turning instruction outside the home box', title == 'Hear the open strings' and not peg and 'Leave the machine heads alone' in outside and 'Sing it first' in outside and 'Your own guitar at home' in home and 'machine head' in home and 'tuner' in home.lower(), {'title': title, 'turn sentences outside box': peg})
        got = {}
        for n in [6, 5, 4, 3, 2, 1]:
            k = len(freqs(pg)); pg.click(f'[data-fref="{n}"]'); pg.wait_for_timeout(120); f = freqs(pg)[k:]; got[n] = round(f[0], 2) if f else None
            if n == 6:
                pg.wait_for_timeout(3000); rep = len(freqs(pg)) - k
            pg.click(f'[data-fref="{n}"]')
        k = len(freqs(pg)); pg.wait_for_timeout(3000)
        rec(L + '8 reference tones E2 A2 D3 G3 B3 E4', all(abs(got[n] - HZ[n]) < 0.01 for n in HZ), got)
        rec(L + '8 a reference note repeats until tapped again, then stops', rep >= 2 and len(freqs(pg)) == k, f'starts in 3 s: {rep}; after stop: {len(freqs(pg)) - k}')
        tickdis = pg.evaluate("()=>document.querySelector('[data-ftick=\"4\"]').disabled")
        rec(L + '1 step 4: honour tick locked until the ear check is passed; Next blocked', tickdis and nxt_disabled(pg) is True, '')
        gaps = []; wrong_fb = ''
        for i in range(4):
            eye = pg.evaluate("()=>document.querySelector('#fsEar .fst-eye').textContent")
            k = len(freqs(pg)); pg.click('#fsEarPlay'); pg.wait_for_timeout(80); f = freqs(pg)[k:]; semi = 12 * math.log2(f[1] / f[0]); gaps.append(round(semi, 2))
            if i == 0:
                pg.click('[data-ear="%s"]' % ('down' if semi > 0 else 'up')); wrong_fb = pg.evaluate("()=>document.querySelector('#fsEar .fst-fb').textContent")
                eye2 = pg.evaluate("()=>document.querySelector('#fsEar .fst-eye').textContent")
                rec(L + '1 ear check: wrong answer explained, stays on the same pair, buttons need a fresh listen', wrong_fb != '' and eye2 == eye and pg.evaluate("()=>document.querySelector('[data-ear=up]').disabled"), wrong_fb)
                k = len(freqs(pg)); pg.click('#fsEarPlay'); pg.wait_for_timeout(80); f = freqs(pg)[k:]; semi = 12 * math.log2(f[1] / f[0])
            pg.click('[data-ear="%s"]' % ('up' if semi > 0 else 'down'))
        rec(L + '2 ear check: 4 pairs, gaps (semitones) big to small, all >= 1', [abs(round(g)) for g in gaps] == [24, 14, 5, 1], gaps)
        rec(L + '1 ear passed -> tick unlocked; tick -> Next', pg.evaluate("()=>!document.querySelector('[data-ftick=\"4\"]').disabled") and nxt_disabled(pg) is True, st(pg)['fs'])
        pg.check('[data-ftick="4"]'); ok4 = nxt_disabled(pg) is False; pg.click('#fsNext')
        # step 5
        t5 = pg.evaluate("()=>document.querySelector('#v-first-steps').innerText")
        rec(L + '2 step 5 content', ok4 and all(x in t5 for x in ['String 6, low E, is on the left', 'thick line at the top is the nut', '1 index, 2 middle, 3 ring, 4 little', 'T means thumb', 'play it open', "don't play it"]) and nxt_disabled(pg) is True, '')
        run_quiz(pg, 5, L + 'step 5'); pg.click('#fsNext')
        # step 6
        t6 = pg.evaluate("()=>document.querySelector('#v-first-steps').innerText"); tab = pg.evaluate("()=>document.querySelector('.fst-fig .tab').textContent")
        rec(L + '2 step 6: TAB top line = string 1 (text and printed TAB)', 'The top line is string 1, high E' in t6 and 'bottom line is string 6, low E' in t6 and tab.split('\n')[0][0].lower() == 'e' and tab.split('\n')[5].startswith('E|-3') and "doesn't show rhythm" in t6 and '0 means play the string open' in t6 and nxt_disabled(pg) is True, tab)
        k = pg.evaluate("()=>window.__buf.length"); pg.click('.fst-fig [data-ftab]'); pg.wait_for_timeout(200); rec(L + '8 step 6 TAB play-back sounds (3 notes + 6-note chord = 9 starts)', pg.evaluate("()=>window.__buf.length") - k == 9, pg.evaluate("()=>window.__buf.length") - k)
        run_quiz(pg, 6, L + 'step 6'); pg.click('#fsNext')
        # step 7
        t7 = pg.evaluate("()=>document.querySelector('#v-first-steps').innerText"); tab7 = pg.evaluate("()=>document.querySelector('.fst-fig .tab').textContent")
        em = pg.evaluate("()=>{const s=document.querySelector('.fst-fig svg');return (s.getAttribute('aria-label')||'')+' | '+[...s.querySelectorAll('text')].map(t=>t.textContent).join(' ')}")
        rec(L + '2 step 7: Em then E-F-G on string 1, Sing it first', all(x in t7 for x in ['E minor', 'Finger 2 goes on string 5', 'Finger 3 goes on string 4', 'open, fret 1, fret 3', 'E, F and G', 'Sing it first']) and tab7.split('\n')[0].replace('-', '').replace('|', '') == 'e013' and all(l.strip('EADGB|-') == '' for l in tab7.split('\n')[1:]), (tab7, em))
        sb = pg.evaluate("()=>{const b=document.querySelector('#fsStart');return [b.textContent,b.disabled]}")
        rec(L + '1 step 7: Start the Path disabled before the tick', sb == ['Start the Path', True], sb)
        k = pg.evaluate("()=>window.__buf.length"); ko = len(freqs(pg)); pg.click('#fsBand'); pg.wait_for_timeout(9500); nb = pg.evaluate("()=>window.__buf.length") - k; lab = pg.evaluate("()=>document.querySelector('#fsBand').textContent")
        oo = pg.evaluate("k=>window.__osc.slice(k).map(o=>[+(o.when-window.__osc[k].when).toFixed(2),Math.round(o.f)])", ko); clicks = [o for o in oo if o[1] >= 1000]; pad = sorted({o[1] for o in oo if o[1] < 1000})
        pg.click('#fsBand'); pg.wait_for_timeout(150); k2 = pg.evaluate("()=>window.__buf.length+window.__osc.length"); pg.wait_for_timeout(1500)
        rec(L + '8 step 7 band: count-in of 6 clicks, then E minor (E G B) with strums; Stop silences it', nb >= 12 and len(clicks) == 6 and {330, 247, 196} <= set(pad) and lab == 'Stop' and pg.evaluate("()=>window.__buf.length+window.__osc.length") == k2 and pg.evaluate("()=>document.querySelector('#fsBand').textContent") == 'Play with the band', f'clicks at {[c[0] for c in clicks]} s; sustained pitches (Hz) {pad}; {nb} sample starts in 9.5 s')
        pg.check('[data-ftick="7"]'); pg.click('#fsStart'); pg.wait_for_timeout(150)
        s = st(pg)
        rec(L + '4 Start the Path: Path view, stage 1 (a-e), tabs Path + Record', pg.evaluate("()=>location.hash") == '#path' and s['stage'] == 'a-e' and tabs(pg) == ['Path', 'Record'] and s['fs']['complete'] is True and s['fs']['done'] == [1, 2, 3, 4, 5, 6, 7], (tabs(pg), s['fs'], pg.evaluate("()=>document.querySelector('#next').innerText")[:90]))
        rec(L + '4 "New for you" notice names Path and Record once', 'Path is open' in pg.evaluate("()=>document.querySelector('#tabMsg').innerText") and 'Record is open' in pg.evaluate("()=>document.querySelector('#tabMsg').innerText"), pg.evaluate("()=>document.querySelector('#tabMsg').innerText"))
        rec(L + '4 First Steps link on the Path; instrument picker now shown', pg.evaluate("()=>!!document.querySelector('#fsLink')&&document.querySelector('#fsLink').offsetParent!==null") and pg.evaluate("()=>[...document.querySelectorAll('[data-inst]')].filter(e=>e.offsetParent).length") == 5, '')
        for h in ['gig', 'rudiments']:
            pg.evaluate("h=>{location.hash=h}", h); pg.wait_for_timeout(60)
        rec(L + '4 unopened tabs cannot be reached by typing the address', pg.evaluate("()=>[...document.querySelectorAll('[id^=\"v-\"]')].filter(e=>!e.classList.contains('hide')).map(e=>e.id).join()") == 'v-path', '')
        # gates, live, through the Path's own level buttons
        raise_stage(pg, 'a-e')
        m1 = pg.evaluate("()=>document.querySelector('#tabMsg').innerText"); tb1 = tabs(pg)
        rec(L + '4 stage 1 gate -> + Warm-up, Rudiments, announced', tb1 == ['Path', 'Warm-up', 'Rudiments', 'Record'] and 'Rudiments is open' in m1 and 'Warm-up is open' in m1, (tb1, m1))
        raise_stage(pg, 'twelve-bar')
        m2 = pg.evaluate("()=>document.querySelector('#tabMsg').innerText"); tb2 = tabs(pg)
        rec(L + '4 stage 2 gate -> + Technique, Invent, Gig, announced', tb2 == ['Path', 'Warm-up', 'Rudiments', 'Technique', 'Invent', 'Gig', 'Record'] and all(x + ' is open' in m2 for x in ['Technique', 'Invent', 'Gig']) and 'Rudiments is open' not in m2, (tb2, m2))
        pg.reload(); pg.wait_for_selector('#next'); rec(L + '4 after reload: tabs kept, notice not repeated', tabs(pg) == tb2 and 'is open' not in pg.evaluate("()=>document.querySelector('#tabMsg').innerText"), tabs(pg))
        # a tab once opened stays if the level drops
        pg.evaluate("()=>{location.hash='a-e'}"); pg.wait_for_timeout(80); pg.click('[data-lv="a-e:0"][data-dir="-1"]'); pg.wait_for_timeout(50)
        if st(pg)['lv'].get('a-e:0') == 2: pg.click('[data-lv="a-e:0"][data-dir="-1"]')
        rec(L + '4 (set-up) level lowered through the UI', st(pg)['lv'].get('a-e:0') == 1 and 'a-e' not in st(pg)['gates'], st(pg)['gates']); rec(L + '4 a tab that has opened stays open if a level later drops', tabs(pg) == tb2, tabs(pg))
        # revisit First Steps
        pg.click('#fsLink'); pg.wait_for_timeout(80)
        rec(L + '4 First Steps link revisits step 1 without losing progress', 'step 1 of 7' in step_no(pg) and st(pg)['fs']['complete'] and st(pg)['lv']['twelve-bar:0'] == 2 and pg.evaluate("()=>!!document.querySelector('a[href=\"#path\"].lk')"), step_no(pg))
        rec(L + '5 localStorage holds only the key shredder', pg.evaluate("()=>Object.keys(localStorage)") == ['shredder'], pg.evaluate("()=>Object.keys(localStorage)"))
        rec(L + '10 no alert/confirm/prompt called; no console errors', pg.evaluate("()=>window.__dlg") == [] and not pg.errors, (pg.evaluate("()=>window.__dlg"), pg.errors))
        ext = [u for u in pg.reqs if not u.startswith('file://') and not u.startswith('data:') and not u.startswith('about:') and not u.startswith('blob:')]
        rec(L + '10 no network requests (file:// only)', not ext, (len(pg.reqs), ext[:3], sorted({u.rsplit('/', 1)[-1].split('#')[0] for u in pg.reqs})))
        b.close()

def placement(width):
    L = f'[{width}] placement '
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        # all correct
        pg = open_page(b, width=width); pg.click('#fsPlaceGo'); kinds = []
        for i in range(8):
            d = q(pg); kinds.append(d['ask'].split(':')[0]); ans = answer_for(pg, d); give(pg, d, ans); pg.wait_for_timeout(40)
        s = st(pg)
        rec(L + 'all 8 correct -> Path opens at stage 1, fs complete + placed', pg.evaluate("()=>location.hash") == '#path' and s['fs']['complete'] and s['fs']['placed'] and tabs(pg) == ['Path', 'Record'] and s['stage'] == 'a-e', (kinds, s['fs'], tabs(pg)))
        rec(L + '8 items drawn from steps 1, 3, 5, 6', len(kinds) == 8 and {k.split('-')[0] for k in kinds} == ({'part', 'str', 'dia', 'tab'} if width >= 600 else {'lit', 'str', 'dia', 'tab'}), kinds)
        # one wrong on each family in turn
        for wrong_i, want in [(0, [1]), (2, [3]), (4, [5]), (7, [6]), (3, [3])]:
            pg = open_page(b, width=width); pg.click('#fsPlaceGo')
            for i in range(8):
                d = q(pg); ans = answer_for(pg, d)
                if i == wrong_i:
                    if d['ask'].startswith('part:'): ans = 'body' if ans != 'body' else 'headstock'
                    else: ans = [o[0] for o in d['opts'] if o[0] != str(ans)][0]
                give(pg, d, ans); pg.wait_for_timeout(40)
            txt = pg.evaluate("()=>document.querySelector('#v-first-steps').innerText"); miss = pg.evaluate("()=>document.querySelector('#fsPlace').dataset.miss")
            s = st(pg); pg.click('#fsPlaceOpen'); stp = step_no(pg)
            rec(L + f'question {wrong_i+1} wrong -> told step {want}, opens it, Path stays shut', miss == ','.join(map(str, want)) and f'step {want[0]} of 7' in stp and not s['fs']['complete'] and tabs(pg) == ['First Steps'] and '7 of 8 right' in txt and nxt_disabled(pg) is True, (miss, stp, s['fs'], txt.replace('\n', ' ')[:160]))
            if wrong_i == 2:
                # pass step 3 and the Path should be startable from step 7
                run_quiz(pg, 3, L + 'after routing, step 3', wrong_first=False)
                pg.click('[data-fgo="7"]'); sb = pg.evaluate("()=>{const b=document.querySelector('#fsStart');return [b.textContent,b.disabled]}"); pg.click('#fsStart'); pg.wait_for_timeout(100)
                rec(L + 'after passing the missed step, Start the Path opens the Path', sb == ['Start the Path', False] and pg.evaluate("()=>location.hash") == '#path' and st(pg)['fs']['complete'], (sb, st(pg)['fs']))
        # two wrong in different steps; quitting keeps nothing
        pg = open_page(b, width=width); pg.click('#fsPlaceGo'); d = q(pg); give(pg, d, answer_for(pg, d)); pg.click('#fsPlaceQuit')
        rec(L + 'quitting part-way returns to step 1 with nothing saved', 'step 1 of 7' in step_no(pg) and st(pg) is None, st(pg))
        # teacher mode from a fresh page
        pg.click('#tchBtn'); pg.wait_for_timeout(80); t1 = tabs(pg); pg.evaluate("()=>{location.hash='gig'}"); pg.wait_for_timeout(80); v = pg.evaluate("()=>[...document.querySelectorAll('[id^=\"v-\"]')].filter(e=>!e.classList.contains('hide')).map(e=>e.id).join()")
        rec(L + '4 teacher mode on a fresh page: all tabs, First Steps available not forced', set(t1) >= {'Path', 'Warm-up', 'Rudiments', 'Technique', 'Invent', 'Gig', 'Record', 'First Steps'} and v == 'v-gig', (t1, v))
        pg.click('#tchBtn'); pg.wait_for_timeout(80); rec(L + '4 teacher mode off again: student is back in First Steps only', tabs(pg) == ['First Steps'], tabs(pg))
        rec(L + '10 no dialogs / console errors', pg.evaluate("()=>window.__dlg") == [] and not pg.errors, pg.errors)
        b.close()

if __name__ == '__main__':
    for w in (1280, 360):
        main(w); placement(w)
    json.dump(R, open(OUT / 'result_flow.json', 'w'), indent=1, default=str)
    bad = [r for r in R if not r[1]]; print(f'\n{len(R) - len(bad)}/{len(R)} pass'); [print('FAIL', r[0], r[2]) for r in bad]
