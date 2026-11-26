"""Shared Playwright helpers for test_ui.py and test_timing.py."""
import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Point SHREDDER_INDEX at another copy (e.g. an older build) to test that instead.
URL = pathlib.Path(os.environ.get("SHREDDER_INDEX") or ROOT / "index.html").resolve().as_uri()

# Records every AudioContext, resume() call, node connection and source start,
# so tests can check what the band scheduled without listening to it.
AUDIO_JS = r"""
(()=>{if(window.__aud)return;const A=window.__aud={starts:[],ctxs:[],resumes:0,edges:new Map()};
const O=window.AudioContext||window.webkitAudioContext;if(!O)return;
const res=O.prototype.resume;O.prototype.resume=function(){A.resumes++;return res.apply(this,arguments)};
class AC extends O{constructor(...a){super(...a);A.ctxs.push(this)}}
window.AudioContext=AC;window.webkitAudioContext=AC;
const conn=AudioNode.prototype.connect;AudioNode.prototype.connect=function(d,...r){if(!A.edges.has(this))A.edges.set(this,[]);A.edges.get(this).push(d);return conn.call(this,d,...r)};
// AudioBufferSourceNode has its own start(), so wrap both prototypes.
for(const C of [AudioScheduledSourceNode,AudioBufferSourceNode,OscillatorNode]){if(!Object.prototype.hasOwnProperty.call(C.prototype,'start'))continue;
 const st=C.prototype.start;C.prototype.start=function(when,...r){if(!this.__rec){this.__rec=1;const osc=this instanceof OscillatorNode;
  A.starts.push({kind:osc?'osc':(this instanceof AudioBufferSourceNode?'buf':'other'),when:when||0,now:this.context.currentTime,wall:performance.now(),
   freq:osc?this.frequency.value:null,type:osc?this.type:null,dur:this.buffer?this.buffer.duration:null,node:this})}
  return st.call(this,when,...r)}}
const gainOf=n=>n instanceof GainNode?n.gain.value:1;
window.__audible=e=>{const dest=e.node.context.destination;let best=0;const walk=(n,g,seen)=>{if(n===dest){best=Math.max(best,g);return}if(seen.has(n))return;seen.add(n);
 for(const d of (A.edges.get(n)||[]))if(d instanceof AudioNode)walk(d,g*gainOf(d),seen);seen.delete(n)};walk(e.node,1,new Set());return best};
window.__starts=()=>A.starts.map((e,i)=>({i,kind:e.kind,when:e.when,now:e.now,wall:e.wall,freq:e.freq,type:e.type,dur:e.dur}));
window.__audState=()=>({ctxs:A.ctxs.length,states:A.ctxs.map(c=>c.state),resumes:A.resumes,now:A.ctxs.length?A.ctxs[0].currentTime:null});
})();
"""

LAUNCH_ARGS = ["--autoplay-policy=no-user-gesture-required"]


