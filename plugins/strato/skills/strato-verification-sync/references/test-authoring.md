# Test authoring

## Assess quality before import or authoring

Compare existing tests and procedures with the intended behavior in the linked specifications. Recommend improvements before import when checks are incomplete, overly broad, redundant, or coupled to incidental implementation details. Preserve useful checks, including ones whose product traceability still needs clarification.

A Test Case should make its purpose, setup, relevant configuration and conditions, actions, and measurable expected results clear enough for a reviewer to understand what would pass or fail. Put shared fixtures and prerequisites in setup. Include boundary and fault conditions where the specification calls for them. Ask for missing limits or test conditions instead of inventing them.

Group manual and bench procedures by a coherent verification purpose. For automated tests, use the suite/case and leaf/step conventions in [GitHub mapping and results](github-results.md), even when result export is deferred. Keep each check's action and expected result explicit. Procedure details may identify equipment, component models, addresses, or measurements when needed to perform the test; specifications remain focused on required behavior.

## Write Test Cases

Follow [shared MCP operations](../../strato/references/mcp-operations.md). Use `entity_type: test_case` in create or update entries. Supported fields include title, Markdown description/setup steps, protocol rows, and specification links. Use native links for the specifications the case actually verifies.

Preserve unrelated rows and manual procedure content. Read the whole case before replacing `test_steps`. Current MCP step inputs contain `action` and `expected_result`; reads also expose authoritative `step_id` values. Do not send step IDs if the advertised write schema excludes them.

After a protocol change, reread the case revision and all step IDs. Where automation mappings exist, reconcile every affected selector: protocol edits or human review can change step identities. Do not leave a known stale mapping enabled for export. Source review state in a mapping is informational and never authorizes result ingestion.
