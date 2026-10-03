---
name: strato
description: Work with Strato DHF records through MCP. Use for requests to find, explain, create, update, or link product requirements, specifications, designs, and other supported records. Follow the user's direction; invoking Strato alone asks what to do.
---

# Strato

Carry out the user's requested Strato work. If invoked without a direction, ask what they want to do.

Use compact tables for findings and proposed actions, with Strato IDs or short finding IDs so the user can select rows.

Discover the connected MCP tools and product, using existing project context where unambiguous. Read the relevant records and follow pagination when enumerating. User Needs explain the why. Product Requirements and Specifications define the what. Design Elements describe the how through design and architecture.

## Make requested changes

Apply explicitly requested changes without asking for the same permission again. Read and follow [MCP operations](references/mcp-operations.md) for bulk writes, preservation of unrelated content and links, revision checks, governance, and recording confirmed changes.

Follow Strato's specification-authoring guidance: concise noun-phrase titles and verifiable “shall” requirements. Name components by function and put component selections and internal register or byte layouts in linked designs when useful. Retain details that express required interface or compatibility constraints. Give each specification the behavior, conditions, and supported acceptance criteria needed to write a Test Case; ask for missing criteria.

Use Markdown and Mermaid for designs and discover engineering artifact support from the server.

Before creating or moving folders, read [Folder organization](references/folder-organization.md). Reuse suitable existing groupings and resolve overlapping taxonomies before adding another branch.

## Sync workflows

For reconciling the repo with Strato specifications and designs, use `strato-design-sync` when installed. For verification coverage and result traceability, use `strato-verification-sync` when installed. Otherwise handle the requested scope with available tools. Verification sync prepares tests and reporting; GitHub or humans execute tests and supply Test Run results.
