"""Independent check, items 7, 10, 11: artwork framing, highlights in both themes, phone targets, screenshots, and the sweep."""
import sys, json, io, re, hashlib
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from common import *
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
R = []
def rec(k, ok, ev): R.append((k, bool(ok), ev)); print(('PASS ' if ok else 'FAIL ') + k + ' :: ' + str(ev)[:420], flush=True)
SH = OUT / 'shots'; SH.mkdir(exist_ok=True)
ALLFS = {'fs': {'done': [1, 2, 3, 4, 5, 6], 'complete': False, 'placed': False}}
RET = {'lv': {f'{s}:{i}': 2 for s in ['a-e', 'twelve-bar'] for i in range(5)}, 'journal': [{'d': 1795000000000, 't': 'A and E felt steadier', 'inst': 'guitar'}]}
MEAS = r"""()=>{const vw=document.documentElement.clientWidth,root=document.querySelector('#v-first-steps');const vis=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'};
 const small=[],out=[];for(const e of root.querySelectorAll('button,input,a,label.chk')){if(!vis(e)||e.disabled)continue;let r=e.getBoundingClientRect();if(e.matches('input[type=checkbox]')&&e.closest('label'))r=e.closest('label').getBoundingClientRect();
  if(r.height<43.5||r.width<43.5)small.push((e.id||e.dataset.fa||e.dataset.fgo&&'dot'+e.dataset.fgo||e.textContent.trim().slice(0,22)||e.tagName)+' '+Math.round(r.width)+'x'+Math.round(r.height))}
 for(const e of root.querySelectorAll('p,h2,h3,button,figure,.tab,.fst-zoom,.fst-turn,.fst-card,svg,input')){if(!vis(e))continue;const r=e.getBoundingClientRect();if(e.closest('.fst-zoom,.fst-turn')&&!e.matches('.fst-zoom,.fst-turn'))continue;if(r.right>vw+1||r.left<-1)out.push(e.tagName+'.'+e.className+' '+Math.round(r.left)+'..'+Math.round(r.right))}
 const fs=[...root.querySelectorAll('p,button,label,li,figcaption,span')].filter(vis).map(e=>parseFloat(getComputedStyle(e).fontSize));
 return {small,out,minFont:Math.min(...fs),over:document.documentElement.scrollWidth-vw,h:document.documentElement.scrollHeight}}"""

def img(b): return Image.open(io.BytesIO(b)).convert('RGB')

