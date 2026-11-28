"""Independent check helpers (not the builder's). Opens index.html the same way tests/uihelp.py does, with its own audio recorder."""
import json, pathlib, os
ROOT = pathlib.Path(__file__).resolve().parents[4]
URL = pathlib.Path(os.environ.get("GL_INDEX") or ROOT / "index.html").resolve().as_uri()
OUT = pathlib.Path(__file__).resolve().parent
REC = r"""
(()=>{window.__dlg=[];for(const k of ['alert','confirm','prompt']){window[k]=(...a)=>{window.__dlg.push(k);return k==='confirm'}}
window.__osc=[];window.__buf=[];
const st=OscillatorNode.prototype.start;OscillatorNode.prototype.start=function(w){window.__osc.push({f:this.frequency.value,type:this.type,when:w||0,now:this.context.currentTime});return st.apply(this,arguments)};
const bs=AudioBufferSourceNode.prototype.start;AudioBufferSourceNode.prototype.start=function(w){window.__buf.push({when:w||0,now:this.context.currentTime,dur:this.buffer?this.buffer.duration:0});return bs.apply(this,arguments)};
})();
"""
ARGS = ["--autoplay-policy=no-user-gesture-required"]

def open_page(browser, width=1280, height=900, scheme="dark", state=None, hash_="", raw=None):
    ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=scheme, accept_downloads=True)
    ctx.add_init_script(REC)
    page = ctx.new_page()
    page.errors = []; page.reqs = []
    page.on("console", lambda m: page.errors.append("console: " + m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: page.errors.append("pageerror: " + str(e)))
    page.on("request", lambda r: page.reqs.append(r.url))
    if state is not None or raw is not None:
        page.goto(URL + "#__seed")
        page.evaluate("s=>{localStorage.clear();localStorage.setItem('shredder',s)}", raw if raw is not None else json.dumps(state))
        page.goto("about:blank")
    page.goto(URL + (("#" + hash_) if hash_ else ""))
    page.set_default_timeout(8000)
    page.wait_for_selector("#tabs a[aria-current=page]", state="attached")
    return page

def st(page):
    return page.evaluate("()=>JSON.parse(localStorage.getItem('shredder')||'null')")

def tabs(page):
    return page.evaluate("()=>[...document.querySelectorAll('#tabs a')].filter(a=>a.offsetParent!==null&&getComputedStyle(a).display!=='none').map(a=>a.textContent.trim())")

def overflow(page):
    return page.evaluate("()=>document.documentElement.scrollWidth-document.documentElement.clientWidth")
