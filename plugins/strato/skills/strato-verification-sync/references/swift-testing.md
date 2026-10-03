# Swift testing

Use this reference for XCTest, Swift Testing, or projects using both. When automation mapping or reporting is selected, apply the shared [mapping and result contract](github-results.md); the existing schemas need no Swift-specific extension.

## Identify the test surface

Inspect `Package.swift`, test targets and sources, Xcode projects/workspaces, shared schemes, `.xctestplan` files, and CI configuration. Identify the toolchain and the targets, configurations, and destinations selected by CI. Source presence alone does not establish that the selected job includes a test.

- Recognize XCTest classes/methods and Swift Testing `@Test` functions. A Swift Testing suite is a containing type; `@Suite` is optional. Include nested suites and tests declared in extensions.
- Keep mixed frameworks distinct. Use consistent mapping framework names such as `xctest` and `swift-testing`; the invoking command (`swift test` or `xcodebuild`) is not the framework identity.
- Inspect XCTest setup/teardown and Swift Testing initializers, helpers, and scoping traits used by the installed version. Describe fixture lifecycle accurately; a shared helper does not establish shared mutable state or execution order.
- Compare assertions, thrown-error expectations, async expectations/confirmations, and applicable performance thresholds with Strato's expected results.

Use source, existing discovery output, native artifacts, and tool help. Test discovery that builds or loads the product belongs in CI, not this review.

## Map suites and leaf tests

Use the nearest containing suite for each leaf. For free functions, use a meaningful grouping and resolve ambiguity before exporting results. Do not create a Test Case for an entire test target merely because the runner also calls it a suite.

| Source construct | Strato mapping |
| --- | --- |
| `final class AlarmTests: XCTestCase` | One Test Case for this class |
| `func testRejectsInvalidLimit()` in that class | One step |
| `struct LimitTests` containing `@Test` functions | One Test Case, even without `@Suite` |
| `@Test(arguments: [0, 100]) func accepts(limit: Int)` | One step, with separate results for the two arguments |
| A loop or multiple assertions inside a test function | Still one step unless the framework exposes distinct leaf tests |

Selectors must retain the target/module and nested suite/function identity exposed by the actual runner. Preserve argument labels or other disambiguators where required. A display name supplied to `@Test` or `@Suite`, source line number, or formatted console label is not a stable selector. Do not assume XCTest, Swift Testing, Xcode, and SwiftPM use interchangeable identifier syntax.

Record any adapter translation between native identifiers and mapping selectors, and validate it against existing discovery/results. Reconcile renamed tests and XCTest-to-Swift-Testing migrations explicitly against the existing case and protocol; do not silently create duplicates or reuse steps based on similar display names.

For parameterized tests, preserve native argument identities and serializable values without deriving identity from completion order. Equal display strings do not prove equal arguments. If the report loses required parameter identities, mark collection incomplete and leave the affected export unresolved. Do not evaluate dynamic argument providers during review or infer parameter counts from the number of source expressions.

## Read existing results and prepare CI reporting

### Xcode

Prefer retained `.xcresult` bundles and structured data from the matching Xcode tools. Inspect the installed command help before choosing an extraction format. For versions that expose these commands, examples of read-only extraction are:

```bash
xcrun xcresulttool help get test-results
xcrun xcresulttool get test-results summary --path artifacts/Tests.xcresult
xcrun xcresulttool get test-results tests --path artifacts/Tests.xcresult
```

Use per-test details and attachments where required to distinguish parameter instances, retries, failures, and fixture errors; summary counts alone cannot establish step outcomes. Retain the bundle and diagnostic references with the normalized artifact. When the bundle or compatible tooling is unavailable, report that limitation and prepare extraction in the customer's macOS CI job if selected.

Keep destinations and test-plan configurations distinct. If one job tests several destinations/configurations, emit separate result artifacts with explicit `workflow.matrix` context for each rather than merging their observations into one apparent pass. Preserve repetitions and retry identities within each context.

### Swift Package Manager

Inspect the pinned toolchain's `swift test --help` and existing reporter configuration. Where supported, `--xunit-output` can request XML output from the existing CI test command.

Check the actual files produced for both frameworks. SwiftPM versions can emit separate XCTest and Swift Testing reports, and output availability/naming can depend on options and toolchain version. Inspect existing samples for leaf identities, parameters, retries, and diagnostics before selecting an adapter. If XML is lossy, retain additional native evidence or report the gap rather than inventing missing details.

For either runner, follow the shared workflow rules for retaining failed/partial output and preserving the original CI exit status. A build failure, process crash, cancellation, or empty report does not establish that all mapped tests failed or passed. Record known observations and the collection limitation separately.

## Swift outcome interpretation and validation

- Preserve skip/disable reasons and known-issue information, including `XCTExpectFailure` and `withKnownIssue`. Apply the shared expected-failure policy; a runner's green summary is insufficient to claim the affected verification step passed.
- Preserve native assertion failures, unexpected errors, and fixture failures. Do not guess a more specific failure category when the report cannot distinguish them.
- Do not infer execution order from source order, Strato step numbers, or a suite's serialization setting.

Before enabling a selected exporter, validate it with captured or synthetic native reports for the actual toolchain: both frameworks, nested/ungrouped tests, parameterization, duplicate display names, renamed selectors, known issues, skips, retries, and truncated/missing output. Check target/destination separation in the adapter and current Test Case revisions through MCP; the shared validator checks artifact/mapping consistency only. Synthetic fixtures validate conversion only; GitHub or humans must establish actual execution evidence.

## Toolchain references

- [Swift Testing suite organization](https://docs.swift.org/latest/documentation/testing/organizingtests/) and [parameterized tests](https://docs.swift.org/latest/documentation/testing/parameterizedtesting/).
- [Migrating XCTest tests and known issues](https://docs.swift.org/latest/documentation/testing/migratingfromxctest/).
- [Apple's xcresulttool changes](https://developer.apple.com/documentation/xcode-release-notes/xcode-16_3-release-notes); installed command help defines the available interface.
- [SwiftPM test command reference](https://github.com/swiftlang/swift-package-manager/blob/main/Sources/PackageManagerDocs/Documentation.docc/SwiftTest.md); consult the matching toolchain version before configuring output.
