from __future__ import annotations

import json
import os
import queue
import shutil
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlsplit

import pytest
from test_codex_setup import configuration


@pytest.mark.skipif(not shutil.which("codex"), reason="Codex is not installed")
def test_native_codex_authorization_and_exchange_parameters(tmp_path):
    """Exercise the installed client without issuing or storing any credential."""
    exchanges = queue.Queue()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_GET(self):
            if "oauth-protected-resource" in self.path:
                self.respond(
                    200,
                    {
                        "resource": origin + "/api/mcp",
                        "authorization_servers": [origin],
                    },
                )
            elif "oauth-authorization-server" in self.path:
                self.respond(
                    200,
                    {
                        "issuer": origin,
                        "authorization_endpoint": origin + "/oauth/authorize",
                        "token_endpoint": origin + "/oauth/token",
                        "response_types_supported": ["code"],
                        "grant_types_supported": [
                            "authorization_code",
                            "refresh_token",
                        ],
                        "token_endpoint_auth_methods_supported": ["none"],
                        "code_challenge_methods_supported": ["S256"],
                        "authorization_response_iss_parameter_supported": True,
                    },
                )
            else:
                self.send_response(401)
                self.send_header(
                    "WWW-Authenticate",
                    f'Bearer resource_metadata="{origin}/.well-known/oauth-protected-resource/api/mcp"',
                )
                self.end_headers()

        def do_POST(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            if self.path == "/oauth/token":
                exchanges.put(
                    (parse_qs(body.decode()), self.headers.get("Authorization"))
                )
                self.respond(400, {"error": "invalid_grant"})
            else:
                self.do_GET()

        def respond(self, status, body):
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        origin = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        config, name = configuration.prepare_config("", "https://acme.stratoware.io")
        (tmp_path / "config.toml").write_text(
            config.replace("https://acme.stratoware.io", origin)
        )
        process = subprocess.Popen(
            ["codex", "mcp", "login", name, "--no-browser"],
            env={**os.environ, "CODEX_HOME": str(tmp_path)},
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        lines = queue.Queue()

        def read_output():
            for line in process.stdout:
                lines.put(line.strip())

        reader = threading.Thread(target=read_output, daemon=True)
        reader.start()
        try:
            for _ in range(20):
                line = lines.get(timeout=10)
                if line.startswith(origin + "/oauth/authorize"):
                    parameters = parse_qs(urlsplit(line).query)
                    break
            else:
                pytest.fail("Codex did not start OAuth authorization")
            assert parameters["client_id"] == ["strato-codex-prod"]
            assert set(parameters["resource"]) == {origin + "/api/mcp"}
            assert parameters["code_challenge_method"] == ["S256"]
            assert parameters["scope"] == ["dhf:records:read dhf:development:write"]
            callback = parameters["redirect_uri"][0]
            parsed = urlsplit(callback)
            assert (parsed.scheme, parsed.hostname, parsed.path) == (
                "http",
                "127.0.0.1",
                "/callback",
            )
            assert parsed.port
            process.stdin.write(
                callback
                + "?"
                + urlencode(
                    {
                        "code": "test-code",
                        "state": parameters["state"][0],
                        "iss": origin,
                    }
                )
                + "\n"
            )
            process.stdin.flush()
            body, authorization = exchanges.get(timeout=10)
            assert not authorization
            assert body["client_id"] == ["strato-codex-prod"]
            assert set(body["resource"]) == {origin + "/api/mcp"}
            assert body["redirect_uri"] == [callback]
            assert len(body["code_verifier"][0]) >= 43
            assert process.wait(timeout=10) != 0
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
            reader.join(timeout=5)
            process.stdin.close()
            process.stdout.close()
            server.shutdown()
            thread.join(timeout=5)
