# Importing a documented baseline

Start with the existing documented requirements and designs. Preserve each identified obligation and its source traceability; grouping the discussion or sharing a design does not combine those requirements.

## Reconcile the source

Inventory every requirement in the selected scope and compare it with current Strato records, implementation, and upstream intent. Use the source document and section to distinguish entries when IDs repeat. Account for each item as new, changed, already present, unresolved, or excluded with a reason. Propose consolidation separately from importing the baseline.

Before import, assess the source against Strato's specification-authoring guidance for style, structure, verifiability, and the boundary between specifications and design. Recommend needed source improvements, including clearer wording, splitting independent obligations, and separating implementation explanations into linked Design Elements. Keep required behavior and supported constraints in specifications; designs explain the mechanisms and rationale.

Use concise noun-phrase titles and verifiable “shall” requirements, preserving the intended meaning and correcting obsolete details where evidence supports the change. Copy each source ID unchanged into `external_reference_id`, without added prefixes or repetition in the title. Keep source citations and import or review status in chat, outside the specification description.

Treat missing traceability separately from unclear requirement wording. Where governance permits, import a usable draft and identify its missing parent or risk links. Keep unresolved items separate so ready work can proceed.

## Recommend or apply the import

If the user asked to assess alignment, recommend the complete import in chat with source and ready counts, corrections, folder placement, and any decisions needed. If they asked to import or selected the recommendation, apply the ready items using [MCP operations](mcp-operations.md) without asking them to select the import again. Editing local documents is separate work.

For interrupted imports, compare current source and Strato records, including pending changes, before continuing. Read back results and reconcile them against the full source inventory to establish what remains.
