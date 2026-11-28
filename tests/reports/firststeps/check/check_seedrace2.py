"""Item 12, cause: when a seed is lost, who lost it? Logs every localStorage call the page makes (with the time and whether it was the app or the test),
and also runs the same seeding against a bare page with no app in it."""
import sys, json, pathlib, time
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from common import *
from playwright.sync_api import sync_playwright
N = int(sys.argv[1]); tag = sys.argv[2]
SEED = json.dumps({'fs': {'done': [1, 2, 3, 4, 5, 6, 7], 'complete': True, 'placed': False}})
LOG = r"""(()=>{const L=[];window.__ls=L;const t0=performance.now();for(const k of ['setItem','removeItem','clear','getItem']){const f=Storage.prototype[k];Storage.prototype[k]=function(...a){const r=f.apply(this,a);
 L.push([Math.round(performance.now()-t0),k,String(a[1]||'').slice(0,30),k==='getItem'?String(r).slice(0,30):'',document.readyState,(new Error().stack||'').includes('index.html')?'app':'test']);return r}}})()"""
bare = pathlib.Path('/tmp/bare'); bare.mkdir(exist_ok=True); (bare / 'index.html').write_text('<!doctype html><title>bare</title><p id=x>bare</p>')
BARE = (bare / 'index.html').as_uri()
res = {'app': [0, N], 'bare page': [0, N], 'cases': []}
with sync_playwright() as p:
    b = p.chromium.launch(args=ARGS)
    for i in range(N):
        ctx = b.new_context(); ctx.add_init_script(LOG); pg = ctx.new_page()
        pg.goto(URL + '#__seed'); log1 = None
        pg.evaluate("s=>{localStorage.clear();localStorage.setItem('shredder',s)}", SEED); log1 = pg.evaluate("()=>window.__ls")
        pg.goto('about:blank'); pg.goto(URL); pg.wait_for_selector('#tabs a[aria-current=page]', state='attached')
        v = pg.evaluate("()=>[...document.querySelectorAll('[id^=\"v-\"]')].filter(e=>!e.classList.contains('hide')).map(e=>e.id).join()")
        if v != 'v-path':
            res['app'][0] += 1; res['cases'].append({'i': i, 'view': v, 'seed page calls': log1, 'second page calls': pg.evaluate("()=>window.__ls"), 'value now': pg.evaluate("()=>String(localStorage.getItem('shredder')).slice(0,40)")})
        ctx.close()
        ctx = b.new_context(); pg = ctx.new_page(); pg.goto(BARE + '#__seed'); pg.evaluate("s=>{localStorage.clear();localStorage.setItem('shredder',s)}", SEED); pg.goto('about:blank'); pg.goto(BARE)
        if pg.evaluate("()=>localStorage.getItem('shredder')") != SEED: res['bare page'][0] += 1
        ctx.close()
    b.close()
json.dump(res, open(OUT / f'result_seedrace2_{tag}.json', 'w'), indent=1); print(tag, res['app'], res['bare page'])
