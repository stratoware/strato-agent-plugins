from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
import uuid
import webbrowser
from collections.abc import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request

from workspace import SetupError, mcp_opener


class ApprovalClient:
    """Exchange proof directly with Strato; the browser never receives it."""

    def __init__(self, origin: str):
        self.origin = origin
        self.opener = mcp_opener(origin)
        self.verifier = secrets.token_urlsafe(48)
        self.setup_id: str | None = None

    def post(self, path: str, payload: dict) -> dict:
        try:
            with self.opener.open(
                Request(
                    self.origin + "/api/mcp/" + path,
                    data=json.dumps(payload).encode(),
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                ),
                timeout=20,
            ) as response:
                raw = response.read(16385)
                if len(raw) > 16384:
                    raise ValueError()
                result = json.loads(raw)
                if not isinstance(result, dict):
                    raise ValueError()
                return result
        except HTTPError as error:
            messages = {
                401: "Sign in to Strato and start setup again.",
                403: "Strato rejected this setup. Check workspace access and network policies, then start again.",
                404: "Browser approval is unavailable. Update Strato and the setup helper, then try again.",
                409: "This approval was already used or setup could not finish. Start setup again from Connectors.",
                410: "Setup was canceled or expired. Start again from Connectors when ready.",
                429: "Too many setup attempts. Wait a few minutes and try again.",
                503: "Strato setup is temporarily unavailable. Try again later.",
            }
            raise SetupError(
                messages.get(
                    error.code, "Strato could not complete setup. Try again later."
                )
            ) from None
        except (URLError, TimeoutError, ValueError, OSError):
            raise SetupError(
                "Could not securely reach Strato. Check the stack, network, and trusted HTTPS certificate, then start setup again."
            ) from None

    def start(self) -> tuple[str, str]:
        challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(self.verifier.encode()).digest())
            .decode()
            .rstrip("=")
        )
        result = self.post(
            "setup-requests", {"client": "codex", "challenge": challenge}
        )
        try:
            setup_id = str(uuid.UUID(result["id"]))
            expected = self.origin + "/ai-connections/approve#" + setup_id
            code = result["user_code"]
            if result["verification_url"] != expected or not isinstance(code, str):
                raise ValueError()
            if (
                len(code) != 9
                or code[4] != "-"
                or any(c not in "0123456789ABCDEF" for c in code.replace("-", ""))
            ):
                raise ValueError()
        except (KeyError, ValueError, TypeError, AttributeError):
            raise SetupError(
                "Strato returned invalid approval details. Update Strato and try again."
            ) from None
        self.setup_id = setup_id
        return expected, code

    def exchange(self, action: str) -> dict:
        if self.setup_id is None or action not in {"redeem", "complete", "cancel"}:
            raise SetupError("Setup has not started")
        return self.post(
            f"setup-requests/{self.setup_id}/{action}", {"verifier": self.verifier}
        )

    def wait_for_approval(self) -> str:
        deadline = time.monotonic() + 600
        while time.monotonic() < deadline:
            result = self.exchange("redeem")
            if result.get("status") == "issued" and isinstance(
                result.get("secret"), str
            ):
                return result["secret"]
            if result.get("status") != "pending":
                raise SetupError(
                    "Unexpected approval response. Start setup again from Connectors."
                )
            time.sleep(3)
        raise SetupError("Setup expired after ten minutes. Start again when ready.")

    def cancel(self) -> None:
        if self.setup_id is not None:
            try:
                self.exchange("cancel")
            except SetupError:
                # An unacknowledged credential expires in ten minutes even if
                # cleanup cannot reach Strato. Never print a failed payload.
                pass


def connect_in_browser(
    origin: str,
    save: Callable[[str, Callable[[], None]], str],
    announce: Callable[[str], None],
    *,
    open_browser: bool = True,
) -> None:
    client = ApprovalClient(origin)
    try:
        url, code = client.start()
        announce(
            f"Approve Codex in Strato: {url}\nCheck that the approval page shows code {code}. No token copying is needed."
        )
        if open_browser:
            webbrowser.open(url)
        token = client.wait_for_approval()

        def confirm() -> None:
            # The saver rolls back local credentials/config if acknowledgment fails.
            result = client.exchange("complete")
            if result.get("status") != "completed":
                raise SetupError(
                    "Strato could not confirm installation. Start setup again."
                )

        name = save(token, confirm)
    except BaseException:
        client.cancel()
        raise
    announce(
        f"Connection saved as {name}; DHF read access verified. Restart Codex, then list your Strato products in a new chat."
    )
