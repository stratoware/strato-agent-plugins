---
name: strato-design-sync
description: Reconcile local software, firmware, electrical, and mechanical engineering work with Strato DHF specifications and designs through MCP. Establish or resume a documented baseline, review later changes in both directions, and apply selected resolutions. Use for design alignment, not verification coverage or test execution.
---

# Strato Design Sync

Compare the current project with its Strato product and discuss findings and recommended next steps in chat. Apply changes when selected; an explicit request to reconcile and import a baseline already selects that work.

User Needs explain the why. Product Requirements and Specifications define the what. Design Elements describe the how through design and architecture.

Use functional component names in specifications. Put selected component models and internal details such as register addresses or byte layouts in linked Design Elements when useful. Keep specific interface details in a specification when they express a required compatibility constraint.

Each specification should support a Test Case with a clear pass/fail result. State the required behavior, relevant conditions, and supported acceptance criteria; ask for missing criteria rather than deriving requirements directly from implementation constants.

## Understand the baseline

Discover the connected MCP tools and product, using existing project context where unambiguous. Read [MCP operations](references/mcp-operations.md) when preparing writes.

Within the user's requested scope, identify relevant engineering areas and major subsystems from product intent and all supplied materials, including artifacts outside the repo. Use system overviews and block diagrams to include subsystems whose detailed documentation is missing. Read the applicable Strato User Needs, Product Requirements, specifications, and Design Elements, following pagination. Review the current folder and working changes, and explain any missing or unreadable evidence that limits the comparison.

Use `.strato/sync-history.json`, a JSON list of sync events, to see whether a sync has happened before. Missing or empty history means first sync, but Strato may already contain useful records. Always compare current source and Strato content.

Choose the work from what is present:

- **Local specifications or designs:** assess and reconcile the complete documented baseline with Strato, following [Importing a documented baseline](references/documented-imports.md).
- **Implementation without specifications:** derive candidate specifications and designs from the product's capabilities, taking existing User Needs and Product Requirements into account. Distinguish inferred intent from documented requirements.
- **Little implementation or documentation:** ask focused onboarding questions and draft an initial baseline from existing Strato intent and the answers.
- **An established baseline:** compare both directions for additions, missing implementation, and drift. Use the import procedure for newly documented areas.

These situations can coexist within one product. Reuse existing specifications and designs where they fit.

## Review alignment

Look for:

- User Needs and Product Requirements without adequate specification coverage.
- Specifications with missing or partial implementation.
- Implemented functionality without specifications.
- Specifications without linked, substantive design or architecture.
- Specifications that conflict with current intent or implementation.
- Designs that conflict with the engineering artifacts.

For each relevant engineering area, assess both existing specifications and missing or insufficiently defined requirements revealed by product intent and available design or implementation evidence. Include those gaps in the initial recommendations.

Ask early for missing inputs or design decisions before drafting dependent specifications, including schematics or drawings for subsystems known only from an overview. Continue supported work while identifying those gaps as follow-on tasks.

Match records by meaning as well as IDs and relationships. Distinguish “not found in this folder” from “not implemented.” Code is evidence, not automatic authority over intended behavior; dates alone do not establish staleness.

Discuss the meaningful gaps and useful next steps in chat, linking to relevant evidence. For an initial baseline, recommend the full import or authoring scope, including needed corrections and unresolved decisions. Summarize large inventories by group without replacing individual requirements with capability summaries.

Use compact tables for findings and proposed actions, with Strato IDs or short finding IDs so the user can select rows.

## Apply selected changes

Organize new records into logical folders reflecting the product's major subsystems, reusing existing groupings where appropriate.

Preserve supported meaning, conditions, units, limits, and diagrams while applying selected improvements. Reread affected records, including pending changes, and preserve unrelated content and links. Follow normal Strato governance and resolve uncertain writes before retrying or issuing dependent writes.

Confirm changes by readback and summarize the outcome in chat. Append one event to `.strato/sync-history.json`, preserving previous entries, with a `timestamp` and product-specific `summary` of confirmed changes, including partial progress. Reviews without Strato changes add no event.

For selected implementation or issue-tracker work, use the agreed expected behavior and the project's normal development workflow.
