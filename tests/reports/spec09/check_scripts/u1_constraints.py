"""U1 (honest wording where storage is blocked; normal wording identical to 0.8) and the hard constraints:
start-up storage check (byte-identical saved data, nothing left on a first visit, only the key 'shredder'),
0.7 / 0.8 backups and bare state import, version label, colours, dialogs, network.
Real 0.7 and 0.8 backup files are made by running those versions (git show fd059ea:index.html, main:index.html) and pressing Download backup."""
import json, subprocess, tempfile, pathlib, shutil, re, sys
from playwright.sync_api import sync_playwright
from common import *

SEED = {"inst": "bass", "stage": "c-g-f", "finish": "rock", "bpm": 96, "capo": {"a-e": 2}, "lv": {"a-e:0": 3, "a-e:1": 2, "a-e:0@bass": 1},
        "journal": [{"d": 1795000000000, "t": "Colour and rhythm practised", "inst": "guitar"}, {"d": 1795100000000, "t": "Second entry"}],
        "changes": [{"d": 1795000000000, "n": 31, "pair": "A-E"}], "warm": {"2026-11-20": [0, 1]}, "gig": {"open": "g-bamba", "block": 25}}
BAD = re.compile(r"saved in this browser|lives in this browser|this browser", re.I)
out, fails = {}, []
TABS = ["path", "warm-up", "rudiments", "technique", "invent", "gig", "record"]


def check(name, ok, detail=None):
    out[name] = {"ok": bool(ok), "detail": detail}
    if not ok: fails.append(name)


def version_dir(rev):
    tmp = pathlib.Path(tempfile.mkdtemp())
    (tmp / "index.html").write_bytes(subprocess.check_output(["git", "-C", str(ROOT), "show", rev + ":index.html"]))
    shutil.copytree(ROOT / "fonts", tmp / "fonts")
    return tmp


def msg(fr):
    return fr.evaluate("()=>{const e=document.getElementById('bkMsg');return e?e.innerText.trim():null}")


def ask_import(fr, txt):
    fr.fill("#bkIn", txt); fr.click("#bkImport"); fr.wait_for_selector("#bkYes"); return fr.inner_text("#bkAsk")


def backup_from(b, base, tmp, name):
    pg = open_app(b, base, state=SEED, hash_="record", accept_downloads=True)
    label = pg.inner_text("header .sub")
    with pg.expect_download() as d: pg.click("#bkDown")
    f = tmp / name; d.value.save_as(str(f)); pg.context.close()
    return f, label


def same(a, b_):
    return [k for k, v in a.items() if k != "teacher" and json.dumps(b_.get(k), sort_keys=True) != json.dumps(v, sort_keys=True)]


WORDS = """()=>({foot:document.querySelector('p.foot').innerText,footText:document.querySelector('p.foot').textContent,footLinks:[...document.querySelectorAll('p.foot a')].map(a=>a.getAttribute('href')+'|'+a.textContent),
 intro:document.querySelector('#backup p.note').innerText,card:document.getElementById('backup').innerText})"""

