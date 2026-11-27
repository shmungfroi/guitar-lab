"""Extras: instrument switch, best tempo + Record on bass, save shape, comparison sanity."""
import json
from lib import *
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = open_page(b, state=passed_state('bass', gates={s + '@bass': 1 for s in IDS}), hash_='invent')
    pg.click('#roll'); bassv = pg.locator('[data-bcell]').count()
    go(pg, 'a-e'); pg.click('[data-inst="guitar"]'); go(pg, 'invent')
    g = pg.evaluate("()=>({cells:document.querySelectorAll('[data-bcell]').length,boxes:document.querySelectorAll('#v-invent .cb').length,keep:!!document.getElementById('keepLoop'),h:[...document.querySelectorAll('#v-rudiments .card h3')].length})")
    pg.click('#roll'); g2 = pg.evaluate("()=>({boxes:document.querySelectorAll('#v-invent .cb').length,chg:document.getElementById('chg').textContent})")
    go(pg, 'a-e'); pg.click('[data-inst="bass"]'); go(pg, 'invent'); b2 = pg.evaluate("()=>({cells:document.querySelectorAll('[data-bcell]').length,keep:!!document.getElementById('keepLoop')})")
    print("switch: bass cells", bassv, "-> guitar", g, "after roll", g2, "-> back to bass", b2)
    go(pg, 'rudiments'); before = store(pg)
    pg.fill('[data-best="r:bs-pulse@bass"]', '96'); pg.dispatch_event('[data-best="r:bs-pulse@bass"]', 'change')
    for _ in range(2): pg.click('[data-lv="r:bs-pulse@bass"][data-dir="1"]')
    go(pg, 'technique'); 
    for _ in range(2): pg.click('[data-lv="t:bs-roots@bass"][data-dir="1"]')
    after = store(pg)
    newk = {k: sorted(set(after[k]) - set(before[k])) for k in ('lv', 'best')}; print("new keys written:", newk, "| top-level keys same:", sorted(after) == sorted(before), sorted(after))
    go(pg, 'record'); print("Record:", [c.replace('\n', ' ')[:130] for c in pg.evaluate("()=>[...document.querySelectorAll('#v-record .card')].slice(1,3).map(c=>c.innerText)")])
    go(pg, 'a-e'); pg.click('[data-inst="guitar"]'); go(pg, 'record'); print("Record on guitar:", [c.replace('\n', ' ')[:110] for c in pg.evaluate("()=>[...document.querySelectorAll('#v-record .card')].slice(1,3).map(c=>c.innerText)")])
    print("msgs", pg.msgs); pg.context.close()
    # (a sandboxed-frame run on bass was tried and dropped: inside a file:// sandboxed frame the harness cannot change the hash, on 0.9 as well, so the bass tabs cannot be reached there; listed under Not tested)
    # sanity for c1: the 0.9 comparison is not vacuous
    pg = open_page(b, OLD, state=passed_state('guitar'), hash_='technique'); print("0.9 guitar technique html bytes:", pg.evaluate("()=>document.getElementById('v-technique').innerHTML.length"), "title", pg.title()); pg.context.close()
    pg = open_page(b, OLD, state=passed_state('bass'), hash_='rudiments'); o = pg.inner_text('#v-rudiments'); pg.context.close()
    pg = open_page(b, NEW, state=passed_state('bass'), hash_='rudiments'); n_ = pg.inner_text('#v-rudiments'); pg.context.close()
    print("bass rudiments differ from 0.9 (expected):", o != n_, "| 0.9 said:", o[10:150].replace('\n', ' '))
    b.close()
