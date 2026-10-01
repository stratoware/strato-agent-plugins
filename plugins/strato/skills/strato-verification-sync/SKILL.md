---
name: strato-verification-sync
description: Reconcile local tests and procedures with Strato specifications, Test Cases, and available result evidence. Identify coverage gaps, author selected tests and Test Cases, and prepare stable GitHub result mappings. Use for verification alignment and traceability; does not execute tests or write Strato Test Runs.
---

# Strato Verification Sync

Review verification coverage and recommend useful next steps in chat. Apply selected authoring and reporting changes; an explicit authoring request already selects that work.

Use compact tables for findings and proposed actions, with Strato IDs or short finding IDs so the user can select rows.

Test execution belongs to GitHub or humans. This skill does not execute tests or create, update, or complete Strato Test Runs. Static validation of mappings, schemas, and workflow configuration is allowed.

## Review coverage

Discover the connected MCP tools and product, using existing project context where unambiguous. Review local tests, manual procedures, working changes, CI configuration, and available execution evidence alongside Strato specifications, Test Cases, and Test Runs. Follow pagination and account for record revisions when comparing results.

Look for missing or partial coverage, missing specification links, mismatched setup or steps, stale protocols, broken test mappings, and missing or outdated execution evidence. Compare actual assertions with expected behavior. Distinguish observed failures from absent, skipped, unreadable, or inapplicable results, and explain limitations that affect the review.

For XCTest or Swift Testing projects, read [Swift testing guidance](references/swift-testing.md).

## Map tests to Strato

- A class or framework-equivalent suite maps to one Test Case.
- A test function or equivalent leaf test maps to one step.
- Shared fixtures become setup instructions.
- Parameterized executions produce separate results under their mapped step.

Use the nearest containing suite for nested tests and meaningful groupings for ungrouped tests. Resolve ambiguous groupings before exporting results. Step numbering does not imply execution order. Keep manual procedures outside automated mappings.

## Apply selected changes

Read [Test authoring and MCP](references/test-authoring.md) for Test Case changes and [GitHub mapping and results](references/github-results.md) for automation mappings or result export.

Reuse existing cases and preserve unrelated content and links. Keep expected results grounded in specifications rather than weakening them to match current tests. After writes, read back Test Case IDs, revisions, and authoritative step IDs for `.strato/test-mapping.json`. Resolve missing identities or uncertain correspondence before enabling export.

Adapt the project's existing reporter and workflow when selected. Preserve CI failure behavior and partial results. Validate the mapping and result contracts with static checks and synthetic fixtures; GitHub or humans provide execution evidence.

Summarize the outcome and remaining work in chat. After confirmed Strato changes, append one event to the JSON list in `.strato/sync-history.json`, preserving previous entries, with a `timestamp` and product-specific `summary`, including partial progress. Reviews and local-only changes add no event.
