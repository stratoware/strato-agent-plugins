# Set up Strato in Claude

Connect your workspace from **Strato → Settings → Connectors → Claude**, then install the Strato plugin from its repository marketplace. If your connector is already authorized, keep that connection.

1. Open [Claude's Plugins](https://claude.ai/customize/plugins) and choose **Add → Add marketplace**.
2. Paste `https://github.com/stratoware/strato-agent-plugins` and select **Sync**.
3. Open **Strato** from that marketplace and add it.

This installs all three skills together: Strato, Strato Design Sync, and Strato Verification Sync. Your Claude plan and organization must permit repository marketplaces.

Enable Strato in a new Claude conversation and ask: “List my Strato products.” Strato's connection status becomes **Connected** after authenticated tool use. Strato cannot detect installed plugins; check that Strato is enabled in Claude's Plugins.

For design and verification sync, provide project files in Claude or select your project folder in Cowork. See [plugin updates](plugin-distribution.md#claude-web-and-cowork) for ongoing maintenance and [Claude's plugin instructions](https://support.claude.com/en/articles/13837440-use-plugins-in-claude) for client controls.
