---
name: strato-design-sync
description: Reconcile local software, firmware, electrical, and mechanical engineering work with Strato DHF specifications and designs through MCP. Establish or resume a documented baseline, review later changes in both directions, and apply selected resolutions. Use for design alignment, not verification coverage or test execution.
---

# Strato Design Sync

Compare the current project with its Strato product. Read and follow the [shared sync workflow](../strato/references/sync-workflow.md) for discovery, the user interview, plan confirmation, and completion.

User Needs explain the why. Product Requirements and Specifications define the what. Design Elements describe the how through design and architecture.

Use functional component names in specifications. Put selected component models and internal details such as register addresses or byte layouts in linked Design Elements when useful. Keep specific interface details in a specification when they express a required compatibility constraint.

Each specification should support a Test Case with a clear pass/fail result. State the required behavior, relevant conditions, and supported acceptance criteria; ask for missing criteria rather than deriving requirements directly from implementation constants.

## Understand the baseline

Within the user's requested scope, identify relevant engineering areas and major subsystems from product intent and all supplied materials, including artifacts outside the repo. Use system overviews and block diagrams to include subsystems whose detailed documentation is missing. Read the applicable Strato User Needs, Product Requirements, specifications, and Design Elements. Ask for missing engineering inputs where needed, including subsystem schematics or drawings.

Choose the work from what is present:

- **Local specifications or designs:** assess and reconcile the complete documented baseline with Strato, following [Importing a documented baseline](references/documented-imports.md).
- **Implementation without specifications:** derive candidate specifications and designs from the product's capabilities, taking existing User Needs and Product Requirements into account. Distinguish inferred intent from documented requirements.
- **Little implementation or documentation:** ask focused onboarding questions and draft an initial baseline from existing Strato intent and the answers.
- **An established baseline:** compare both directions for additions, missing implementation, and drift. Use the import procedure for newly documented areas.

These situations can coexist within one product.

Choose a consistent organizing principle from the product's overall architecture and review needs, following [Folder organization](../strato/references/folder-organization.md). Include known parts whose specifications are still incomplete, and propose moves of existing records where needed. Existing coverage should not determine the product's organization; avoid mixing functions, assemblies, and shared constraints as undifferentiated siblings.

Assess existing records for clarity, testability, and the separation of requirements from design when proposing improvements.

## Review alignment

Look for:

- User Needs and Product Requirements without adequate specification coverage.
- Specifications with missing or partial implementation.
- Implemented functionality without specifications.
- Specifications without linked, substantive design or architecture.
- Specifications that conflict with current intent or implementation.
- Designs that conflict with the engineering artifacts.

For each relevant engineering area, assess both existing specifications and missing or insufficiently defined requirements revealed by product intent and available design or implementation evidence. Include those gaps in the initial recommendations.

Match records by meaning as well as IDs and relationships. Distinguish “not found in this folder” from “not implemented.” Code is evidence, not automatic authority over intended behavior; dates alone do not establish staleness.

Discuss meaningful gaps with evidence and recommendations, including the full baseline scope on first sync. Grouped summaries should not replace individual requirements with capability summaries.

## Apply selected changes

Read [shared MCP operations](../strato/references/mcp-operations.md) and [design record guidance](references/mcp-operations.md) before writing. Apply the agreed folder plan and preserve supported meaning, conditions, units, limits, and diagrams while making selected improvements.

For selected implementation or issue-tracker work, use the agreed expected behavior and the project's normal development workflow.

## Close the loop and recommend the next pass

Assess the relevant product areas for grounded specifications, explanatory designs, native relationships, and unresolved decisions. Imported titles alone do not provide substantive coverage.

Where Test Case coverage remains unassessed or incomplete, recommend a verification-sync pass with a defined scope. Do not claim verification completeness from design links or create Test Cases under this skill's authority.
