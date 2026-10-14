from __future__ import annotations

import json
import socket
import ssl
import sys
from pathlib import Path
from unittest.mock import Mock
from urllib.error import URLError

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/strato/setup"))

import workspace  # noqa: E402

ORIGIN = "https://acme.stratoware.io"
TOKEN = "pqmcp_00000000-0000-4000-8000-000000000001_" + "x" * 43


def test_native_discovery_checks_issuer_and_protocol(monkeypatch):
    metadata = {
        "issuer": ORIGIN,
        "authorization_endpoint": ORIGIN + "/oauth/authorize",
        "token_endpoint": ORIGIN + "/oauth/token",
        "token_endpoint_auth_methods_supported": ["none"],
        "code_challenge_methods_supported": ["S256"],
        "authorization_response_iss_parameter_supported": True,
    }
    response = Mock()
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    response.read.return_value = json.dumps(metadata).encode()
    opener = Mock()
    opener.open.return_value = response
    monkeypatch.setattr(workspace, "mcp_opener", lambda origin: opener)
    workspace.verify_oauth_server(ORIGIN)
    assert (
        opener.open.call_args.args[0].full_url
        == ORIGIN + "/.well-known/oauth-authorization-server"
    )
    metadata["issuer"] = "https://attacker.test"
    response.read.return_value = json.dumps(metadata).encode()
    with pytest.raises(workspace.SetupError):
        workspace.verify_oauth_server(ORIGIN)


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
            workspace.verify_oauth_server(self.origin, allow_local=True)
        build.assert_not_called()

    def test_local_verification_cannot_skip_opt_in(self, monkeypatch):
        opener = Mock()
        monkeypatch.setattr(workspace, "mcp_opener", opener)
        with pytest.raises(workspace.SetupError, match="allow-local"):
            workspace.verify_oauth_server(self.origin)
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
            workspace.verify_oauth_server(self.origin, allow_local=True)
        assert TOKEN not in str(error.value)
