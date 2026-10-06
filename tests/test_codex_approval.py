from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import ANY, Mock
from urllib.error import HTTPError

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/strato/setup"))

import browser_setup  # noqa: E402
from workspace import SetupError  # noqa: E402

ORIGIN = "https://acme.stratoware.io"
SETUP_ID = "00000000-0000-4000-8000-000000000001"
URL = f"{ORIGIN}/ai-connections/approve#{SETUP_ID}"
TOKEN = "pqmcp_00000000-0000-4000-8000-000000000002_" + "x" * 43


def saved_connection(token, confirm):
    confirm()
    return "strato-acme"


@pytest.fixture
def transport(monkeypatch):
    requests = []
    responses = [
        {"id": SETUP_ID, "verification_url": URL, "user_code": "ABCD-1234"},
        {"status": "pending"},
        {"status": "issued", "secret": TOKEN},
        {"status": "completed"},
    ]
    opener = Mock()

    def respond(request, **kwargs):
        requests.append(request)
        payload = responses.pop(0)
        if isinstance(payload, Exception):
            raise payload
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = json.dumps(payload).encode()
        return response

    opener.open.side_effect = respond
    monkeypatch.setattr(browser_setup, "mcp_opener", lambda _: opener)
    monkeypatch.setattr(browser_setup.webbrowser, "open", Mock())
    monkeypatch.setattr(browser_setup.time, "sleep", lambda _: None)
    return requests, responses


def test_approval_keeps_proof_out_of_browser_and_saves_without_token_copying(transport):
    requests, _ = transport
    output = []
    save = Mock(side_effect=saved_connection)
    browser_setup.connect_in_browser(ORIGIN, save, output.append)
    browser_setup.webbrowser.open.assert_called_once_with(URL)
    save.assert_called_once_with(TOKEN, ANY)
    assert requests[-1].full_url.endswith("/complete")
    body = json.loads(requests[1].data)
    proof = body["verifier"]
    assert json.loads(requests[0].data)["challenge"] != proof
    for request in requests:
        assert proof not in request.full_url
        assert TOKEN not in request.full_url
        assert request.full_url.startswith(ORIGIN + "/api/mcp/setup-requests")
    assert TOKEN not in str(output) and proof not in str(output)
    assert "ABCD-1234" in str(output)


@pytest.mark.parametrize("failure", [SetupError("Cannot save"), KeyboardInterrupt()])
def test_failed_save_cancels_issued_credential(transport, failure):
    requests, responses = transport
    responses[:] = [
        responses[0],
        {"status": "issued", "secret": TOKEN},
        {"status": "canceled"},
    ]
    with pytest.raises(type(failure)):
        browser_setup.connect_in_browser(ORIGIN, Mock(side_effect=failure), Mock())
    assert requests[-1].full_url.endswith("/cancel")
    assert not any(request.full_url.endswith("/complete") for request in requests)


@pytest.mark.parametrize("status", [301, 403, 409, 410, 503])
def test_errors_never_print_remote_secret_payloads(transport, status):
    _, responses = transport
    responses[:] = [HTTPError(ORIGIN, status, TOKEN, {}, None)]
    with pytest.raises(SetupError) as error:
        browser_setup.connect_in_browser(ORIGIN, Mock(), Mock())
    assert TOKEN not in str(error.value)


def test_approval_url_cannot_redirect_to_another_host(transport):
    _, responses = transport
    responses[0]["verification_url"] = "https://evil.test/approve"
    with pytest.raises(SetupError, match="invalid approval details"):
        browser_setup.connect_in_browser(ORIGIN, Mock(), Mock())
    browser_setup.webbrowser.open.assert_not_called()


def test_lost_completion_response_cancels_instead_of_claiming_success(transport):
    requests, responses = transport
    responses[:] = [
        responses[0],
        {"status": "issued", "secret": TOKEN},
        TimeoutError(),
        {"status": "canceled"},
    ]
    output = []
    with pytest.raises(SetupError):
        browser_setup.connect_in_browser(
            ORIGIN, Mock(side_effect=saved_connection), output.append
        )
    assert requests[-1].full_url.endswith("/cancel")
    assert "Connection saved as" not in str(output)
