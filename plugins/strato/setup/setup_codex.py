# /// script
# requires-python = ">=3.10"
# dependencies = ["keyring==25.7.0", "tomlkit==0.13.3", "truststore==0.10.4", "typer==0.20.0"]
# ///
from __future__ import annotations

import json
import os
import sys
from collections.abc import Callable
from pathlib import Path

import typer
from browser_setup import connect_in_browser
from configuration import executables, install_plugin, save_connection
from credentials import credential_store, read_token
from rich.console import Console
from workspace import SetupError, verify_token, workspace_origin

app = typer.Typer(pretty_exceptions_enable=False)
console = Console(stderr=True)


@app.command()
def connect(
    workspace_url: str = typer.Option(..., help="HTTPS Strato workspace origin."),
    allow_local: bool = typer.Option(
        False, help="Allow HTTPS tenant.stratoware.localhost workspaces."
    ),
    open_browser: bool = typer.Option(
        True,
        "--browser/--no-browser",
        help="Open the approval page, or print its link for the user.",
    ),
) -> None:
    """Install the plugin and approve workspace access in the Strato browser."""
    try:
        origin = workspace_origin(workspace_url, allow_local=allow_local)
        codex, uv = executables()
        credential_store()
        install_plugin(codex)
        home = (
            Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
            .expanduser()
            .resolve()
        )

        def save(token: str, confirm: Callable[[], None]) -> str:
            verify_token(origin, token, allow_local=allow_local)
            return save_connection(home, origin, token, uv, confirm)

        connect_in_browser(origin, save, console.print, open_browser=open_browser)
        console.print(
            "Strato setup completed. Restart Codex and start a new chat to verify its tools."
        )
    except SetupError as exc:
        console.print(str(exc))
        raise typer.Exit(1) from None
    except Exception:
        console.print(
            "Setup failed. Check Codex, your OS credential store, and filesystem permissions. No credentials were printed."
        )
        raise typer.Exit(1) from None


@app.command()
def headers(
    workspace_url: str = typer.Option(...), allow_local: bool = typer.Option(False)
) -> None:
    """Credential protocol for Codex only. Never run this in a chat or terminal."""
    try:
        token = read_token(workspace_origin(workspace_url, allow_local=allow_local))
        sys.stdout.write(json.dumps({"Authorization": f"Bearer {token}"}))
    except Exception:
        console.print(
            "Strato credential unavailable. Unlock your OS credential store or run guided setup again."
        )
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
