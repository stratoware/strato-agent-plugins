from __future__ import annotations

import json
import re
import socket
import ssl
from ipaddress import ip_address
from urllib.error import URLError
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


def verify_oauth_server(origin: str, *, allow_local: bool = False) -> None:
    origin = workspace_origin(origin, allow_local=allow_local)
    opener = mcp_opener(origin)
    try:
        with opener.open(
            Request(
                origin + "/.well-known/oauth-authorization-server",
                headers={"Accept": "application/json"},
            ),
            timeout=20,
        ) as response:
            body = response.read(16385)
            if len(body) > 16384:
                raise ValueError()
            metadata = json.loads(body)
        if (
            metadata.get("issuer") != origin
            or metadata.get("authorization_endpoint") != origin + "/oauth/authorize"
            or metadata.get("token_endpoint") != origin + "/oauth/token"
            or "none" not in metadata.get("token_endpoint_auth_methods_supported", [])
            or "S256" not in metadata.get("code_challenge_methods_supported", [])
            or not metadata.get("authorization_response_iss_parameter_supported")
        ):
            raise ValueError()
    except URLError as error:
        if isinstance(error.reason, ssl.SSLCertVerificationError):
            raise SetupError(
                "The workspace HTTPS certificate is not trusted. Install the local stack CA in the OS trust store and retry."
            ) from None
        raise SetupError(
            "Could not reach Strato OAuth. Check the workspace and network policy."
        ) from None
    except (ValueError, OSError):
        raise SetupError(
            "Native OAuth is not available at this Strato workspace. Check the deployment, HTTPS trust, and network policy, then retry."
        ) from None
