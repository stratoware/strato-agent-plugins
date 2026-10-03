# Release notes

## 0.2.4

- Guide both sync skills through focused questions in chat, a proposed update plan, and confirmation before applying it. Include improvements to existing Strato records and logical folder structure when establishing a baseline.
- Establish or reconcile verification coverage across software, firmware, electrical, and mechanical work. Assess existing tests and manual or bench procedures before import and propose improvements to Test Cases and their organization.
- Keep automation mapping and GitHub reporting optional while maintaining existing mappings affected by case changes. Verification sync does not execute tests or write Test Runs; mapping and result schemas remain version 1.
- Keep questions, decisions, and plans in chat. Limit sync history events to a timestamp and short summary of confirmed Strato changes, and retain selected organizing principles separately as project preferences.
- Share sync workflow, MCP write, import field, and history guidance across the skills to keep their behavior consistent.

## 0.2.3

- Publish the plugin through a public repository containing release snapshots, with development history maintained separately.
- Add support and contribution guidance, private security reporting, and public installation instructions.
- License the distributed plugin under MIT, including a license copy in the installable package.
- Keep the three skills and verification schemas unchanged from 0.2.2.

## 0.2.2

- Include missing or insufficiently defined requirements in the initial design-sync recommendations for each relevant engineering area, using product intent and all supplied materials, including artifacts outside the repo.
- Write specifications in functional, testable terms, keeping component selections and internal implementation details in designs. Use system overviews to inform subsystem coverage and logical folders, and ask for missing subsystem evidence as follow-on work.
- Configure automatic approval for Strato tool calls in the Codex and Claude Code setup guides, including instructions for existing connections.

## 0.2.1

- Add a general `strato` skill for directed DHF lookups and edits, with the two sync skills available for systematic workflows. Invoking it without a direction asks what to do.
- Rename `strato-design-review` to `strato-design-sync` and `strato-verification-review` to `strato-verification-sync`. The review names are reserved for future report workflows. For manually copied installations, replace the old skill folders with the renamed folders.
- Give design and verification findings and recommendations directly in chat, preparing detailed changes when selected.
- Summarize confirmed Strato changes in one timestamped `.strato/sync-history.json` entry after selected work. Empty history means first sync; every review compares current repo and Strato evidence.
- Simplify all three skills and their references in plain English, retaining Strato-specific import and verification contracts. Present findings and proposed actions in compact tables with Strato IDs or short finding IDs.
- Use concise specification titles and preserve source IDs unchanged in the external-reference field. Keep descriptions focused on requirements and necessary technical context; discuss source citations and import or review status in chat.
- Assess upstream specification coverage across relevant engineering disciplines, including areas without local implementation artifacts. Ask for missing engineering inputs before drafting specifications that depend on them, continuing supported work while waiting. Classify requirements by their subject and product conventions.
- Assess documented specifications against Strato authoring guidance before import and recommend improvements to wording, structure, and separation from design. User Needs explain why, requirements and specifications define what, and design and architecture explain how.
- Document the `dhf:development:write` permission for software, hardware (including mechanical), labeling, design, and verification records.
- Use MCP folder listing, creation, and revision-checked record moves for specifications, designs, and Test Cases. Follow existing product or source groupings without prescribing a fixed taxonomy or requiring a separate manual folder-setup step.
- Use bulk tools for record creation, updates, folder creation, and moves, including individual changes. Create dependencies first, place records directly in their folders, and reconcile uncertain outcomes before retrying.
- Preserve individually identified local requirements during documented-baseline imports. Count and disposition every source item, use document and section context to distinguish repeated source IDs, and distinguish batch summaries from actual record boundaries.
- Reconcile code drift and missing parent links per item; apply explicitly authorized imports without repeat selection and read back the results. Resume interrupted imports by comparing source documents with current Strato records. Proposed consolidation requires separate selection.
- Add synthetic scenarios for large SRS imports, duplicate identifiers, and interrupted application. Package checks do not establish agent behavioral conformance.

## 0.2.0

- Route design reviews through documented-baseline import, focused onboarding, implementation-derived baseline authoring, or two-way reconciliation of existing specifications.
- Require upstream intent, capability coverage, semantic ID reconciliation, and concrete specification/design drafts before action selection. Isolate blocked decisions and propose selected implementation or issue-tracker work without automatically changing product records.
- Mapping/result schemas remain version 1. Verification skill behavior is unchanged.

## 0.1.1

- Add shared XCTest and Swift Testing guidance for coverage reviews, suite/step mappings, parameterized tests, and Xcode/Swift Package Manager result reporting. This provides authoring guidance, not a bundled or runtime-validated Swift exporter; mapping/result schemas remain version 1.
- Simplify the overview and provide matching Codex and Claude Code guides for installation, connection, first review, updates, and troubleshooting.
- Clarify first-time Strato MCP setup, with screenshots of the connection settings and token permissions from the local demo interface.

## 0.1.0

Initial private release prepared for testing:

- Design review for software, firmware, electrical, and mechanical engineering evidence.
- Verification coverage review and selected test/Test Case authoring without test execution or Test Run writes.
- Version 1 test mapping and GitHub result schemas, examples, and a static validator.
- Existing Strato MCP connection support, including capability discovery.

GitHub result ingestion is not included. This package requires a separately configured Strato MCP connection. Hardware writes and revision-checked design-link updates require the corresponding Strato server capabilities. Installed-client smoke tests remain outstanding, including Claude Code runtime testing.
