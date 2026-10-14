# /// script
# requires-python = ">=3.10"
# dependencies = ["keyring==25.7.0", "tomlkit==0.13.3", "truststore==0.10.4", "typer==0.20.0"]
# ///
from __future__ import annotations

import os
from pathlib import Path

import typer
from configuration import executables, install_plugin, save_connection
from credentials import check_credential_store
from rich.console import Console
from workspace import SetupError, verify_oauth_server, workspace_origin

app = typer.Typer(pretty_exceptions_enable=False)
console = Console(stderr=True)


@app.callback()
def main() -> None:
    """Install Strato and connect using Codex's native OAuth support."""


@app.command()
def connect(
    workspace_url: str = typer.Option(..., help="HTTPS Strato workspace origin."),
    allow_local: bool = typer.Option(
        False, help="Allow local HTTPS Strato workspaces."
    ),
) -> None:
    """Install the plugin, then sign in and approve access in the browser."""
    try:
        origin = workspace_origin(workspace_url, allow_local=allow_local)
        codex, _uv = executables()
        check_credential_store()
        verify_oauth_server(origin, allow_local=allow_local)
        install_plugin(codex)
        home = (
            Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
            .expanduser()
            .resolve()
        )
        console.print(
            "Codex will open Strato in your browser. Sign in, check the workspace and permissions, and approve access yourself."
        )
        save_connection(home, origin, codex)
        console.print(
            "Authorization saved securely by Codex. Restart Codex and ask it to list your Strato products to verify the connection. Access renews automatically."
        )
    except SetupError as error:
        console.print(str(error))
        raise typer.Exit(1) from None
    except Exception:
        console.print(
            "Setup could not complete. Check Codex, your OS credential store, network access, and filesystem permissions. No credentials were printed."
        )
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
