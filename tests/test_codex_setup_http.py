from __future__ import annotations

import json
import socket
import ssl
import sys
from pathlib import Path
from unittest.mock import Mock
from urllib.error import HTTPError, URLError

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/strato/setup"))

import workspace  # noqa: E402

ORIGIN = "https://acme.stratoware.io"
TOKEN = "pqmcp_00000000-0000-4000-8000-000000000001_" + "x" * 43


def test_verification_only_uses_dhf_read_tool(monkeypatch):
    requests = []
    opener = Mock()

    def respond(req, **kwargs):
        assert req.full_url == ORIGIN + "/api/mcp"
        assert req.get_header("Authorization") == "Bearer " + TOKEN
        body = json.loads(req.data)
        requests.append(body)
        response = Mock()
        response.headers = {}
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {"protocolVersion": "2025-03-26"}
                if body["method"] == "initialize"
                else {"isError": False, "content": []},
            }
        ).encode()
        return response

    opener.open.side_effect = respond
    monkeypatch.setattr(workspace, "build_opener", lambda *args: opener)
    workspace.verify_token(ORIGIN, TOKEN)
    assert requests[-1]["params"] == {"name": "products_list_v1", "arguments": {}}


@pytest.mark.parametrize("status", [301, 302, 401, 403, 500])
def test_bad_remote_responses_do_not_leak_credentials(monkeypatch, status):
    opener = Mock()
    opener.open.side_effect = HTTPError(ORIGIN, status, TOKEN, {}, None)
    monkeypatch.setattr(workspace, "build_opener", lambda *args: opener)
    with pytest.raises(workspace.SetupError) as error:
        workspace.verify_token(ORIGIN, TOKEN)
    assert TOKEN not in str(error.value)
    assert (
        workspace.NoRedirect().redirect_request(
            None, None, status, "", {}, "https://evil.test"
        )
        is None
    )


def test_invalid_or_injected_token_never_reaches_network(monkeypatch):
    opener = Mock()
    monkeypatch.setattr(workspace, "build_opener", opener)
    with pytest.raises(workspace.SetupError):
        workspace.verify_token(ORIGIN, TOKEN + "\r\nX-Injected: value")
    opener.assert_not_called()


class TestLocalTransport:
    origin = "https://demo.stratoware.localhost:13100"

    def test_local_certificate_verification_stays_enabled_and_proxy_is_disabled(
        self, monkeypatch
    ):
        monkeypatch.setattr(
            workspace.socket,
            "getaddrinfo",
            lambda *args, **kwargs: [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 13100)),
            ],
        )
        build = Mock()
        monkeypatch.setattr(workspace, "build_opener", build)
        workspace.mcp_opener(self.origin)
        handlers = build.call_args.args
        context = next(
            handler._context
            for handler in handlers
            if isinstance(handler, workspace.HTTPSHandler)
        )
        assert context.check_hostname
        assert context.verify_mode == ssl.CERT_REQUIRED
        assert (
            next(
                handler.proxies
                for handler in handlers
                if isinstance(handler, workspace.ProxyHandler)
            )
            == {}
        )
        assert any(isinstance(handler, workspace.NoRedirect) for handler in handlers)

    def test_non_loopback_dns_is_rejected_before_sending_token(self, monkeypatch):
        monkeypatch.setattr(
            workspace.socket,
            "getaddrinfo",
            lambda *args, **kwargs: [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("203.0.113.1", 13100)),
            ],
        )
        build = Mock()
        monkeypatch.setattr(workspace, "build_opener", build)
        with pytest.raises(workspace.SetupError, match="loopback"):
            workspace.verify_token(self.origin, TOKEN, allow_local=True)
        build.assert_not_called()

    def test_local_verification_cannot_skip_opt_in(self, monkeypatch):
        opener = Mock()
        monkeypatch.setattr(workspace, "mcp_opener", opener)
        with pytest.raises(workspace.SetupError, match="allow-local"):
            workspace.verify_token(self.origin, TOKEN)
        opener.assert_not_called()

    def test_untrusted_certificate_has_actionable_credential_free_error(
        self, monkeypatch
    ):
        opener = Mock()
        opener.open.side_effect = URLError(ssl.SSLCertVerificationError(TOKEN))
        monkeypatch.setattr(workspace, "mcp_opener", lambda origin: opener)
        with pytest.raises(
            workspace.SetupError, match="certificate is not trusted"
        ) as error:
            workspace.verify_token(self.origin, TOKEN, allow_local=True)
        assert TOKEN not in str(error.value)
