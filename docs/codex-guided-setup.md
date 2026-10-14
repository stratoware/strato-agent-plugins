# Guided Codex setup

Connect from Strato with Codex 0.160.0 or later on macOS or Linux and an unlocked OS credential store. Codex installs the plugin, handles OAuth, and renews access automatically. No token copying, environment variables, or configuration editing is required. Public-directory registration and hosted OpenAI connections are separate.

## Connect from Strato

1. Open **Profile → Connectors → Open Codex**. The workspace is selected automatically. Send the prepared request in the new Codex chat. If Codex does not open, expand **Codex didn’t open?** and copy the setup request.
2. Codex installs the plugin and opens Strato in your browser. Sign in using your normal Strato account if needed.
3. Check the workspace and signed-in account. Choose **Read and write DHF** (the default) or **Read only**, then approve access. Existing record permissions and lifecycle restrictions still apply.
4. Wait for Codex to finish authorization. Restart Codex if requested to load the newly installed plugin.
5. Ask it to list your Strato products. Strato shows **Authorized** after consent and **Connected** after the first successful tool request.

The Codex card shows permissions, authorization date, expiry, and last successful use. **Disconnect** immediately rejects subsequent tool requests. **Reconnect Codex** requires fresh consent. Disconnect older installations you no longer need.

## Instructions for the setup agent

- Work locally. Read this guide and the helper source first. Preserve the customer's project and unrelated Codex settings.
- Use a separate checkout of `https://github.com/stratoware/strato-agent-plugins` at `stable`. If the Strato request specifies a staging candidate from `https://github.com/stratoware/strato-agent-plugins-dev`, verify the exact requested commit. Staging testers need repository access. Inspect the remote and local changes before reusing a checkout. An explicitly authorized local pilot may use the specified reviewed checkout.
- Locate Codex and `uv`, including the desktop app's bundled CLI if necessary. Help install missing prerequisites from official sources. The agent performs commands on the user's behalf.
- Run `uv run --locked --script plugins/strato/setup/setup_codex.py connect --workspace-url https://YOUR-WORKSPACE.stratoware.io` with the supplied workspace. Keep it running during browser approval.
- Let the user sign in, choose permissions, and approve. Do not approve on their behalf, create manual tokens, or inspect OAuth credentials.
- The helper checks Codex's version and the OS credential store, registers the official marketplace at `stable` if absent, and installs `strato@strato`. An existing official marketplace retains its selected ref; a conflicting marketplace is rejected.
- The helper configures the registered public OAuth client, PKCE resource binding, and `mcp_oauth_credentials_store = "keyring"`, then runs `codex mcp login`. Codex manages credential storage and renewal; the helper never redeems or stores access tokens.
- After successful authorization, explain restart guidance and ask the user to verify a Strato read. Installation alone does not prove a successful tool request.

## Local development and release

The application, signing infrastructure, edge Worker, and installer must be released together. Staging uses a pinned candidate from the private repository. Publish the helper to public `stable` only after the native renewal and security gates pass, before updating the production setup request. There are no customer-facing feature switches.

For local development, use `https://TENANT.stratoware.localhost:PORT` with `--allow-local`. The hostname must resolve only to loopback. Trust the mkcert CA in the OS certificate store and retain HTTPS verification. Set `VITE_STRATO_SETUP_CHECKOUT` in the frontend's ignored `.env.development.local` to the reviewed checkout; production builds ignore this setting. Plugin skills still install from the official repository marketplace.

## Storage and recovery

Codex stores OAuth credentials in macOS Keychain or a supported Linux credential store. The installer rejects plaintext storage or an unavailable store. It removes only Strato-owned legacy helper settings and the matching legacy keyring entry after successful native login. Unrelated TOML settings, comments, and tool approval policies are preserved. New connections prompt for writes. Existing configuration is backed up with owner-only permissions; failed login restores it unless another process changed it meanwhile.

Access tokens expire after ten minutes and are renewed automatically. The connection expires after 90 days and requires fresh consent. Disconnect revokes the connection immediately at Strato, including outstanding access tokens and refresh credentials.

Canceled, denied, or expired approval: start setup again. Locked credential store: unlock it and retry. Plugin policies or GitHub access failures must be resolved before setup. Duplicate endpoints, conflicting names, managed symlinks, and invalid TOML need the reported conflict resolved. If authorization succeeded but local setup failed, disconnect the unused grant in Strato before retrying.

Windows, cloud execution, and Claude connections are not supported by this release. Do not fall back to personal tokens or copy credentials into chat.
