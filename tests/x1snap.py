"""R13 X1: what guitar (and, until their batches ship, drums, keys and vocals) rendered on 0.9.

`capture(page)` walks one instrument through Rudiments, Technique, Invent (before a roll and
after a roll with Math.random pinned) and the side panel and stage-2 song TAB of all eight
stages, and returns {name: innerHTML}. `x1_0_9.json` holds the sha256 and length of each,
taken from 0.9 (main 90719f9). To re-make it from an older build:

    mkdir -p /tmp/gl09 && git show main:index.html > /tmp/gl09/index.html && ln -sfn "$PWD/fonts" /tmp/gl09/fonts
    SHREDDER_INDEX=/tmp/gl09/index.html python3 tests/x1snap.py

To see a difference, run the same command with `--dump DIR` on both builds and diff the folders.
"""
import hashlib
import json
import pathlib
import sys

FILE = pathlib.Path(__file__).resolve().parent / "x1_0_9.json"
STAGES = ["a-e", "twelve-bar", "am-e7", "c-g-f", "four-chords", "six-eight", "hallelujah", "beyond"]
TS = 1764200000000


def states(inst):
    """Two saves per instrument: a first visit, and every gate passed with some levels and tempos logged."""
    sfx = "" if inst == "guitar" else "@" + inst
    lv = {f"{s}{sfx}:{i}": 2 for s in STAGES for i in range(5)}
    lv.update({"r:pulse" + sfx: 2, "r:spider" + sfx: 1, "t:power" + sfx: 3, "t:maj7" + sfx: 2})
    rich = {"inst": inst, "lv": lv, "best": {"r:pulse" + sfx: 96}, "finish": "rock", "bpm": 84,
            "gates": {s + sfx: TS for s in STAGES},
            "changes": [{"d": TS, "st": "a-e", "pair": "A-E", "n": 33, "inst": inst}]}
    return {"new": {"inst": inst}, "rich": rich}


PIN_RANDOM = "()=>{let x=7;Math.random=()=>{x=(x*16807)%2147483647;return (x-1)/2147483646}}"
HTML = "s=>{const e=document.querySelector(s);return e?e.innerHTML:null}"


def capture(pg, go):
    out = {}
    for s in STAGES:
        go(pg, s)
        out["side/" + s] = pg.evaluate(HTML, "#side")
        out["songtab/" + s] = pg.evaluate("()=>[...document.querySelectorAll('#stage .tab')].map(e=>e.outerHTML).join('')")
    go(pg, "twelve-bar")
    for tab in ["rudiments", "technique", "invent"]:
        go(pg, tab)
        out[tab] = pg.evaluate(HTML, "#v-" + tab)
    pg.evaluate(PIN_RANDOM)
    pg.click("#roll")
    out["invent/rolled"] = pg.evaluate(HTML, "#v-invent")
    go(pg, "four-chords")
    go(pg, "invent")
    pg.evaluate(PIN_RANDOM)
    pg.click("#roll")
    out["invent/rolled-c"] = pg.evaluate(HTML, "#v-invent")
    return out


def digest(html):
    return [hashlib.sha256((html or "").encode("utf-8")).hexdigest()[:20], len(html or "")]


def capture_all(browser, insts, dump=None):
    import uihelp
    res = {}
    for inst in insts:
        for name, st in states(inst).items():
            pg = uihelp.open_app(browser, state=st)
            for k, v in capture(pg, uihelp.go).items():
                res[f"{inst}/{name}/{k}"] = digest(v)
                if dump:
                    p = pathlib.Path(dump) / f"{inst}.{name}.{k.replace('/', '.')}.html"
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text((v or "").replace("><", ">\n<"), encoding="utf-8")
            assert not pg.errors, pg.errors
            uihelp.close(pg)
    return res


if __name__ == "__main__":
    sys.path.insert(0, str(FILE.parent))
    import uihelp
    from playwright.sync_api import sync_playwright
    dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
    with sync_playwright() as p:
        b = p.chromium.launch(args=uihelp.LAUNCH_ARGS)
        res = capture_all(b, ["guitar", "bass", "drums", "keys", "vocals"], dump)
        b.close()
    if dump:
        print("dumped", len(res), "panels to", dump)
    else:
        FILE.write_text(json.dumps(res, indent=0, sort_keys=True) + "\n", encoding="utf-8")
        print("wrote", FILE, len(res))
