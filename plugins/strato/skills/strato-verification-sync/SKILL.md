---
name: strato-verification-sync
description: Reconcile software, firmware, electrical, and mechanical verification with Strato specifications and Test Cases through MCP. Establish a verification baseline, reconcile later changes in both directions, and apply selected test, procedure, or reporting changes. Does not execute tests or write Strato Test Runs.
---

# Strato Verification Sync

Compare the project's verification work with its Strato product. Read and follow the [shared sync workflow](../strato/references/sync-workflow.md) for discovery, the user interview, plan confirmation, and completion.

Specifications define what must be demonstrated. Tests and procedures describe how to demonstrate it; execution evidence records what happened. Keep expected results grounded in requirements rather than treating current assertions or observed results as authority.

Test execution belongs to GitHub or humans. This skill does not execute tests or create, update, or complete Strato Test Runs. Static validation of mappings, schemas, and workflow configuration is allowed.

## Understand the baseline

Within the user's requested scope, identify the relevant product areas and verification methods from Strato intent, system overviews, and supplied engineering materials, including artifacts outside the repo. Software tests alone do not establish coverage of hardware or mechanical requirements. Include relevant manual and bench procedures, and ask for missing inputs such as equipment, operating conditions, or acceptance criteria.

Read the applicable Strato Product Requirements, specifications, relevant designs, Test Cases, and available Test Run evidence. Review local tests and procedures, CI configuration, and existing execution evidence alongside them.

For XCTest or Swift Testing work, read [Swift testing guidance](references/swift-testing.md).

Choose the work from what is present; these situations can coexist:

- **Existing tests or procedures:** assess the complete baseline against specifications and [Test authoring](references/test-authoring.md), then propose improvements and reconciliation with Strato. Preserve individual checks and their traceability when summarizing the plan by group.
- **Specifications without adequate tests:** propose Test Cases and, where useful, local tests or procedures that demonstrate the required behavior across relevant product areas.
- **Unclear intent or acceptance criteria:** work through focused questions with the user and identify specification changes needed before dependent tests can be defined.
- **An established verification baseline:** compare both directions for additions, missing counterparts, and drift. Assess newly discovered tests or procedures before importing them.

Propose a coherent Test Case structure using [Folder organization](../strato/references/folder-organization.md). Choose a consistent organizing principle from the product's verification strategy and review needs, including areas whose evidence is incomplete. Existing case placement or the most developed local test suite should not dictate the whole product's organization. Improve and move existing cases where justified, preserving supported intent and traceability.

## Review alignment

Look for:

- Specifications with missing or partial verification coverage.
- Local tests or procedures missing from Strato, and Strato cases missing a local counterpart where one is intended.
- Missing or incorrect specification links, and checks that do not demonstrate the linked requirement.
- Mismatched setup, actions, or expected results; outdated protocols and ambiguous acceptance criteria.
- Broken automation mappings, renamed tests, or changed case revisions and step identities.
- Missing or outdated execution evidence, separately from observed failures.

Match by meaning as well as IDs. Assess actual assertions, procedure steps, and expected results; a link alone does not establish coverage. Account for the tested commit, case revision, configuration, and conditions when judging evidence. Distinguish absent, skipped, unreadable, or inapplicable results from failure, and “not found here” from “does not exist.”

Use the shared interview and planning flow to resolve these gaps before dependent writes. Route unclear requirements or missing design intent to design reconciliation rather than inventing acceptance criteria or weakening them to match current tests.

## Apply selected changes

Read [shared MCP operations](../strato/references/mcp-operations.md) and [Test authoring](references/test-authoring.md) before Test Case writes. Apply the agreed case and folder changes, native specification links, and selected local test or procedure changes.

Automation mappings and GitHub reporting are optional. Read [GitHub mapping and results](references/github-results.md) when they are selected or when case changes affect existing mappings. Maintain those mappings against authoritative case revisions and step IDs before result export. Manual-only work needs no mapping file.

Adapt the project's existing reporter and workflow when selected, preserving CI failure behavior and available results from failed runs. Validate contracts with static checks and synthetic fixtures; GitHub or humans provide execution evidence.

## Close the loop

Distinguish authored Test Cases from adequate coverage and from passing execution evidence. Cases need substantive setup, actions, and expected results; their presence alone does not close a coverage gap. Summarize remaining coverage, authoring, and evidence gaps in chat and recommend the next useful pass within the shared workflow.
