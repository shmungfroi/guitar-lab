"""Independent check helpers for The Guitar Lab 0.9 (not the builder's harness; pattern reused from the 0.8 independent check).
Serves a folder over http://127.0.0.1 so a sandboxed iframe can load it, and records console, dialogs and requests.
serve() serves this branch's index.html; serve(main08()) serves 0.8 as it is on `main` (git show main:index.html) for comparison."""
import http.server, json, pathlib, threading, functools, socketserver, subprocess, tempfile, shutil, re

ROOT = pathlib.Path(__file__).resolve().parents[4]
RES = pathlib.Path(__file__).parent / "results"
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


def main08():
    tmp = pathlib.Path(tempfile.mkdtemp())
    (tmp / "index.html").write_bytes(subprocess.check_output(["git", "-C", str(ROOT), "show", "main:index.html"]))
    shutil.copytree(ROOT / "fonts", tmp / "fonts")
    return tmp


def serve(root=ROOT):
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(H, directory=str(root)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, "http://127.0.0.1:%d" % srv.server_address[1]


def watch(page):
    page.msgs, page.reqs, page.dialogs = [], [], []
    page.on("console", lambda m: page.msgs.append((m.type, m.text)))
    page.on("pageerror", lambda e: page.msgs.append(("pageerror", str(e))))
    page.on("request", lambda r: page.reqs.append(r.url))

    def dlg(d):
        page.dialogs.append((d.type, d.message))
        d.dismiss()
    page.on("dialog", dlg)
    return page


def open_app(browser, base, width=1280, height=900, scheme="dark", state=None, raw=None, hash_="", **ctxkw):
    """state: object saved as JSON under 'shredder'; raw: exact string saved under 'shredder'."""
    ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=scheme, **ctxkw)
    page = watch(ctx.new_page())
    page.set_default_timeout(10000)
    if state is not None or raw is not None:
        page.goto(base + "/fonts/")  # same origin, not the app
        page.evaluate("s=>{localStorage.clear();localStorage.setItem('shredder',s)}", raw if raw is not None else json.dumps(state))
    page.goto(base + "/index.html" + ("#" + hash_ if hash_ else ""))
    page.wait_for_selector("#tabs a[aria-current=page]", state="attached")
    return page


def bad_msgs(page):
    return [m for m in page.msgs if m[0] in ("error", "warning", "pageerror")]


def off_host(page, base):
    return [u for u in page.reqs if not u.startswith(base) and not u.startswith("blob:") and not u.startswith("data:")]


def rgb2hex(s):
    n = [float(x) for x in re.findall(r"[\d.]+", s)[:3]]
    return "#%02x%02x%02x" % tuple(int(round(x)) for x in n)


OVERFLOW = "()=>{const d=document.documentElement;return [d.scrollWidth,d.clientWidth,document.body.scrollWidth]}"
