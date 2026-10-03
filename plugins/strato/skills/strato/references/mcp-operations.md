# Shared Strato MCP operations

MCP server aliases vary; discover tools by capability/name.

| Capability | Current tool contract |
| --- | --- |
| Discover product | `products_list_v1`, no product slug required |
| Enumerate records | `items_list_v1`, product slug, optional record types; follow `next_offset` until exhausted |
| Read records | `items_get_details_v1`, product slug and bounded `item_ids`; inspect each result's status |
| List folders | `folders_list_v1`, product slug and category; omit parent for roots, supply `parent_folder_id` for children |
| Create folders | `folders_create_v1`, product slug and `creates` entries: category, name, optional `parent_folder_id` |
| Move records | `items_move_v1`, product slug and `moves` entries: item ID, reviewed `expected_revision`, `target_folder_id` (null for root), and one-based `target_position` |
| Create records | `items_create_v1`, product slug and `creates` entries: entity type, title, supported fields |
| Update records | `items_update_v1`, product slug and `updates` entries: entity type, item ID, reviewed `expected_revision`, and changed fields |

## Apply writes

Read affected records, including pending changes, before writing. Preserve unrelated content and links. All four write tools accept 1–100 entries, including a single change. Keep record boundaries intact when splitting work into batches. Create dependencies first and use their returned IDs in later calls.

For imports, preserve source IDs unchanged in `external_reference_id` where applicable, without adding prefixes or repeating them in titles. Keep descriptions focused on the record's engineering content; discuss source citations and import or review status in chat.

Folder tools cover Software, Hardware, and Labeling Specifications, Design Elements, and Test Cases. Batch needed root folders, then children using returned parent IDs. Create records directly in their intended `target_folder_id`. Moves preserve content and links; positions apply after earlier moves in the batch.

Creates and moves are ordered and non-atomic. Inspect every receipt: `created` or `moved` confirms a saved change, `unknown` needs reconciliation, and `not_attempted` was not sent to the write service. Updates are atomic: a stale revision or invalid entry rejects the whole batch. After a timeout or lost response, let the outstanding request settle and reread Strato, including pending changes, before deciding what remains. External reference IDs help matching but do not prevent duplicates.

For sparse updates, omit untouched fields. Supplied relationship lists are complete replacements for that category, not additions; merge intended additions with the current list. `[]` clears the category. Do not send null to preserve a value. Other users can edit governed relationships from reciprocal endpoints; reread both sides before a replacement because a record revision alone does not cover those changes.

Read-only access uses `dhf:records:read`. The `dhf:development:write` scope covers Software, Hardware, and Labeling Specifications, Design Elements and their links, Test Cases, and Test Runs. This does not grant lifecycle acceptance, release, or changes to User Needs, Product Requirements, or risks. Each skill's scope may be narrower than the server permission.

## Confirm and record the outcome

Read back changed records and describe their actual state in chat. A successful governed write may still await human review; do not infer acceptance when it is not exposed.

After confirmed Strato changes, append one event to `.strato/sync-history.json`, preserving previous entries. Each new event contains only `timestamp` and a short, product-specific `summary` of confirmed changes, including partial progress. Questions, decisions, and plans stay in chat, except explicitly selected organizing principles recorded as described in the folder guidance. Reviews and local-only changes add no event.
