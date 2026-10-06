# Guided Codex setup

Install the repository plugin and approve Strato access in your browser. No token copying, environment variables, or configuration editing is required. This flow supports local Codex on macOS and Linux with an unlocked OS credential store. Public-directory registration and hosted OAuth are separate. Windows and remote/cloud execution use the [manual guide](codex.md).

## Connect from Strato

1. Open **Profile → Connectors → Set up Codex**. The current workspace is selected automatically. Send the prepared request in the new Codex chat. If Codex does not open, expand **Codex didn’t open?** and copy the setup request.
2. Codex installs the plugin and opens Strato's approval page. Sign in using your normal Strato account if needed.
3. Check that the approval code matches the code in the setup chat. Select **Read and write DHF** (the default) or **Read only**, confirm that you started setup, and select **Approve access**. Existing record permissions and lifecycle restrictions still apply.
4. Wait for **Connection saved and DHF read access verified**. The installer retrieves the credential directly and stores it securely on your computer.
5. Restart Codex and ask it to list your Strato products in a new chat. This confirms the restarted Codex client can use the connection.

Manage permissions and expiry on the Codex card. **Disconnect** immediately revokes access for subsequent requests. **Reconnect Codex** starts a fresh approval. Disconnect any older installation you no longer need. The advanced section is only for manual integrations.

## Instructions for the setup agent

- Work locally. Read this guide and the helper source first. Preserve the customer's project and unrelated Codex settings.
- Use a separate checkout of `https://github.com/stratoware/strato-agent-plugins` at `stable`. If the Strato setup request specifies a staging candidate from `https://github.com/stratoware/strato-agent-plugins-dev`, use that private repository and verify the checkout matches the exact requested commit. Staging testers need access to that repository. Inspect the remote and local changes before reusing a checkout. For an explicitly authorized unpublished local pilot, use the specified reviewed checkout.
- Locate Codex and `uv`, including the desktop app's bundled CLI if necessary. Help install missing prerequisites from official sources. The agent performs terminal commands on the user's behalf.
- Run `uv run --locked --script plugins/strato/setup/setup_codex.py connect --workspace-url https://YOUR-WORKSPACE.stratoware.io` with the actual workspace. Keep it running while the user approves access. Show the helper's approval code and link; neither can retrieve a credential.
- Let the user sign in, compare the code, choose permissions, and approve. Do not approve on their behalf. Do not create a manual token or fall back to token copying if browser approval fails.
- Never execute the `headers` subcommand for debugging: its stdout is the credential protocol consumed by Codex. Never expose credentials or raw server payloads in chat, screenshots, files, or logs.
- The helper checks credential-helper support, registers the official `stable` marketplace if absent, and installs `strato@strato`. An existing official marketplace keeps its chosen ref; a conflicting marketplace is rejected.
- After successful setup, explain the restart and new-chat verification. The helper verifies a DHF read; it cannot prove that a restarted Codex client has connected.

## Local development and release

The backend requires the additive MCP setup migration. Guided setup is available whenever the updated application is deployed; there are no guided-setup feature switches. Staging can use an exact candidate commit from the private development repository before public release. Publish the helper on public `stable` after the staging pilot passes and before promoting the application to production.

For local development, use `https://TENANT.stratoware.localhost:PORT` with `--allow-local`, using the stack's HTTPS proxy port. The hostname must resolve only to loopback. The mkcert CA must already be trusted in the OS certificate store. Keep HTTPS verification enabled; HTTP, remote local-host resolutions, arbitrary hosts, and redirects are rejected.

Set `VITE_STRATO_SETUP_CHECKOUT` in the frontend's ignored `.env.development.local` to the reviewed plugin checkout's absolute host path. Restart Vite if needed. Production builds ignore this override and reject local workspace origins. The plugin skills still install from the official repository marketplace.

Credentials are keyed by the full workspace origin, including its local port. Multiple worktrees can coexist with hosted connections. Approval uses the local tenant's existing sign-in and only grants access to that tenant.

## Storage and recovery

The installer generates a random proof and sends only its S256 challenge when starting setup. The approval link contains a request identifier, not a credential. Approval is bound to the signed-in tenant/user and an HttpOnly browser cookie, requires a matching request origin, and expires after ten minutes. Only the initiating installer can redeem the approved request, once. No localhost callback server is needed.

Strato stores only hashed credentials. Redemption and issuance commit atomically. An issued credential initially lasts ten minutes; after a successful MCP read and durable local save, the installer acknowledges completion and Strato extends it to 90 days from issuance. A failed installation cancels the new grant and restores the previous local credentials/configuration. An abandoned, unacknowledged credential expires after ten minutes even if cleanup cannot reach Strato.

The credential goes into macOS Keychain or Linux Secret Service under `io.stratoware.codex`, keyed by workspace URL. Plaintext and unknown keyring backends are rejected. The helper copies itself and its locked dependencies to `$CODEX_HOME/strato-setup` (normally `~/.codex/strato-setup`). Codex calls it to obtain the Authorization header.

Unrelated TOML settings and comments are preserved. Setup reuses the matching endpoint, retains its existing tool approval policy, and uses **prompt for writes** for new entries. The first existing configuration is backed up to `config.toml.strato-backup` with owner-only permissions. Verification lists products without changing DHF records.

Canceled or expired approval: start setup again. Locked credential store: unlock it and retry. Unavailable browser approval: update the backend and helper; do not ask the user to create a token. Plugin policy restrictions or GitHub access failures must be resolved before setup. Duplicate endpoint entries, conflicting server names, managed symlinks, or invalid TOML require resolving the reported conflict.

Connections expire after 90 days and require fresh approval; this local flow does not refresh them automatically. Removing local configuration alone does not revoke access. Use **Disconnect** in Strato, then optionally remove the server in Codex Settings and its entry from the OS credential manager.
