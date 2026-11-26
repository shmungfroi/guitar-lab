"""Independent check helpers for The Guitar Lab 0.8 (not the builder's harness).
Serves the repo over http://127.0.0.1 so a sandboxed iframe can load it, and records every request."""
import http.server, json, pathlib, threading, functools, socketserver

ROOT = pathlib.Path(__file__).resolve().parents[4]
WRAP = """<!doctype html><meta charset=utf-8><title>wrap</title><body style="margin:0">
<iframe id=f sandbox="%s" src="/index.html%s" style="border:0;width:100vw;height:100vh"></iframe>"""


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")  # fonts for the opaque-origin frame
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path.startswith("/__wrap"):
            from urllib.parse import urlparse, parse_qs
            q = parse_qs(urlparse(self.path).query)
            body = (WRAP % (q.get("sb", ["allow-scripts"])[0], "#" + q.get("h", [""])[0])).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


def serve():
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(H, directory=str(ROOT)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, "http://127.0.0.1:%d" % srv.server_address[1]


def watch(page):
    """Record console (all types), page errors, dialogs and requests on a page."""
    page.msgs, page.reqs, page.dialogs = [], [], []
    page.on("console", lambda m: page.msgs.append((m.type, m.text)))
    page.on("pageerror", lambda e: page.msgs.append(("pageerror", str(e))))
    page.on("request", lambda r: page.reqs.append(r.url))

    def dlg(d):
        page.dialogs.append((d.type, d.message))
        d.dismiss()
    page.on("dialog", dlg)
    return page


def open_app(browser, base, width=1280, height=900, scheme="dark", state=None, hash_="", **ctxkw):
    ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=scheme, **ctxkw)
    page = watch(ctx.new_page())
    page.set_default_timeout(10000)
    if state is not None:
        page.goto(base + "/fonts/")  # same origin, not the app
        page.evaluate("s=>{localStorage.clear();localStorage.setItem('shredder',s)}", json.dumps(state))
    page.goto(base + "/index.html" + ("#" + hash_ if hash_ else ""))
    page.wait_for_selector("#tabs a[aria-current=page]", state="attached")
    return page


def bad_msgs(page):
    return [m for m in page.msgs if m[0] in ("error", "warning", "pageerror")]


def lum(hexc):
    h = hexc.lstrip("#")
    v = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    v = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in v]
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]


def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def rgb2hex(s):
    import re
    n = [float(x) for x in re.findall(r"[\d.]+", s)[:3]]
    return "#%02x%02x%02x" % tuple(int(round(x)) for x in n)


OVERFLOW = "()=>{const d=document.documentElement;return [d.scrollWidth,d.clientWidth,document.body.scrollWidth]}"