def open_app(browser, width=1280, height=900, scheme="dark", state=None, hash_="", clock=False):
    ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=scheme)
    ctx.add_init_script(AUDIO_JS)
    page = ctx.new_page()
    page.errors = []
    page.on("console", lambda m: page.errors.append("console: " + m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: page.errors.append("pageerror: " + str(e)))
    if clock:
        page.clock.install()
    if state is not None:  # seed the app's own saved state, then load it fresh
        page.goto(URL + "#__seed")
        page.evaluate("s=>{localStorage.clear();localStorage.setItem('shredder',s)}", json.dumps(state))
        page.goto("about:blank")
    page.goto(URL + (("#" + hash_) if hash_ else ""))
    page.set_default_timeout(10_000)
    page.wait_for_selector("#tabs a[aria-current=page]", state="attached")
    return page


def go(page, h):
    """Change the hash and wait for the app's hashchange render to finish."""
    page.evaluate("""h=>new Promise(r=>{if(location.hash==='#'+h){r();return}
      window.addEventListener('hashchange',()=>setTimeout(r,0),{once:true});location.hash=h})""", h)


def state(page):
    return page.evaluate("()=>JSON.parse(localStorage.getItem('shredder')||'{}')")


def starts(page):
    return page.evaluate("()=>window.__starts()")


def close(page):
    page.context.close()


OVERFLOW_JS = r"""
()=>{const W=document.documentElement.clientWidth,bad=[];
 const de=document.documentElement;if(de.scrollWidth>W+1)bad.push('page scrollWidth '+de.scrollWidth+' > '+W);
 const clipper=p=>{const o=getComputedStyle(p).overflowX;return o==='auto'||o==='scroll'||o==='hidden'||o==='clip'};
 const name=el=>el.tagName.toLowerCase()+(el.id?'#'+el.id:'')+(el.className&&typeof el.className==='string'?'.'+el.className.trim().split(/\s+/).join('.'):'');
 for(const el of document.querySelectorAll('body *')){const r=el.getBoundingClientRect();if(!r.width||!r.height)continue;
  if(r.right<=W+1&&r.left>=-1)continue;const cs=getComputedStyle(el);if(cs.position==='fixed'||cs.visibility==='hidden'||el.closest('.sr'))continue;
  let p=el.parentElement,ok=false;while(p&&p!==document.body){if(clipper(p)){const pr=p.getBoundingClientRect();if(pr.right<=W+1&&pr.left>=-1){ok=true;break}}p=p.parentElement}
  if(ok)continue;let anc=el.parentElement,dup=false;while(anc&&anc!==document.body){if(anc.__ovf){dup=true;break}anc=anc.parentElement}
  el.__ovf=1;if(!dup)bad.push(name(el)+' spans '+Math.round(r.left)+'..'+Math.round(r.right)+' in '+W)}
 document.querySelectorAll('body *').forEach(e=>{delete e.__ovf});return bad.slice(0,6)}
"""

# Checks that the key panels for the current view rendered. Returns a list of problems.
PANELS_JS = r"""
({view,inst,nch,nrud,ntech})=>{const P=[];const q=s=>document.querySelectorAll(s);const vis=el=>!!el&&el.getClientRects().length>0;
 const sec=document.getElementById('v-'+view);if(!vis(sec))P.push('section v-'+view+' not visible');
 const cur=document.querySelector('#tabs a[aria-current=page]');if(!cur||cur.getAttribute('href')!=='#'+view)P.push('tab not marked current');
 if(view==='path'){if(!vis(document.querySelector('#stage h2')))P.push('no stage title');if(q('#neck .fr').length!==8)P.push('neck frets '+q('#neck .fr').length);
  if(!q('#side .card').length)P.push('no side cards');if(!q('#stage .rmap').length)P.push('no road map');if(!document.getElementById('playMap'))P.push('no play button');
  const st=document.getElementById('stage');
  if(inst==='guitar'&&st.querySelectorAll('.cb svg').length!==nch)P.push('chord boxes '+st.querySelectorAll('.cb svg').length+' != '+nch);
  if(inst==='bass'&&!/Root/.test(st.textContent))P.push('no bass roots');
  if(inst==='drums'&&!st.querySelector('table'))P.push('no drum grid');
  if(inst==='keys'&&st.querySelectorAll('svg.kb').length!==nch)P.push('keyboards '+st.querySelectorAll('svg.kb').length+' != '+nch);
  if(inst==='vocals'&&!/cue sheet/i.test(st.textContent))P.push('no cue sheet')}
 if(view==='warm-up'){if(q('input[data-warm]').length!==5)P.push('warm-up items');if(q('button[data-ref]').length!==6)P.push('reference strings')}
 if(view==='rudiments'&&q('#v-rudiments .card').length!==nrud)P.push('rudiment cards '+q('#v-rudiments .card').length);
 if(view==='technique'){if(q('#v-technique .card').length!==ntech)P.push('technique cards '+q('#v-technique .card').length);if(q('#v-technique svg.fb').length!==4)P.push('fretboards')}
 if(view==='invent'&&!document.getElementById('roll'))P.push('no roll button');
 if(view==='gig'){if(q('input[data-gsong]').length!==6)P.push('gig songs');if(!document.getElementById('playGig'))P.push('no gig play');if(!q('#v-gig .rmap').length)P.push('no gig chart')}
 if(view==='record'&&!document.getElementById('jf'))P.push('no journal');
 return P}
"""