with sync_playwright() as p:
    b = p.chromium.launch(); _, base = serve(); d8 = version_dir("main"); _, base8 = serve(d8); d7 = version_dir("fd059ea"); _, base7 = serve(d7)
    tmp = pathlib.Path(tempfile.mkdtemp())
    f07, l07 = backup_from(b, base7, tmp, "b07.json"); f08, l08 = backup_from(b, base8, tmp, "b08.json")
    bk07, bk08 = f07.read_text(), f08.read_text(); o07, o08 = json.loads(bk07), json.loads(bk08)
    out["backup files made"] = {"0.7": [l07, o07["version"], o07["format"]], "0.8": [l08, o08["version"], o08["format"]]}
    check("real 0.7 and 0.8 backup files made by those versions", o07["version"] == "0.7" and o08["version"] == "0.8")

    # ---------- U1 normal page: wording character for character against 0.8
    w = {}
    for nm, bs in (("0.9", base), ("0.8", base8)):
        pg = open_app(b, bs, state=SEED, hash_="record"); r = pg.evaluate(WORDS)
        r["ask"] = ask_import(pg, bk08); pg.click("#bkNo")
        r["ask bare"] = ask_import(pg, json.dumps(o07["state"])); pg.click("#bkYes"); r["after import"] = msg(pg)
        r["footStyle"] = pg.evaluate("()=>{const p=document.querySelector('p.foot'),a=p.querySelector('a'),c=getComputedStyle(a),r=p.getBoundingClientRect();return [c.color,c.textDecorationLine,c.fontSize,getComputedStyle(p).fontSize,Math.round(r.height),Math.round(r.width)]}")
        w[nm] = r; pg.context.close()
    for k in ("foot", "footText", "footLinks", "intro", "card", "ask", "ask bare", "after import", "footStyle"):
        check("U1 normal page: %s identical to 0.8" % k, w["0.9"][k] == w["0.8"][k], {"0.9": w["0.9"][k], "0.8": w["0.8"][k]} if w["0.9"][k] != w["0.8"][k] or k in ("foot", "intro", "ask") else None)
    # first visit (no save at all), still normal wording
    pg = open_app(b, base, hash_="record"); r = pg.evaluate(WORDS); pg8 = open_app(b, base8, hash_="record"); r8 = pg8.evaluate(WORDS)
    check("U1 normal page, first visit: footer and Backup card identical to 0.8", r == r8); pg.context.close(); pg8.context.close()

    # ---------- U1 storage blocked
    def blocked_words(fr, pg, label):
        r = fr.evaluate(WORDS); r["ask"] = ask_import(fr, bk08)
        r["console at this point"] = bad_msgs(pg)
        fr.click("#bkYes"); r["after import"] = msg(fr)
        texts = {}
        for t in TABS:
            fr.click('#tabs a[href="#%s"]' % t); fr.wait_for_selector('#tabs a[href="#%s"][aria-current=page]' % t); texts[t] = fr.inner_text("body")
        r["'this browser' anywhere on any tab"] = sorted(set(m.group(0) + " @" + t for t, x in texts.items() for m in re.finditer(r".{0,50}this browser.{0,40}", x)))
        for k in ("foot", "intro", "ask"):
            check("U1 %s: %s has no 'saved in this browser' / 'lives in this browser'" % (label, k), not BAD.search(r[k]), r[k])
            check("U1 %s: %s mentions a backup" % (label, k) if k != "ask" else "U1 %s: ask says the progress loaded on this page" % label,
                  ("backup" in r[k].lower()) if k != "ask" else "loaded on this page now" in r[k], None)
        check("U1 %s: footer and intro name Download and Copy" % label, all(("Download" in r[k] and "Copy" in r[k]) for k in ("foot", "intro")))
        check("U1 %s: footer still links to the Record tab" % label, r["footLinks"] and r["footLinks"][0].startswith("#record|"), r["footLinks"])
        check("U1 %s: message after import is the 0.8 honest one" % label, "this visit only" in (r["after import"] or ""), r["after import"])
        check("U1 %s: no 'this browser' on any tab" % label, not r["'this browser' anywhere on any tab"], r["'this browser' anywhere on any tab"])
        check("U1 %s: no console errors/warnings, no dialogs" % label, not bad_msgs(pg) and not pg.dialogs, [bad_msgs(pg), pg.dialogs])
        return r
    for sb in ("allow-scripts", "allow-scripts allow-downloads"):
        for width in (1280, 360):
            ctx = b.new_context(viewport={"width": width, "height": 900}); pg = watch(ctx.new_page()); pg.set_default_timeout(10000)
            pg.goto(base + "/__wrap?sb=" + sb.replace(" ", "+") + "&h=record"); fr = pg.wait_for_selector("#f").content_frame(); fr.wait_for_selector("#bkCopy")
            st = fr.evaluate("()=>{try{localStorage.getItem('x');return 'available'}catch(e){return 'blocked: '+e.name}}")
            r = blocked_words(fr, pg, "sandbox(%s) %d" % (sb, width)); r["storage"] = st
            r["overflow"] = fr.evaluate(OVERFLOW); check("U1 sandbox(%s) %d: no page overflow" % (sb, width), r["overflow"][0] <= r["overflow"][1] + 1, r["overflow"])
            out["sandbox(%s) %d wording" % (sb, width)] = r; ctx.close()
    # sandbox with same-origin: storage works, so normal wording
    ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = watch(ctx.new_page()); pg.goto(base + "/__wrap?sb=allow-scripts+allow-same-origin&h=record"); fr = pg.wait_for_selector("#f").content_frame(); fr.wait_for_selector("#bkCopy")
    r = fr.evaluate(WORDS); check("U1 sandbox with allow-same-origin (storage works): normal wording", r["foot"] == w["0.8"]["foot"] and "lives in this browser only" in r["intro"], r["intro"][:60]); ctx.close()
    # top-level page where the browser refuses writes (setItem throws, reads work) and where reading throws too
    for label, init in (("top-level, setItem throws (quota / private mode)", "Storage.prototype.setItem=function(){throw new DOMException('full','QuotaExceededError')}"),
                        ("top-level, localStorage access throws", "Object.defineProperty(window,'localStorage',{get(){throw new DOMException('denied','SecurityError')}})")):
        ctx = b.new_context(viewport={"width": 1280, "height": 900}); ctx.add_init_script(init); pg = watch(ctx.new_page()); pg.set_default_timeout(10000)
        pg.goto(base + "/index.html#record"); pg.wait_for_selector("#bkCopy"); out[label] = blocked_words(pg, pg, label); ctx.close()

    # ---------- start-up storage check
    SPY = """(()=>{window.__ls=[];for(const m of ['setItem','removeItem','clear']){const o=Storage.prototype[m];Storage.prototype[m]=function(...a){window.__ls.push([this===window.sessionStorage?'session':'local',m,...a.map(String)]);return o.apply(this,a)}}})()"""
    raws = {"pretty JSON, odd spacing, unknown key, non-ASCII": '{ "inst":"bass",\n  "zzUnknown":[1,2,{"a":null}],  "journal":[{"d":1795000000000,"t":"café ♯   \\u00e9 <b>&amp;"}], "bpm":96.0 }',
            "0.7-shaped save (compact)": json.dumps(o07["state"], separators=(",", ":")), "0.8-shaped save (spaced)": json.dumps(o08["state"], indent=3),
            "not JSON": "{nonsense", "empty string": "", "empty object": "{}", "the word null": "null", "an array": "[1,2,3]", "wrong types": '{"lv":5,"journal":"x","gig":[]}'}
    sc = {}
    for nm, raw in raws.items():
        ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = watch(ctx.new_page()); pg.set_default_timeout(10000)
        pg.goto(base + "/fonts/"); pg.evaluate("s=>{localStorage.clear();localStorage.setItem('shredder',s)}", raw)
        ctx.add_init_script(SPY)
        pg.goto(base + "/index.html"); pg.wait_for_selector("#tabs a[aria-current=page]", state="attached"); pg.wait_for_timeout(300)
        a1 = pg.evaluate("()=>[localStorage.getItem('shredder'),Object.keys(localStorage),Object.keys(sessionStorage),document.cookie,window.__ls]")
        pg.reload(); pg.wait_for_selector("#tabs a[aria-current=page]", state="attached"); pg.wait_for_timeout(300)
        a2 = pg.evaluate("()=>[localStorage.getItem('shredder'),Object.keys(localStorage),Object.keys(sessionStorage),document.cookie,window.__ls]")
        pg.goto(base + "/index.html#record"); pg.wait_for_selector("#backup"); intro = pg.inner_text("#backup p.note")[:42]
        a3 = pg.evaluate("()=>localStorage.getItem('shredder')")
        ok = a1[0] == raw and a2[0] == raw and a3 == raw and a1[1] == ["shredder"] and a2[1] == ["shredder"] and not a1[2] and not a1[3] and all(c[1] == "setItem" and c[2] == "shredder" and c[3] == raw for c in a1[4])
        sc[nm] = {"identical after load, reload, third load": ok, "bytes": len(raw.encode()), "storage calls on load": [[c[0], c[1], c[2], "(same value)" if len(c) > 3 and c[3] == raw else (c[3:] or "")] for c in a1[4]], "wording": intro, "console": bad_msgs(pg)}
        check("storage check leaves saved data byte-identical: " + nm, ok and not bad_msgs(pg), sc[nm]); ctx.close()
    out["storage check, seeded"] = sc
    # first visit
    ctx = b.new_context(viewport={"width": 1280, "height": 900}); ctx.add_init_script(SPY); pg = watch(ctx.new_page()); pg.set_default_timeout(10000)
    pg.goto(base + "/index.html"); pg.wait_for_selector("#tabs a[aria-current=page]", state="attached"); pg.wait_for_timeout(300)
    fv = pg.evaluate("async()=>({local:Object.keys(localStorage),session:Object.keys(sessionStorage),cookie:document.cookie,calls:window.__ls,idb:indexedDB.databases?(await indexedDB.databases()).map(d=>d.name):'n/a',caches:await caches.keys().catch(()=>[])})")
    check("first visit: nothing left behind after load (no keys, cookies, databases)", not fv["local"] and not fv["session"] and not fv["cookie"] and not fv["idb"] and not fv["caches"], fv)
    for t in TABS:
        pg.click('#tabs a[href="#%s"]' % t); pg.wait_for_selector('#tabs a[href="#%s"][aria-current=page]' % t)
    fv2 = pg.evaluate("()=>[Object.keys(localStorage),localStorage.getItem('shredder')]")
    # the same first visit on 0.8: opening the Gig tab writes the gig plan in both versions, so compare rather than expect nothing
    ctx8 = b.new_context(viewport={"width": 1280, "height": 900}); pg8 = ctx8.new_page(); pg8.goto(base8 + "/index.html"); pg8.wait_for_selector("#tabs a[aria-current=page]", state="attached"); k8 = pg8.evaluate("()=>Object.keys(localStorage)")
    for t in TABS:
        pg8.click('#tabs a[href="#%s"]' % t); pg8.wait_for_selector('#tabs a[href="#%s"][aria-current=page]' % t)
    fv8 = pg8.evaluate("()=>[Object.keys(localStorage),localStorage.getItem('shredder')]"); ctx8.close()
    check("first visit, all seven tabs opened: what is stored is identical to 0.8 (only 'shredder', written when the Gig tab opens)", fv2 == fv8 and fv2[0] in ([], ["shredder"]) and k8 == [], {"keys": fv2[0], "bytes": len(fv2[1] or "")})
    # after real use only 'shredder' exists
    pg.click('#tabs a[href="#path"]'); pg.click('[data-inst="drums"]'); pg.click('#tabs a[href="#gig"]'); pg.click("#present"); pg.wait_for_timeout(100)
    k = pg.evaluate("()=>[Object.keys(localStorage),Object.keys(sessionStorage),document.cookie]"); check("after use: localStorage holds only 'shredder'", k == [["shredder"], [], ""], k); ctx.close()
    # a second tab opening on a first visit must not disturb a tab already open (the check writes then removes)
    ctx = b.new_context(viewport={"width": 1280, "height": 900}); pA = watch(ctx.new_page()); pA.goto(base + "/index.html#record"); pA.wait_for_selector("#backup"); before = pA.inner_text("body")
    pB = watch(ctx.new_page()); pB.goto(base + "/index.html"); pB.wait_for_selector("#tabs a[aria-current=page]", state="attached"); pA.wait_for_timeout(300)
    check("two tabs, first visit: first tab undisturbed, nothing stored", pA.inner_text("body") == before and not bad_msgs(pA) and pA.evaluate("()=>Object.keys(localStorage)") == [], None); ctx.close()

    # ---------- imports: 0.7, 0.8, bare state; paste and file chooser
    imp = {}
    for nm, txt, f, st in (("0.7 backup", bk07, f07, o07["state"]), ("0.8 backup", bk08, f08, o08["state"]), ("bare state", json.dumps(o07["state"]), None, o07["state"])):
        pg = open_app(b, base, hash_="record"); ask = ask_import(pg, txt); pg.click("#bkYes"); m = msg(pg)
        s = pg.evaluate("()=>JSON.parse(localStorage.getItem('shredder'))"); d1 = same(st, s)
        pg.reload(); pg.wait_for_selector("#backup"); d2 = same(st, pg.evaluate("()=>JSON.parse(localStorage.getItem('shredder'))"))
        pg.click('#tabs a[href="#path"]'); shown = pg.inner_text('[data-inst][aria-pressed=true]')
        imp[nm + " (pasted)"] = {"ask": ask, "msg": m, "fields differing": d1, "after reload": d2, "instrument shown": shown, "keys": pg.evaluate("()=>Object.keys(localStorage)")}
        check("import %s, pasted: every field restored and kept after reload" % nm, not d1 and not d2 and "Backup imported" in m and shown == "Bass" and not bad_msgs(pg) and not pg.dialogs, imp[nm + " (pasted)"]); pg.context.close()
        if f:
            pg = open_app(b, base, hash_="record")
            with pg.expect_file_chooser() as fc: pg.click("#bkPick")
            fc.value.set_files(str(f)); pg.wait_for_selector("#bkYes"); pg.click("#bkYes"); m = msg(pg); d1 = same(st, pg.evaluate("()=>JSON.parse(localStorage.getItem('shredder'))"))
            check("import %s, file chooser: every field restored" % nm, not d1 and "Backup imported" in m, [m, d1]); pg.context.close()
    out["imports"] = imp
    # ---------- version label, new backup, newer-version message
    pg = open_app(b, base, state=SEED, hash_="record", accept_downloads=True)
    with pg.expect_download() as d: pg.click("#bkDown")
    f09 = tmp / "b09.json"; d.value.save_as(str(f09)); o09 = json.loads(f09.read_text())
    pg.fill("#bkIn", json.dumps({"app": "The Guitar Lab", "format": 2, "state": o07["state"]})); pg.click("#bkImport"); newer = msg(pg)
    body = "".join(pg.inner_text("body") for _ in [0])
    v = {"title": pg.title(), "header": pg.inner_text("header .sub"), "backup": {k: o09[k] for k in ("app", "format", "version")}, "backup state identical to the 0.8 backup of the same save": o09["state"] == o08["state"], "backup state keys == 0.8 backup's": sorted(o09["state"]) == sorted(o08["state"]), "newer msg": newer, "0.8 visible": bool(re.search(r"\b0\.8\b", body))}
    check("version label 0.9: title, header, backup version, newer-version message; no 0.8 shown", v["title"] == "The Guitar Lab 0.9" and "version 0.9" in v["header"] and v["backup"] == {"app": "The Guitar Lab", "format": 1, "version": "0.9"} and "(0.9)" in newer and not v["0.8 visible"] and v["backup state identical to the 0.8 backup of the same save"] and v["backup state keys == 0.8 backup's"], v)
    # a 0.9 backup goes back into 0.8 (data shape unchanged)
    pg8 = open_app(b, base8, hash_="record"); ask_import(pg8, f09.read_text()); pg8.click("#bkYes"); check("data shape unchanged: a 0.9 backup imports into 0.8", "Backup imported" in msg(pg8) and not same(o09["state"], pg8.evaluate("()=>JSON.parse(localStorage.getItem('shredder'))")), msg(pg8)); pg8.context.close()
    check("normal page: no dialogs, no console errors, no off-host requests", not pg.dialogs and not bad_msgs(pg) and not off_host(pg, base), [pg.dialogs, bad_msgs(pg), off_host(pg, base)])
    out["requests made by the page"] = sorted(set(u.replace(base, "") for u in pg.reqs if not u.startswith("blob:"))); pg.context.close()

    # ---------- colours: lit keys and dominant, both themes, against 0.8
    col = {}
    for scheme in ("dark", "light"):
        for nm, bs in (("0.9", base), ("0.8", base8)):
            pg = open_app(b, bs, scheme=scheme, state={"inst": "keys"}, hash_="path")
            col[scheme + " " + nm] = pg.evaluate("""()=>{const cs=getComputedStyle(document.documentElement),v=n=>cs.getPropertyValue(n).trim();const probe=c=>{const e=document.createElement('i');e.style.color=c;document.body.appendChild(e);const r=getComputedStyle(e).color;e.remove();return r};
              const on=[...document.querySelectorAll('rect.k-on')].map(r=>getComputedStyle(r).fill);const vars={};for(const n of ['--kbl','--dom','--hi','--ton','--pre','--sec','--sub','--bg','--card','--ink','--mut','--rule','--wood','--fret','--ivory','--inlay','--fin'])vars[n]=probe('var('+n+')');
              return {litFills:[...new Set(on)].sort(),litCount:on.length,vars}}""")
            col[scheme + " " + nm]["litFills"] = [rgb2hex(x) for x in col[scheme + " " + nm]["litFills"]]; col[scheme + " " + nm]["vars"] = {k: rgb2hex(x) for k, x in col[scheme + " " + nm]["vars"].items()}
            pg.context.close()
        a, c = col[scheme + " 0.9"], col[scheme + " 0.8"]
        check("colours %s: lit keys are #7a5c12 (white) and #a47510 (black), same as 0.8" % scheme, a == c and set(a["litFills"]) == {"#7a5c12", "#a47510"} and a["vars"]["--kbl"] == "#a47510", a["litFills"])
        check("colours %s: dominant is %s, every colour variable same as 0.8" % (scheme, "#d0574b" if scheme == "dark" else "#a8352b"), a["vars"]["--dom"] == ("#d0574b" if scheme == "dark" else "#a8352b") and a["vars"] == c["vars"], a["vars"]["--dom"])
    out["colours"] = col
    b.close()

