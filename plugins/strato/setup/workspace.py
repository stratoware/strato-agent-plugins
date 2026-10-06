from __future__ import annotations

import json
import re
import socket
import ssl
from ipaddress import ip_address
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    HTTPSHandler,
    ProxyHandler,
    Request,
    build_opener,
)

import truststore


class SetupError(ValueError):
    """An actionable message that never includes credentials or server payloads."""


TENANT_LABEL = r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
LOCAL_HOST = re.compile(TENANT_LABEL + r"\.stratoware\.localhost")


def is_local_workspace(origin: str) -> bool:
    return LOCAL_HOST.fullmatch(urlsplit(origin).hostname or "") is not None


def workspace_origin(value: str, *, allow_local: bool = False) -> str:
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        raise SetupError("Enter a valid HTTPS Strato workspace address.") from None
    host = parsed.hostname or ""
    local = allow_local and LOCAL_HOST.fullmatch(host) is not None
    authority = f"{host}:{port}" if local and port is not None else host
    if (
        parsed.scheme != "https"
        or parsed.netloc != authority
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
        or value not in (f"https://{authority}", f"https://{authority}/")
        or (local and port == 0)
        or not (
            local
            or re.fullmatch(TENANT_LABEL + r"\.(?:staging\.)?stratoware\.io", host)
        )
        or host.split(".")[0] in {"mcp", "www", "api", "app", "auth", "staging"}
    ):
        raise SetupError(
            "Enter your HTTPS Strato workspace address, without a path or credentials. "
            "Local development workspaces require --allow-local."
        )
    # Canonicalize the default HTTPS port so credentials have one key per origin.
    return f"https://{host}" if port == 443 else f"https://{authority}"


def server_name(origin: str) -> str:
    if is_local_workspace(origin):
        parsed = urlsplit(origin)
        return f"strato-{parsed.hostname.split('.')[0]}-local-{parsed.port or 443}"
    return "strato-" + urlsplit(origin).hostname.removesuffix(".stratoware.io").replace(
        ".", "-"
    )


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def mcp_opener(origin: str):
    if not is_local_workspace(origin):
        return build_opener(NoRedirect())
    parsed = urlsplit(origin)
    try:
        addresses = socket.getaddrinfo(
            parsed.hostname, parsed.port or 443, type=socket.SOCK_STREAM
        )
    except OSError:
        raise SetupError(
            "The local workspace hostname could not be resolved. Check local DNS and the stack."
        ) from None
    if not addresses or any(
        not ip_address(address[4][0]).is_loopback for address in addresses
    ):
        raise SetupError(
            "Local Strato workspaces must resolve only to this computer's loopback addresses."
        )
    # Use the OS trust store (including an installed mkcert CA), with verification
    # enabled. Local credentials must never travel through an HTTP(S) proxy.
    context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    return build_opener(NoRedirect(), ProxyHandler({}), HTTPSHandler(context=context))


def verify_token(origin: str, token: str, *, allow_local: bool = False) -> None:
    """Check authenticated DHF read access without returning customer records."""
    origin = workspace_origin(origin, allow_local=allow_local)
    if not re.fullmatch(r"pqmcp_[0-9a-f-]{36}_[A-Za-z0-9_-]{32,128}", token):
        raise SetupError(
            "Strato returned an invalid connection credential. Start setup again from Connectors."
        )
    opener = mcp_opener(origin)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    requests = [
        (
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "strato-setup", "version": "1"},
            },
        ),
        ("notifications/initialized", {}),
        ("tools/call", {"name": "products_list_v1", "arguments": {}}),
    ]
    for request_id, (method, params) in enumerate(requests, 1):
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        if method != "notifications/initialized":
            message["id"] = request_id
        body = json.dumps(message).encode()
        try:
            with opener.open(
                Request(origin + "/api/mcp", data=body, headers=headers), timeout=20
            ) as response:
                if method == "notifications/initialized":
                    continue
                session = response.headers.get("Mcp-Session-Id")
                if session:
                    headers["Mcp-Session-Id"] = session
                payload = response.read(2_000_001)
                if len(payload) > 2_000_000:
                    raise SetupError(
                        "The MCP response was too large. Contact Strato support."
                    )
                result = json.loads(payload)
        except HTTPError as exc:
            if exc.code == 401:
                raise SetupError(
                    "This token is invalid, expired, revoked, or belongs to another workspace."
                ) from None
            if exc.code == 403:
                raise SetupError(
                    "Access was denied. Check DHF read permission and workspace network policies."
                ) from None
            raise SetupError(
                "Strato could not complete the connection check. Try again later."
            ) from None
        except URLError as exc:
            if isinstance(exc.reason, ssl.SSLCertVerificationError):
                raise SetupError(
                    "The workspace HTTPS certificate is not trusted or does not match its hostname. "
                    "For local development, install the stack's mkcert CA in the OS trust store and retry."
                ) from None
            raise SetupError(
                "Could not reach the MCP endpoint. Check the workspace address and that the stack is running."
            ) from None
        except (TimeoutError, ValueError):
            raise SetupError(
                "Could not read a valid MCP response. Check the workspace address and network access."
            ) from None
        if (
            not isinstance(result, dict)
            or result.get("id") != request_id
            or "error" in result
        ):
            raise SetupError(
                "The MCP connection check failed. Check token permissions and try again."
            )
        data = result.get("result")
        if not isinstance(data, dict) or data.get("isError"):
            raise SetupError(
                "DHF read access could not be confirmed. Check the token's permissions."
            )
        if method == "initialize":
            headers["MCP-Protocol-Version"] = data.get("protocolVersion", "2025-03-26")