with sync_playwright() as p:
    b = p.chromium.launch(args=ARGS)
    # --- 7 the plate inside every frame is exactly what guitarArt() returns
    pg = open_page(b, state=ALLFS); acc = pg.evaluate("()=>typeof guitarArt")
    print('guitarArt reachable from the page:', acc)
    frames = {}
    for n in range(1, 8):
        pg.click(f'[data-fgo="{n}"]')
        frames[n] = pg.evaluate(r"""()=>[...document.querySelectorAll('#v-first-steps .fst-fig svg.ga, #v-first-steps .fst-fig svg[class*="ga"]')].map(s=>{const w=s.parentElement,ww=w.parentElement;const o={label:s.getAttribute('aria-label'),viewBox:s.getAttribute('viewBox'),svgStyle:s.getAttribute('style')||'',svgTransform:getComputedStyle(s).transform,
            wrapClass:ww.className||w.className,wrapStyle:w.getAttribute('style')||'',html:s.outerHTML};
            if(typeof guitarArt==='function'){const kind=/electric/.test(o.label)?'electric':'acoustic';const cands=[];for(const labels of [true,false])for(const st of [false,true])cands.push(guitarArt({kind,theme:'auto',labels,stringTargets:st}));
              const t=document.createElement('div');o.same=cands.some(c=>{t.innerHTML=c;const nz=x=>x.replace(/ga\d+/g,'gaN');return nz(t.firstElementChild.outerHTML)===nz(o.html)})}
            o.sha=null;o.len=o.html.length;delete o.html;return o})""")
    for n, fr in frames.items(): print(' step', n, [(f['wrapClass'], f['wrapStyle'][:70], f['viewBox'], f.get('same'), f['svgTransform']) for f in fr])
    flat = [f for fr in frames.values() for f in fr]
    rec('7 every plate shown in steps 1-6 is guitarArt() output unaltered (same markup once the per-call id counter ga1, ga2... is set aside, own viewBox 0 0 560 832, no transform or style on the svg itself); turning and cropping are on wrapper divs only', len(flat) >= 7 and all(f.get('same') and f['viewBox'] == '0 0 560 832' and f['svgTransform'] == 'none' and f['svgStyle'] == '' for f in flat), {n: [(f['wrapClass'], f['wrapStyle']) for f in fr] for n, fr in frames.items()})
    # proportions kept: rendered width/height ratio of each svg = 560/832 (uniform scale, so no stretch)
    ratios = []
    for n in range(1, 7):
        pg.click(f'[data-fgo="{n}"]'); ratios += pg.evaluate("()=>[...document.querySelectorAll('#v-first-steps .fst-fig svg[class*=\"ga\"]')].map(s=>+(s.clientWidth/s.clientHeight).toFixed(4))")
    rec('7 no plate is stretched: every rendered width/height = 560/832 = 0.6731', all(abs(r - 560 / 832) < 0.004 for r in ratios), sorted(set(ratios)))

    # --- 7 highlights visible, both themes: every part (lit close-up as on a phone) and every string
    for scheme in ['dark', 'light']:
        pg = open_page(b, width=360, height=800, scheme=scheme, state=ALLFS); pg.click('[data-fgo="1"]'); seen = {}
        for _ in range(140):
            if len(seen) == 14: break
            pg.click('#fsQuizGo'); part = pg.evaluate("()=>{const e=document.querySelector('.fst-fig [data-part].hl');return e&&e.dataset.part}")
            if part and part not in seen:
                fig = pg.locator('.fst-fig figure').first; fig.scroll_into_view_if_needed(); a = img(fig.screenshot())
                pg.evaluate("()=>document.querySelectorAll('.fst-fig .hl').forEach(e=>e.classList.replace('hl','hl-off'))"); c = img(fig.screenshot())
                pg.evaluate("()=>document.querySelectorAll('.fst-fig .hl-off').forEach(e=>e.classList.replace('hl-off','hl'))")
                d = ImageChops.difference(a, c).convert('L'); px = sum(1 for v in d.get_flattened_data() if v > 40); mx = max(d.get_flattened_data())
                seen[part] = (px, mx)
                if part in ('saddle', 'nut', 'frets', 'strings', 'positionMarkers', 'machineHeads'): a.save(SH / f'lit_{part}_360_{scheme}.png')
            pg.click('#fsQuizEnd')
        weak = {k: v for k, v in seen.items() if v[0] < 250 or v[1] < 80}
        rec(f'7 [{scheme}] lit part stands out on the phone close-up for all 14 parts (pixels changed by the highlight, strongest change 0-255)', len(seen) == 14 and not weak, seen)
        pg.click('[data-fgo="3"]'); ss = {}
        for _ in range(80):
            if len(ss) == 6: break
            pg.click('#fsQuizGo'); s = pg.evaluate("()=>{const e=document.querySelector('.fst-fig [data-string].hl');return e&&e.dataset.string}")
            if s and s not in ss:
                fig = pg.locator('.fst-fig .fst-zoom').first; a = img(fig.screenshot()); pg.evaluate("()=>document.querySelectorAll('.fst-fig .hl').forEach(e=>e.classList.replace('hl','hl-off'))"); c = img(fig.screenshot())
                d = ImageChops.difference(a, c).convert('L'); ss[s] = (sum(1 for v in d.get_flattened_data() if v > 40), max(d.get_flattened_data()))
                if s in ('1', '6'): a.save(SH / f'lit_string{s}_360_{scheme}.png')
            pg.click('#fsQuizEnd')
        rec(f'7 [{scheme}] each lit string stands out (step 3 check, 360)', len(ss) == 6 and all(v[0] >= 250 and v[1] >= 80 for v in ss.values()), dict(sorted(ss.items())))

    # --- 11 sweep + 10 screenshots: 7 steps, check states, placement, 7 tabs
    sweep = []; worst = {}
    for w, h in [(360, 800), (1280, 900)]:
        for scheme in ['dark', 'light']:
            tag = f'{w}_{scheme}'; pg = open_page(b, width=w, height=h, scheme=scheme, state=ALLFS)
            for n in range(1, 8):
                pg.click(f'[data-fgo="{n}"]'); pg.wait_for_timeout(120); m = pg.evaluate(MEAS); pg.screenshot(path=str(SH / f'step{n}_{tag}.png'), full_page=True)
                sweep.append((f'step {n} {tag}', m['over'], len(pg.errors), m['small'], m['out'], m['minFont'], m['h']))
                if n in (1, 3, 5, 6):
                    pg.click('#fsQuizGo'); pg.wait_for_timeout(80); m = pg.evaluate(MEAS); pg.screenshot(path=str(SH / f'step{n}_check_{tag}.png'), full_page=True)
                    sweep.append((f'step {n} check {tag}', m['over'], len(pg.errors), m['small'], m['out'], m['minFont'], m['h']))
                    if n == 1 and w == 360:
                        fig = pg.evaluate("()=>{const f=document.querySelector('.fst-fig').getBoundingClientRect(),o=document.querySelector('.fst-opts').getBoundingClientRect();return [Math.round(f.top+scrollY),Math.round(o.bottom+scrollY),innerHeight]}")
                        worst[tag] = fig
                    # wrong answer state
                    if pg.query_selector('#fsQuiz [data-fa]'):
                        pg.click('#fsQuiz [data-fa]'); m = pg.evaluate(MEAS); sweep.append((f'step {n} check answered {tag}', m['over'], len(pg.errors), m['small'], m['out'], m['minFont'], m['h']))
                    pg.click('#fsQuizEnd')
                if n == 4:
                    pg.click('#fsEarPlay'); m = pg.evaluate(MEAS); sweep.append((f'step 4 ear {tag}', m['over'], len(pg.errors), m['small'], m['out'], m['minFont'], m['h']))
            fr = open_page(b, width=w, height=h, scheme=scheme); fr.screenshot(path=str(SH / f'fresh_{tag}.png')); fr.click('#fsPlaceGo'); fr.wait_for_timeout(80); m = fr.evaluate(MEAS); fr.screenshot(path=str(SH / f'placement_{tag}.png'), full_page=True)
            sweep.append((f'placement q1 {tag}', m['over'], len(fr.errors), m['small'], m['out'], m['minFont'], m['h']))
            for i in range(8):
                if fr.query_selector('#fsQuiz [data-fa]'): fr.click('#fsQuiz [data-fa]')
                else:
                    pt = fr.evaluate("()=>{const r=document.querySelector('.fst-plates [data-part=\"body\"] .hit').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height*.8]}"); fr.mouse.click(*pt)
                fr.wait_for_timeout(30)
            if fr.query_selector('#fsPlace'):
                m = fr.evaluate(MEAS); fr.screenshot(path=str(SH / f'placement_result_{tag}.png'), full_page=True); sweep.append((f'placement result {tag}', m['over'], len(fr.errors), m['small'], m['out'], m['minFont'], m['h']))
            fr.click('#fsPlaceOpen') if fr.query_selector('#fsPlaceOpen') else None
            fr2 = open_page(b, width=w, height=h, scheme=scheme); fr2.click('a.lk[href="#record"]'); fr2.wait_for_timeout(80); sweep.append((f'record on a first visit {tag}', overflow(fr2), len(fr2.errors), [], [], 0, 0)); fr2.screenshot(path=str(SH / f'record_firstvisit_{tag}.png'), full_page=True)
            rt = open_page(b, width=w, height=h, scheme=scheme, state=RET)
            for t in ['path', 'warm-up', 'rudiments', 'technique', 'invent', 'gig', 'record']:
                rt.evaluate("h=>{location.hash=h}", t); rt.wait_for_timeout(100); sweep.append((f'tab {t} {tag}', overflow(rt), len(rt.errors), [], [], 0, 0))
                if t == 'path': rt.screenshot(path=str(SH / f'path_{tag}.png'))
            for x in (pg, fr, fr2, rt):
                if x.errors: print('ERRORS', tag, x.errors[:3])
    bad = [s for s in sweep if s[1] > 0 or s[2] > 0]
    rec(f'11 sweep: {len(sweep)} screens (7 steps, check and answered states, ear check, placement, Record on a first visit, 7 tabs) x 360/1280 x dark/light: no page overflow, no console errors', not bad, bad or f'{len(sweep)} clean')
    outs = [(s[0], s[4]) for s in sweep if s[4]]
    rec('11 nothing inside First Steps runs past the screen edge', not outs, outs[:6])
    small = {}
    for s in sweep:
        if '360' in s[0]:
            for x in s[3]: small.setdefault(x, []).append(s[0])
    rec('7 phone (360): every button, link, tick and field in First Steps is at least 44 px each way', not small, {k: v[0] for k, v in small.items()})
    small12 = {}
    for s in sweep:
        if '1280' in s[0]:
            for x in s[3]: small12.setdefault(x, []).append(s[0])
    print('NOTE targets under 44 px at 1280:', {k: v[0] for k, v in small12.items()})
    print('NOTE smallest text in First Steps (px):', sorted({s[5] for s in sweep if s[5]})[:3], '| step 1 check at 360: figure top, answers bottom, screen height', worst)
    print('NOTE page heights at 360 dark (px):', {s[0]: s[6] for s in sweep if '360_dark' in s[0] and s[0].startswith('step') and 'check' not in s[0] and 'ear' not in s[0]})
    # visible words: British spelling, no emoji
    pg = open_page(b, state=ALLFS); words = ''
    for n in range(1, 8):
        pg.click(f'[data-fgo="{n}"]'); words += pg.evaluate("()=>document.querySelector('#v-first-steps').innerText") + '\n'
    us = re.findall(r'\b(?:color|center|favorite|practic(?:ing|ed)|memoriz\w+|recogniz\w+|pinky|whole step|half step|quarter note|eighth note|measure[s]?|fretboard hand|tuning peg[s]? clockwise|soundhole)\b', words, flags=re.I)
    emo = re.findall(r'[\U0001F300-\U0001FAFF☀-➿]', words)
    rec('10 words: no American spellings or terms found, no emoji', not us and not emo, {'american': us, 'emoji': emo, 'words checked': len(words.split())})
    b.close()
json.dump(R, open(OUT / 'result_look.json', 'w'), indent=1, default=str)
bad = [r for r in R if not r[1]]; print(f'\n{len(R) - len(bad)}/{len(R)} pass'); [print('FAIL', r[0], str(r[2])[:900]) for r in bad]
