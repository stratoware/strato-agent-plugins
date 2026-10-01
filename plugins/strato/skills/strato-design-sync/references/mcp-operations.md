# Strato MCP operations

MCP server aliases vary; discover tools by capability/name.

| Capability           | Current tool contract                                                                           |
| -------------------- | ----------------------------------------------------------------------------------------------- |
| Discover product     | `products_list_v1`, no product slug required                                                    |
| Enumerate records    | `items_list_v1`, product slug, optional record types; follow `next_offset` until exhausted      |
| Read records         | `items_get_details_v1`, product slug and bounded `item_ids`; inspect each result's status       |
| List folders         | `folders_list_v1`, product slug and category; omit parent for roots, supply `parent_folder_id` for children |
| Create folders       | `folders_create_v1`, product slug and `creates` entries: category, name, optional `parent_folder_id` |
| Move records         | `items_move_v1`, product slug and `moves` entries: item ID, reviewed `expected_revision`, `target_folder_id` (null for root), and one-based `target_position` |
| Create records       | `items_create_v1`, product slug and `creates` entries: entity type, title, supported fields |
| Update records       | `items_update_v1`, product slug and `updates` entries: entity type, item ID, reviewed `expected_revision`, and changed fields |
| Upload circuit       | `dhf_kicad_upload_v1`, only when advertised and enabled                                         |

All four write tools accept 1–100 entries, including a single change. Keep individual specifications intact when splitting work into batches. Create dependencies first and use their returned IDs in later calls.

Folder tools cover Software, Hardware, and Labeling Specifications, Design Elements, and Test Cases. Batch needed root folders, then children using returned parent IDs. Create records directly in their intended `target_folder_id`. Moves preserve content and links; positions apply after earlier moves in the batch.

Creates and moves are ordered and non-atomic. Inspect every receipt: `created` or `moved` confirms a saved change, `unknown` needs reconciliation, and `not_attempted` was not sent to the write service. Updates are atomic: a stale revision or invalid entry rejects the whole batch. After a timeout or lost response, let the outstanding request settle and reread Strato, including pending changes, before deciding what remains. External reference IDs help matching but do not prevent duplicates.

Architecture and detailed design are ordinary `design_element` records with Markdown descriptions, not separate record types. Software and Hardware Specifications are `software_specification` and `hardware_specification`; mechanical requirements use Hardware Specifications. Classify requirements by what they constrain and the product's conventions, rather than the source file format or repository label.

Specifications expose `implemented_by_design_elements`. Design Elements own `linked_software_specifications` and `linked_hardware_specifications`. Both links may be supplied on Design Element creation and update. A diagram embedded in a description does not itself establish a specification relationship.

For sparse updates, omit untouched fields. Supplied relationship lists are complete replacements for that category, not additions; merge intended additions with the current list. `[]` clears the category. Do not send null to preserve a value. Specification `linked_product_requirements` uses the same replacement semantics.

Other users can also edit governed relationships from their reciprocal endpoint; reread both link categories immediately before a replacement. The record revision alone does not cover changes made through reciprocal endpoints.

Read-only access uses `dhf:records:read`. The `dhf:development:write` scope covers Software, Hardware, and Labeling Specifications, Design Elements and their links, Test Cases, and Test Runs. This does not grant lifecycle acceptance, release, or changes to User Needs, Product Requirements, or risks.

Rich-text reads and writes use Markdown. Preserve fenced Mermaid source. KiCad uploads return immutable artifact identities and insertion Markdown; use those values exactly and preserve tenant/product scope. Artifact references alone do not expose source bytes; use the advertised read/upload tools for each supported format.

A successful governed write may still await human review. Read back records and describe their actual state.
