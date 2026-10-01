# GitHub mapping and result artifacts

Use the customer's existing test framework, reporter, and native reports to implement this Strato artifact contract.

## Mapping

Use [test-mapping.schema.json](../assets/test-mapping.schema.json) for `.strato/test-mapping.json`. The [mapping example](../assets/test-mapping.example.json) is synthetic; replace all sample identities with actual returned values.

- `schema_version` identifies the contract; `mapping_revision` increases whenever selectors, protocol revisions, or mappings change.
- `strato` identifies the tenant origin and product. `repository` is the GitHub owner/repository identity, including an enterprise hostname where needed.
- Each case binds one framework suite/class and repository-relative source path to a Strato Test Case and exact revision. Each leaf selector binds to its returned step ID.
- Preserve `review_state: unknown` unless acceptance or proposal status is actually available. This informational value never authorizes acceptance or result ingestion.
- Suite identities must be unique within framework/repository; case identities must not be mapped to competing suites. Each leaf selector and step ID must be unique within its case. No two mappings may claim the same discovered test execution.
- Parameters and retry attempts are execution identities, not additional Strato step IDs. Renamed tests or rewritten protocols require explicit reconciliation, not fuzzy result reassignment.
- Manual-only cases have no automation mapping. Automated portions of mixed cases may be mapped, but the resulting artifact must not imply that manual steps passed.

Before enabling an exporter, verify every case revision and step ID against a fresh MCP read, compare actions/expected results with the source tests, and check selectors against static framework discovery conventions or existing discovery output. If identities cannot be established without running tests, leave that mapping unresolved for GitHub/humans to validate.

## Result contract

Emit [test-results.schema.json](../assets/test-results.schema.json) as `strato-test-results.json` for each GitHub job/matrix instance. See the [result example](../assets/test-results.example.json).

Compute `mapping_sha256` from the exact mapping bytes checked out for the run, and upload those bytes alongside the native test reports. Include `mapping_revision`, tenant/product, repository, the commit actually checked out/tested (including PR merge commits), run ID/attempt, job, and matrix values. Do not obtain a newer mapping after tests execute.

Each observation includes the mapped case revision and step ID, framework/suite/test selectors, unique execution ID, parameter values, retry attempt, native outcome, normalized outcome, duration in milliseconds when known, and references to retained diagnostics. Diagnostic references identify files within the artifact or accessible workflow evidence, not local machine paths.

Normalize observed outcomes to `passed`, `failed`, `errored`, `skipped`, `not_run`, or `unknown`. Preserve native values:

- A native assertion failure is `failed`; setup/teardown errors are `errored`.
- A native skip is `skipped`, never passed. Expected failures and unexpected passes remain explicit in native outcomes; use `unknown` unless project policy defines their verification interpretation.
- Keep every retry attempt. A later pass must not hide earlier failed observations.
- `not_run` requires evidence that a known execution was not run. Unexplained absence is `unknown`; missing reports or unresolved discovery make collection `partial` or `unavailable`.
- Do not invent durations; use null when unavailable. Do not synthesize a native outcome for an unobserved execution.

Reconcile output against the run's known test selection. Report unmapped executions, missing mapped tests, stale selectors, missing parameter instances, and missing jobs/shards in collection notes. `complete` describes collection within this job's declared selection, not overall product verification. A valid empty array is not proof of success. Preserve partial output on parser or test failures and mark its collection status accordingly.

The artifact contains observations, not a Strato verdict or Test Run completion. Strato result ingestion is outside this workflow.

## Workflow changes

Prefer native metadata carrying case/step identity when reliable; retain the sidecar mapping as the authoritative binding. Otherwise adapt native report output using exact framework identities, not display-title substring matching.

Collect and upload artifacts after failing test steps using the workflow's existing supported mechanism. Keep the original test exit status and job failure intact; do not make CI green through `continue-on-error` or shell pipelines. Keep artifact names distinct for matrix jobs, shards, and attempts. A human-readable workflow summary may link to artifacts but is not the import contract.

Validate schemas, mapping uniqueness, result-to-mapping references, and adapter handling with synthetic native-report fixtures. Leave execution to GitHub or humans.

## Static contract validation

Run the bundled validator without executing any product tests:

```bash
uv run <skill-directory>/scripts/validate_verification.py .strato/test-mapping.json --results strato-test-results.json
```

Omit `--results` to validate only a mapping. The script checks schema shape, unique mappings, repository-relative paths, exact mapping hash, result-to-step references, and duplicate attempts. It cannot prove selector existence, completeness of parameter discovery, Strato acceptance, or engineering coverage; assess those separately as described above.
