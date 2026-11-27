"""Viewport screenshots of bass pages for the quality judgement (no toast: gates seeded)."""
from lib import *
import time
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in ((360, 760), (1280, 900)):
        for th in ('dark', 'light'):
            st = passed_state('bass', finish='bossa'); st["gates"] = {s + '@bass': 1795700000000 for s in IDS}
            pg = open_page(b, width=w, height=h, scheme=th, state=st, hash_='twelve-bar')
            pg.evaluate("()=>document.querySelector('#stage .tab').scrollIntoView({block:'center'})"); pg.screenshot(path=f"shots/v_tab_{w}_{th}.png")
            pg.evaluate("()=>{const d=[...document.querySelectorAll('#side details')];d.forEach(x=>x.open=true);d[0].scrollIntoView({block:'start'});window.scrollBy(0,-120)}"); pg.screenshot(path=f"shots/v_cards_{w}_{th}.png")
            go(pg, 'rudiments'); pg.evaluate("()=>window.scrollTo(0,document.querySelector('#v-rudiments').offsetTop-90)"); pg.screenshot(path=f"shots/v_rud_{w}_{th}.png")
            go(pg, 'technique'); pg.evaluate("()=>{const c=[...document.querySelectorAll('#v-technique .card')].find(c=>/Bossa bass/.test(c.textContent));c.scrollIntoView({block:'center'})}"); pg.screenshot(path=f"shots/v_bossa_{w}_{th}.png")
            pg.context.close()
    b.close()
