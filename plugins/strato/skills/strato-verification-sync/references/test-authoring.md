# Test authoring and MCP

`products_list_v1` discovers product slugs; other DHF tools require `product_slug`. Enumerate with `items_list_v1` and follow every `next_offset`; read known IDs with `items_get_details_v1`, checking each result status.

Reuse suitable Test Case folders, grouping new cases by the product's verification strategy or test suites.

Use `items_create_v1` for new Test Cases and `items_update_v1` for existing cases, with `entity_type: test_case` in each entry. Both accept 1–100 entries; updates require the reviewed `expected_revision`. Preserve one case per mapped suite. Supported fields include title, Markdown description/setup steps, protocol rows, and specification links. Omit untouched fields; supplied lists replace their category, and `[]` clears it.

Use `folders_list_v1`, `folders_create_v1`, and `items_move_v1` for folder placement. Batch needed folders before creating cases in their intended `target_folder_id`. Moves require the reviewed revision, destination, and one-based position.

Creates and moves can partially succeed; inspect every receipt and reconcile uncertain outcomes before retrying. Updates are atomic. Read back cases after writes for their authoritative revisions and step IDs.

Each protocol row describes the local test's action and expected result. Shared fixtures belong in setup. Preserve unrelated rows and manual procedure content. Read the whole case before replacing `test_steps`.

Current MCP step inputs contain `action` and `expected_result`; reads also expose authoritative `step_id` values. Do not send step IDs if the advertised write schema excludes them. After any protocol change, reread all step IDs and the case revision and reconcile every mapped selector. Protocol edits or human review can change step identities.

The read scope is `dhf:records:read`. Authoring uses `dhf:development:write`, which includes Test Cases and verification links.

Changes follow normal Strato governance and may await human review. MCP's current read projection does not necessarily expose acceptance state: record it as unknown rather than inferring acceptance from write success. Source review state in a mapping is informational and is never approval to import results.

Test Run writes (`test_suite_launch_runs_v1`, `test_run_update_results_v1`, and `test_run_complete_v1`) are outside this skill; existing results may be read as evidence.
