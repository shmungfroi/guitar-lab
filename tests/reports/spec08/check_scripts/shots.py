"""Close-up screenshots for the look check (keyboards both themes; Present drum grid at 360 and 1280)."""
import pathlib
from playwright.sync_api import sync_playwright
from common import *
shots = pathlib.Path(__file__).parent / "shots"; shots.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); srv, base = serve()
    for scheme in ("dark", "light"):
        pg = open_app(b, base, width=900, scheme=scheme, state={"inst": "keys", "stage": "a-e", "capo": {"a-e": 2}})
        pg.locator("#stage svg.kb").first.locator("xpath=ancestor::div[1]").screenshot(path=str(shots / ("kb_%s.png" % scheme)))
        pg.locator("#side .card").first.screenshot(path=str(shots / ("fncard_%s.png" % scheme))); pg.context.close()
    for w in (360, 1280):
        pg = open_app(b, base, width=w, height=800, state={"inst": "drums"}, hash_="gig"); pg.click("#present"); pg.wait_for_timeout(100)
        pg.locator("#v-gig .dgw").first.scroll_into_view_if_needed(); pg.locator("#v-gig .dgw").first.screenshot(path=str(shots / ("present_dg_%d.png" % w))); pg.context.close()
    pg = open_app(b, base, width=900, state={"inst": "drums"}); pg.locator("#side .card").nth(1).screenshot(path=str(shots / "drums_metro_card.png")); pg.locator(".mbar").screenshot(path=str(shots / "drums_mbar.png")); pg.context.close()
    b.close()
