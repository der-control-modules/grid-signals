"""A cross-host redirect must not carry the `auth-token` header forward;
a same-host redirect (a different path or port) still carries it.
"""
import http.server
import threading

from co2_signal.co2_api import ElectricityMapsAPI

MARKER = "SECRET-MARKER-9f3a1c"


class _CaptureHandler(http.server.BaseHTTPRequestHandler):
    captured_headers = None

    def do_GET(self):
        type(self).captured_headers = dict(self.headers)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *args):
        pass


def _redirect_handler(location):
    class _RedirectHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(302)
            self.send_header("Location", location)
            self.end_headers()

        def log_message(self, *args):
            pass

    return _RedirectHandler


def _serve(handler_cls):
    server = http.server.HTTPServer(("127.0.0.1", 0), handler_cls)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _fetch_via_redirect(redirect_host):
    _CaptureHandler.captured_headers = None
    dest = _serve(_CaptureHandler)
    redirect = _serve(_redirect_handler(f"http://{redirect_host}:{dest.server_port}/"))
    try:
        api = ElectricityMapsAPI(api_key=MARKER, zone="US-CAL-CISO")
        api.base_url = f"http://127.0.0.1:{redirect.server_port}"
        api.get_co2_intensity()
    finally:
        redirect.shutdown()
        dest.shutdown()
    return {k.lower(): v for k, v in (_CaptureHandler.captured_headers or {}).items()}


def test_cross_host_redirect_drops_the_auth_token_header():
    headers = _fetch_via_redirect("localhost")
    assert "auth-token" not in headers


def test_same_host_redirect_keeps_the_auth_token_header():
    headers = _fetch_via_redirect("127.0.0.1")
    assert headers.get("auth-token") == MARKER
