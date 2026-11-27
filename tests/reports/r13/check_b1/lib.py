"""Independent check B1: shared helpers (written by the checker, not the builder)."""
import json, pathlib
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parents[4]
NEW = (ROOT / "index.html").as_uri()
OLD = pathlib.Path("/tmp/v09.html").as_uri()
IDS = ['a-e','twelve-bar','am-e7','c-g-f','four-chords','six-eight','hallelujah','beyond']
INST = ['guitar','bass','drums','keys','vocals']
VIEWS = ['path','warm-up','rudiments','technique','invent','gig','record']
# deterministic Math.random + frozen clock-free; records dialogs
INIT = r"""(()=>{let s=12345;Math.random=()=>{s=(s*1103515245+12345)%2147483648;return s/2147483648};
window.__dlg=[];for(const k of ['alert','confirm','prompt']){window[k]=function(){window.__dlg.push(k);return null}}})();"""
AUD = r"""(()=>{const A=window.__aud={starts:[]};for(const C of [OscillatorNode,AudioBufferSourceNode]){const st=C.prototype.start;
C.prototype.start=function(w,...r){A.starts.push({osc:this instanceof OscillatorNode,when:w||0,freq:this.frequency?this.frequency.value:null,type:this.type||null});return st.call(this,w,...r)}}})();"""

def open_page(browser, url=NEW, width=1280, height=900, scheme="dark", state=None, hash_="", audio=False, raw=None):
    ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=scheme)
    ctx.add_init_script(INIT)
    if audio: ctx.add_init_script(AUD)
    pg = ctx.new_page()
    pg.msgs = []; pg.reqs = []
    pg.on("console", lambda m: pg.msgs.append(m.type + ": " + m.text) if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: pg.msgs.append("pageerror: " + str(e)))
    pg.on("request", lambda r: pg.reqs.append(r.url))
    if state is not None or raw is not None:
        pg.goto(url + "#__seed")
        pg.evaluate("s=>{localStorage.clear();localStorage.setItem('shredder',s)}", raw if raw is not None else json.dumps(state))
        pg.goto("about:blank")
    pg.goto(url + (("#" + hash_) if hash_ else ""))
    pg.wait_for_selector("#tabs a[aria-current=page]", state="attached")
    return pg

def go(pg, h):
    pg.evaluate("""h=>new Promise(r=>{if(location.hash==='#'+h){r();return}
      window.addEventListener('hashchange',()=>setTimeout(r,0),{once:true});location.hash=h})""", h)

def store(pg): return pg.evaluate("()=>JSON.parse(localStorage.getItem('shredder')||'{}')")

def passed_state(inst, n=8, **extra):
    """State with the first n stages passed (all five steps at Consistent) on inst."""
    lv = {}
    for sid in IDS[:n]:
        for i in range(5):
            lv[(sid if inst == 'guitar' else sid + '@' + inst) + ':' + str(i)] = 2
    d = {"inst": inst, "lv": lv}; d.update(extra); return d
