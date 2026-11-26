"""T3 + T5 + backup constraints. Sandboxed iframe (opaque origin: no storage, clipboard blocked by permissions policy) and the normal page.
A real 0.7 backup file is made by running main's index.html (git show main:index.html) and pressing Download backup."""
import json, subprocess, tempfile, pathlib, shutil, sys
from playwright.sync_api import sync_playwright
from common import *
import common

SEED = {"inst": "bass", "stage": "c-g-f", "finish": "rock", "bpm": 96, "capo": {"a-e": 2}, "lv": {"a-e:0": 3, "a-e:1": 2, "a-e:0@bass": 1},
        "journal": [{"d": 1795000000000, "t": "Colour and rhythm practised", "inst": "guitar"}, {"d": 1795100000000, "t": "Second entry"}],
        "changes": [{"d": 1795000000000, "n": 31, "pair": "A-E"}], "warm": {"2026-11-20": [0, 1]}, "gig": {"open": "g-bamba", "block": 25}}
out = {}


def msg(fr):
    return fr.evaluate("()=>{const e=document.getElementById('bkMsg');return e?e.innerText.trim():null}")


def do_import(fr, txt):
    fr.fill("#bkIn", txt); fr.click("#bkImport"); fr.wait_for_selector("#bkYes"); ask = fr.inner_text("#bkAsk"); fr.click("#bkYes"); return ask, msg(fr)


