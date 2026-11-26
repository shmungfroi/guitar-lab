import sys
import pathlib

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import uihelp  # noqa: E402


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(args=uihelp.LAUNCH_ARGS)
        yield b
        b.close()


@pytest.fixture
def app(browser):
    """Factory: app(width=..., scheme=..., state={...}, hash_='gig') -> page. Closed after the test."""
    pages = []

    def make(**kw):
        pg = uihelp.open_app(browser, **kw)
        pages.append(pg)
        return pg

    yield make
    for pg in pages:
        uihelp.close(pg)
