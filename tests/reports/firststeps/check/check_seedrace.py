"""Independent check, item 12: is the intermittent failure a lost seed? Seeds a save the way tests/uihelp.py open_app does (seed page -> about:blank -> app)
and two other ways, N times each under CPU load, and counts how often the app comes up as a first visit instead."""
import sys, json, subprocess, time
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from common import *
from playwright.sync_api import sync_playwright
N = int(sys.argv[1]) if len(sys.argv) > 1 else 120
LOAD = int(sys.argv[2]) if len(sys.argv) > 2 else 6
SEED = json.dumps({'fs': {'done': [1, 2, 3, 4, 5, 6, 7], 'complete': True, 'placed': False}})
burn = [subprocess.Popen([sys.executable, '-c', 'while True: pass']) for _ in range(LOAD)]
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS); out = {}
        for how in ['blank-hop (as uihelp.open_app)', 'direct goto, no about:blank', 'init script on the same load']:
            lost = 0; t0 = time.time()
            for i in range(N):
                ctx = b.new_context(viewport={'width': 1280, 'height': 900}); pg = ctx.new_page()
                if how.startswith('init'):
                    ctx.add_init_script("if(location.protocol==='file:'&&!sessionStorage.getItem('__s')){sessionStorage.setItem('__s','1');localStorage.setItem('shredder'," + json.dumps(SEED) + ")}")
                else:
                    pg.goto(URL + '#__seed'); pg.evaluate("s=>{localStorage.clear();localStorage.setItem('shredder',s)}", SEED)
                    if how.startswith('blank'): pg.goto('about:blank')
                pg.goto(URL); pg.wait_for_selector('#tabs a[aria-current=page]', state='attached')
                v = pg.evaluate("()=>[...document.querySelectorAll('[id^=\"v-\"]')].filter(e=>!e.classList.contains('hide')).map(e=>e.id).join()")
                if v != 'v-path': lost += 1
                ctx.close()
            out[how] = [lost, N, round(time.time() - t0, 1)]; print(how, '-> seed lost', lost, 'of', N, flush=True)
        b.close()
    json.dump({'load_processes': LOAD, 'results': out}, open(OUT / ('result_seedrace_%s.json' % (sys.argv[3] if len(sys.argv) > 3 else 'load%d' % LOAD)), 'w'), indent=1)
finally:
    for x in burn: x.kill()