# ---------- source-level checks
src = (ROOT / "index.html").read_text(); old = (d8 / "index.html").read_text()
g = {"alert/confirm/prompt calls": re.findall(r"(?<![\w.$])(?:window\.)?(?:alert|confirm|prompt)\s*\(", src), "fetch/XHR/WebSocket/sendBeacon/EventSource/import()": re.findall(r"\bfetch\s*\(|XMLHttpRequest|WebSocket|sendBeacon|EventSource|\bimport\s*\(\s*['\"`]", src),
     "http(s) URLs": sorted(set(re.findall(r"https?://[^\s'\"`)<]+", src))), "src=/url() targets": sorted(set(re.findall(r"(?:src=|url\()['\"]?([^'\")\s>]+)", src))),
     "localStorage uses": re.findall(r"localStorage\.\w+\([^)]*\)", src), "sessionStorage/indexedDB/cookie": re.findall(r"sessionStorage|indexedDB|document\.cookie", src),
     "colour counts 0.9 vs 0.8": {c: [src.count(c), old.count(c)] for c in ("#a47510", "#7a5c12", "#d0574b", "#a8352b")}, "'0.8' left in source": [src[max(0, m.start() - 60):m.end() + 30] for m in re.finditer(r"0\.8", src)]}
out["source"] = g
check("source: no alert/confirm/prompt", not g["alert/confirm/prompt calls"]); check("source: no network APIs; only URL is the song-search link", not g["fetch/XHR/WebSocket/sendBeacon/EventSource/import()"] and g["http(s) URLs"] == ["https://www.youtube.com/results?search_query="], g["http(s) URLs"])
check("source: every localStorage call names 'shredder'", all("'shredder'" in x for x in g["localStorage uses"]) and not g["sessionStorage/indexedDB/cookie"], g["localStorage uses"])
check("source: colour strings appear as often as in 0.8", all(a == c for a, c in g["colour counts 0.9 vs 0.8"].values()), g["colour counts 0.9 vs 0.8"])
json.dump(out, open(RES / "u1_constraints.json", "w"), indent=1, ensure_ascii=False, default=str)
print(json.dumps(out, indent=1, ensure_ascii=False, default=str))
print("\nCHECKS", sum(1 for v in out.values() if isinstance(v, dict) and "ok" in v), "FAILS", len(fails))
for f in fails: print("FAIL", f, json.dumps(out[f]["detail"], ensure_ascii=False, default=str)[:700])
