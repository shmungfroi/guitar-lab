"""Read the app's data tables and helper functions out of index.html.

The app keeps everything inside one block-scoped <script>, so nothing is on
window. We copy index.html to a temp folder (with a link to fonts/), add one
line at the end of that script, `globalThis.__APP=n=>eval(n)`, which lets a
direct eval see the block's own bindings, load the copy in headless Chromium
and read whatever we need as JSON. This survives refactors of the app's code
as long as the names we ask for still exist. index.html itself is never edited.
"""
import json
import pathlib
import re
import os
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Point SHREDDER_INDEX at another copy (e.g. an older build) to test that instead.
INDEX = pathlib.Path(os.environ.get("SHREDDER_INDEX") or ROOT / "index.html").resolve()

NAMES = ["CH", "FB", "SOLFA", "KEYS", "FN", "PAT", "FIN", "ST", "FORM", "TON", "PCN",
         "OPEN", "TB", "GIG", "INST", "RUD", "TECH", "KNOW"]

COLLECT = r"""
()=>{const g=n=>{try{return __APP(n)}catch(e){return undefined}};const out={};
 for(const n of %(names)s)out[n]=g(n);
 const CH=out.CH,ST=out.ST,S=g('S');
 const f=n=>{const v=g(n);return typeof v==='function'?v:null};
 const bassPos=f('bassPos'),pcsOf=f('pcsOf'),rootOf=f('rootOf'),spell=f('spell'),sounds=f('sounds');
 out.bass={};out.pcs={};out.root={};out.spellOf={};
 for(const n in CH){try{let b=null;try{b=bassPos(n)}catch(e){}
   if(!b||!b.r||!Number.isFinite(b.r[1]))b=bassPos(rootOf(n));out.bass[n]=b}catch(e){out.bass[n]=String(e)}
  out.pcs[n]=pcsOf(n);out.root[n]=rootOf(n);out.spellOf[n]=spell(n)}
 out.sounds={};const saved=JSON.stringify(S.capo);
 for(const s of ST)for(let c=0;c<=7;c++){S.capo={};if(c)S.capo[s.id]=c;try{out.sounds[s.id+':'+c]=sounds(s)}catch(e){out.sounds[s.id+':'+c]=String(e)}}
 S.capo=JSON.parse(saved);return JSON.parse(JSON.stringify(out))}
"""


def hooked_html():
    html = INDEX.read_text(encoding="utf-8")
    blocks = [m for m in re.finditer(r"<script>(.*?)</script>", html, re.S)]
    assert blocks, "no main <script> in index.html"
    m = max(blocks, key=lambda m: len(m.group(1)))
    body = m.group(1)
    cut = body.rstrip().rfind("}")
    if body.lstrip().startswith("{") and cut > 0:
        body = body[:cut] + ";globalThis.__APP=n=>eval(n);\n" + body[cut:]
    else:
        body = body + "\n;globalThis.__APP=n=>eval(n);\n"
    return html[:m.start(1)] + body + html[m.end(1):]


_cache = None


def load():
    global _cache
    if _cache is not None:
        return _cache
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory() as td:
        tdp = pathlib.Path(td)
        (tdp / "index.html").write_text(hooked_html(), encoding="utf-8")
        (tdp / "fonts").symlink_to(INDEX.parent / "fonts" if (INDEX.parent / "fonts").exists() else ROOT / "fonts")
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto((tdp / "index.html").as_uri())
            pg.wait_for_function("()=>typeof globalThis.__APP==='function'", timeout=10000)
            _cache = pg.evaluate(COLLECT % {"names": json.dumps(NAMES)})
            b.close()
    return _cache


if __name__ == "__main__":
    d = load()
    print(sorted(k for k, v in d.items() if v is not None))
    print(d["bass"]["A"], d["sounds"]["a-e:1"])
