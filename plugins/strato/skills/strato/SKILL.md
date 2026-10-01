---
name: strato
description: Work with Strato DHF records through MCP. Use for requests to find, explain, create, update, or link product requirements, specifications, designs, and other supported records. Follow the user's direction; invoking Strato alone asks what to do.
---

# Strato

Carry out the user's requested Strato work. If invoked without a direction, ask what they want to do.

Use compact tables for findings and proposed actions, with Strato IDs or short finding IDs so the user can select rows.

Discover the connected MCP tools and product, using existing project context where unambiguous. Read the relevant records and follow pagination when enumerating. User Needs explain the why. Product Requirements and Specifications define the what. Design Elements describe the how through design and architecture.

## Make requested changes

Apply explicitly requested changes without asking for the same permission again. Follow Strato governance; submitting a change does not accept or release it.

Read affected records, including pending changes, before writing. Preserve unrelated content and links: supplied relationship lists replace that category. Use revision checks when available.

Use the bulk tools for record creation, updates, folder creation, and moves, including one-entry changes. Respect batch limits and create dependencies first using returned IDs. Inspect every result and reconcile uncertain outcomes before retrying.

Follow Strato's specification-authoring guidance: concise noun-phrase titles and verifiable “shall” requirements. Name components by function and put component selections and internal register or byte layouts in linked designs when useful. Retain details that express required interface or compatibility constraints. Give each specification the behavior, conditions, and supported acceptance criteria needed to write a Test Case; ask for missing criteria.

For imports, copy source IDs unchanged into `external_reference_id`, without added prefixes or repetition in titles. Keep descriptions focused on the requirement and necessary technical context; discuss source citations and import or review status in chat. Use Markdown and Mermaid for designs and discover engineering artifact support from the server.

Organize new records into logical folders, reusing existing groupings where appropriate.

Confirm results by readback and summarize the outcome in chat. Append one event to the JSON list in `.strato/sync-history.json`, preserving previous entries, with a `timestamp` and product-specific `summary` of confirmed Strato changes, including partial progress.

## Sync workflows

For reconciling the repo with Strato specifications and designs, use `strato-design-sync` when installed. For verification coverage and result traceability, use `strato-verification-sync` when installed. Otherwise handle the requested scope with available tools. Verification sync prepares tests and reporting; GitHub or humans execute tests and supply Test Run results.
