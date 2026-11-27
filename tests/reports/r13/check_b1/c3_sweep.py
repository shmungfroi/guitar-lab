"""Checks 7-8: sweep 7 tabs x 5 instruments x 360/1280 x light/dark (Path at all 8 stages; Invent also after a roll), console, overflow, network, dialogs; bass screenshots."""
import json, re
from lib import *
OV = r"""()=>{const W=document.documentElement.clientWidth,de=document.documentElement,bad=[];if(de.scrollWidth>W+1)bad.push('page scrollWidth '+de.scrollWidth+'>'+W);
const clip=p=>{const o=getComputedStyle(p).overflowX;return o!=='visible'};
for(const el of document.querySelectorAll('body *')){const r=el.getBoundingClientRect();if(!r.width||!r.height)continue;if(r.right<=W+1&&r.left>=-1)continue;const cs=getComputedStyle(el);if(cs.position==='fixed'||cs.visibility==='hidden'||el.closest('.sr'))continue;
let p=el.parentElement,ok=false;while(p&&p!==document.body){if(clip(p)){const pr=p.getBoundingClientRect();if(pr.right<=W+1&&pr.left>=-1){ok=true;break}}p=p.parentElement}if(!ok)bad.push(el.tagName+'.'+el.className+' '+Math.round(r.left)+'..'+Math.round(r.right))}return bad.slice(0,4)}"""
SCROLL = r"""()=>[...document.querySelectorAll('[id^=v-]:not(.hide) .tab, [id^=v-]:not(.hide) .card')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.className+': '+e.scrollWidth+'>'+e.clientWidth+' '+e.textContent.slice(0,30))"""
views = 0; problems = []; reqs = set(); dlg = 0; inner = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for inst in INST:
        for w in (360, 1280):
            for th in ('dark', 'light'):
                st = passed_state(inst, finish='flam')
                pg = open_page(b, width=w, height=800 if w == 360 else 900, scheme=th, state=st)
                def chk(label):
                    global views
                    views += 1
                    o = pg.evaluate(OV)
                    if o: problems.append((inst, w, th, label, o))
                    s = pg.evaluate(SCROLL)
                    if s: inner.setdefault((inst, w, label), s)
                for sid in IDS:
                    go(pg, sid); chk('path:' + sid)
                    if inst == 'bass' and sid in ('twelve-bar', 'a-e', 'beyond'): pg.screenshot(path=f"shots/bass_path_{sid}_{w}_{th}.png", full_page=True)
                go(pg, 'twelve-bar')
                for v in VIEWS[1:]:
                    go(pg, v); chk(v)
                    if inst == 'bass' and v in ('rudiments', 'technique'): pg.screenshot(path=f"shots/bass_{v}_{w}_{th}.png", full_page=True)
                go(pg, 'invent'); pg.click('#roll'); chk('invent-rolled')
                if inst == 'bass':
                    n = pg.locator('[data-bcell]').count()
                    for _ in range(4): pg.click(f'[data-bcell="{n-1}"]')
                    pg.click('[data-bcell="3"]'); pg.click('[data-bcell="3"]'); chk('invent-built')
                    pg.screenshot(path=f"shots/bass_invent_{w}_{th}.png", full_page=True)
                    go(pg, 'six-eight'); go(pg, 'invent'); pg.click('#roll'); chk('invent-6/8')
                if pg.msgs: problems.append((inst, w, th, 'console', pg.msgs[:3]))
                reqs |= set(r.split('#')[0] for r in pg.reqs); dlg += len(pg.evaluate("()=>window.__dlg"))
                pg.context.close()
    b.close()
print("views checked:", views, "| problems:", len(problems)); [print("  ", x) for x in problems[:20]]
print("requests:", sorted(reqs)); print("dialog calls:", dlg)
print("inner scrollers (elements that scroll sideways inside themselves):"); [print("  ", k, v[:3]) for k, v in inner.items() if k[0] == 'bass']
print("  non-bass inner scrollers:", sorted(set((k[0], k[1], k[2]) for k in inner if k[0] != 'bass'))[:12])