with sync_playwright() as p:
    b = p.chromium.launch(); srv, base = serve()
    # --- make a genuine 0.7 backup file from main
    tmp = pathlib.Path(tempfile.mkdtemp()); (tmp / "index.html").write_bytes(subprocess.check_output(["git", "-C", str(ROOT), "show", "main:index.html"])); shutil.copytree(ROOT / "fonts", tmp / "fonts")
    real_root = common.ROOT; common.ROOT = tmp; srv7, base7 = serve(); common.ROOT = real_root
    import functools, socketserver, threading
    srv7.shutdown(); srv7 = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(H, directory=str(tmp))); threading.Thread(target=srv7.serve_forever, daemon=True).start(); base7 = "http://127.0.0.1:%d" % srv7.server_address[1]
    pg = open_app(b, base7, state=SEED, hash_="record", accept_downloads=True)
    out["0.7 app label"] = pg.inner_text("header .sub")
    with pg.expect_download() as d: pg.click("#bkDown")
    f07 = tmp / "backup07.json"; d.value.save_as(str(f07)); bk07 = f07.read_text(); o07 = json.loads(bk07)
    out["0.7 backup"] = {"file": d.value.suggested_filename, "version": o07.get("version"), "format": o07.get("format"), "keys": sorted(o07["state"].keys())}
    st07 = o07["state"]; pg.context.close()

    # --- normal page, 0.8
    pg = open_app(b, base, hash_="record", accept_downloads=True, permissions=["clipboard-read", "clipboard-write"])
    n = {}
    n["title"] = pg.title(); n["header"] = pg.inner_text("header .sub"); n["0.7 strings visible"] = "0.7" in pg.inner_text("body")
    n["import 0.7 file (pasted): ask"], n["import 0.7 file (pasted): msg"] = do_import(pg, bk07)
    s = pg.evaluate("()=>JSON.parse(localStorage.getItem('shredder'))")
    n["keys in localStorage"] = pg.evaluate("()=>Object.keys(localStorage)")
    def same(a, b_):  # compare everything the 0.7 state carried
        diff = []
        for k, v in a.items():
            if k == "teacher": continue
            if json.dumps(b_.get(k), sort_keys=True) != json.dumps(v, sort_keys=True): diff.append(k)
        return diff
    n["0.7 file: state fields that differ after import"] = same(st07, s)
    # via the file chooser
    pg.evaluate("()=>{localStorage.clear()}"); pg.reload(); pg.wait_for_selector("#bkPick")
    with pg.expect_file_chooser() as fc: pg.click("#bkPick")
    fc.value.set_files(str(f07)); pg.wait_for_selector("#bkYes"); pg.click("#bkYes"); n["import 0.7 file (chooser): msg"] = msg(pg)
    n["0.7 file via chooser: differ"] = same(st07, pg.evaluate("()=>JSON.parse(localStorage.getItem('shredder'))"))
    # bare state
    pg.evaluate("()=>{localStorage.clear()}"); pg.reload(); pg.wait_for_selector("#bkPick")
    n["import bare state: ask"], n["import bare state: msg"] = do_import(pg, json.dumps(st07))
    n["bare state: differ"] = same(st07, pg.evaluate("()=>JSON.parse(localStorage.getItem('shredder'))"))
    pg.reload(); pg.wait_for_selector("#bkPick"); n["after reload still there"] = same(st07, pg.evaluate("()=>JSON.parse(localStorage.getItem('shredder'))")) == []
    # bad input stays in-page
    pg.fill("#bkIn", "{nonsense"); pg.click("#bkImport"); n["bad import msg"] = msg(pg)
    pg.fill("#bkIn", json.dumps({"app": "The Guitar Lab", "format": 2, "state": st07})); pg.click("#bkImport"); n["newer-format msg"] = msg(pg)
    # download
    with pg.expect_download() as d: pg.click("#bkDown")
    f08 = tmp / "backup08.json"; d.value.save_as(str(f08)); o08 = json.loads(f08.read_text())
    n["download msg"] = msg(pg); n["0.8 backup"] = {"file": d.value.suggested_filename, "app": o08["app"], "format": o08["format"], "version": o08["version"], "state==0.7 state": same(st07, o08["state"]) == []}
    pg.click("#bkCopy"); pg.wait_for_function("document.getElementById('bkMsg').innerText.includes('copied')"); n["copy msg (clipboard allowed)"] = msg(pg)
    n["clipboard == backup"] = json.loads(pg.evaluate("()=>navigator.clipboard.readText()"))["state"] == o08["state"]; n["fallback box hidden when clipboard works"] = pg.evaluate("()=>document.getElementById('bkOut').classList.contains('hide')")
    n["console"] = pg.msgs; n["dialogs"] = pg.dialogs; n["requests off-host"] = [u for u in pg.reqs if not u.startswith(base)]; n["requests"] = sorted(set(u.replace(base, "") for u in pg.reqs if not u.startswith("blob:")))
    out["normal page"] = n; pg.context.close()

    # --- normal page, clipboard permission denied (top level, no policy block): fallback path
    ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = watch(ctx.new_page()); pg.goto(base + "/index.html#record"); pg.wait_for_selector("#bkCopy")
    pg.evaluate("()=>{navigator.clipboard.writeText=()=>Promise.reject(new DOMException('no','NotAllowedError'))}")
    pg.click("#bkCopy"); pg.wait_for_function("!document.getElementById('bkOut').classList.contains('hide')")
    out["top-level, writeText rejects"] = {"msg": msg(pg), "fallback visible": pg.is_visible("#bkOut"), "console": pg.msgs}; ctx.close()

    # --- sandboxed frames
    for sb in ("allow-scripts", "allow-scripts allow-downloads", "allow-scripts allow-same-origin"):
        for scheme in ("dark",):
            ctx = b.new_context(viewport={"width": 1280, "height": 900}, color_scheme=scheme, accept_downloads=True, permissions=["clipboard-read"]); pg = watch(ctx.new_page())
            pg.goto(base + "/__wrap?sb=" + sb.replace(" ", "+") + "&h=record"); fr = pg.frames[1] if len(pg.frames) > 1 else None
            fr = pg.frame_locator("#f"); el = pg.wait_for_selector("#f").content_frame(); el.wait_for_selector("#bkCopy")
            r = {}
            r["storage"] = el.evaluate("()=>{try{localStorage.setItem('x','1');localStorage.removeItem('x');return 'available'}catch(e){return 'blocked: '+e.name}}")
            r["clipboard-write allowed by policy"] = el.evaluate("()=>{const fp=document.permissionsPolicy||document.featurePolicy;return fp?fp.allowsFeature('clipboard-write'):'no policy api'}")
            r["origin"] = el.evaluate("()=>location.origin+' / '+self.origin")
            r["console after load"] = list(pg.msgs); pg.msgs.clear()
            r["import ask"], r["import msg"] = do_import(el, bk07)
            el.click('#tabs a[href="#path"]'); el.wait_for_selector('[data-inst][aria-pressed=true]'); r["imported state on Path"] = el.inner_text('[data-inst][aria-pressed=true]') + " / " + el.inner_text("#stage h2"); el.click('#tabs a[href="#record"]'); el.wait_for_selector("#bkDown")
            r["console after import"] = list(pg.msgs); pg.msgs.clear()
            dl = []; pg.on("download", lambda d_: dl.append(d_.suggested_filename))
            el.click("#bkDown"); pg.wait_for_timeout(800)
            r["download msg"] = msg(el); r["download events"] = list(dl); r["console after download"] = list(pg.msgs); pg.msgs.clear()
            el.click("#bkCopy"); pg.wait_for_timeout(500)
            r["copy msg"] = msg(el); r["fallback visible"] = el.is_visible("#bkOut")
            r["fallback text is the backup"] = el.evaluate("()=>{try{const o=JSON.parse(document.getElementById('bkOut').value);return o.version+' / '+o.app}catch(e){return 'no: '+e}}") if r["fallback visible"] else None
            r["fallback selected"] = el.evaluate("()=>{const t=document.getElementById('bkOut');return document.activeElement===t&&t.selectionEnd-t.selectionStart===t.value.length}") if r["fallback visible"] else None
            r["console after copy"] = list(pg.msgs); r["dialogs"] = pg.dialogs
            # did the copy really land? read the system clipboard from the top page
            try:
                pg.bring_to_front(); clip = pg.evaluate("()=>navigator.clipboard.readText()"); r["clipboard really holds the backup"] = '"app": "The Guitar Lab"' in clip
            except Exception as e:
                r["clipboard really holds the backup"] = "could not read: " + str(e)[:80]
            # second press, and a press with the textarea already open
            pg.msgs.clear(); el.click("#bkCopy"); pg.wait_for_timeout(300); r["console after 2nd copy"] = list(pg.msgs)
            # positive control: prove this harness would see the browser's message if the app had asked the clipboard directly
            pg.msgs.clear(); el.click("#bkCopy"); el.evaluate("()=>navigator.clipboard.writeText('x').catch(()=>{})"); pg.wait_for_timeout(300); r["control: direct writeText logs"] = list(pg.msgs)
            out["sandbox=" + sb] = r; ctx.close()
    b.close()
print(json.dumps(out, indent=1, ensure_ascii=False))
