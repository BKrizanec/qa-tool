# qa-tool

An MCP server that tells an agent **what a legacy test suite really verifies**.

It reads a Cucumber-JVM + Selenium suite without running it, traces every Gherkin step through
step definitions, page objects and the project's own helper layer, and reports in plain language
where a scenario *claims* to check something its code never checks: `Then` steps that can't fail,
scenarios that verify nothing, commented-out or empty steps, page objects no test reaches, and
runners that silently skip feature files.

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'
```

Register the server with an MCP client (stdio), e.g. Claude Code:

```bash
claude mcp add qa-tool -- /absolute/path/to/qa-tool/.venv/bin/qa-tool-mcp
```

Or in a client's JSON config:

```json
{ "mcpServers": { "qa-tool": { "command": "/absolute/path/to/qa-tool/.venv/bin/qa-tool-mcp" } } }
```

The same audit runs from the command line: `.venv/bin/qa-tool-audit /path/to/suite [--json] [--out report.md]`.

## Tools

| Tool | Returns |
|---|---|
| `audit_suite(repo_path, format="markdown")` | The trust report (Markdown for people, `json` for findings as data) |
| `trace_scenario(repo_path, scenario)` | Step-by-step evidence for one scenario: matched step definition, assertions reached and whether each can fail the test, actions performed, and what it checks in plain language |

`trace_scenario` exists so the agent's LLM can make the semantic call ("does this check match the
step's wording?") that the audit's word matching only approximates. Both tools are read-only.

## Checks

| Code | Meaning |
|---|---|
| `SCENARIO_VERIFIES_NOTHING` | No step in the scenario can fail it |
| `HOLLOW_THEN` | A `Then` step reaches no real assertion |
| `MISLABELLED_THEN` | A `Then` step performs actions and checks nothing |
| `INTENT_MISMATCH` | A `Then` step checks something unrelated to its wording; notes when the real check is hidden in a `Given`/`When` |
| `ALWAYS_FAILS` | An unconditional `fail(...)` in a step |
| `DISABLED_STEP` / `EMPTY_STEP` | Step body is commented out / empty |
| `IGNORED_PARAM` | A step parameter or Examples column is never used |
| `CHECK_ONLY_ACTION_STEP` | Action wording ("navigate", "click"…) but no action is performed |
| `UNDEFINED_STEP` | No step definition; detects definitions that were commented out |
| `ORPHAN_PAGE_OBJECT` | Page object no scenario reaches |
| `SOFT_ASSERT_RISK` | Shared static soft-assert state; soft failures collected after the status is reported |
| `REUSED_FAILURE_MESSAGE` | Same failure message on different checks |
| `RUNNER_*` / `FEATURES_NEVER_RUN` | `@CucumberOptions` runners with absolute/missing paths, `dryRun`, `strict = false`, features no runner includes |

Waits and sleeps (`wait*`, `sleep*`, `smartWait`) count as synchronisation, not verification.

## Sample reports

Produced against public repositories, in [docs/sample-reports/](docs/sample-reports/):

| Repository | Commit | Findings |
|---|---|---|
| [anhtester/AutomationFrameworkCucumberTestNG](https://github.com/anhtester/AutomationFrameworkCucumberTestNG) | `8005156` | 8 |
| [rahulrathore44/SeleniumCucumber](https://github.com/rahulrathore44/SeleniumCucumber) | `7394ef7` | 9 |
| [naveenanimation20/CucumberSeleniumFramework](https://github.com/naveenanimation20/CucumberSeleniumFramework) | `bf35ec1` | 59 |
| [rajatt95/MasterSeleniumFramework_BDD](https://github.com/rajatt95/MasterSeleniumFramework_BDD) | `589321e` | 1 |

## Development

```bash
.venv/bin/pytest
```

`tests/fixtures/shop-suite` is a small suite with one planted problem per check. The anhtester
regression tests run when `QA_TOOL_FIXTURE` points at a clone of that repository.

## Known limits

- Java + Cucumber-JVM only. C# (SpecFlow/Reqnroll) and JavaScript (Cucumber-JS) are planned.
- Cucumber 7 JUnit Platform suites (`junit-platform.properties`) aren't read for runner scope.
- Call resolution is best effort (no full type inference); lambda-style step definitions
  (`Given("…", () -> …)`) are not indexed.
- Findings come from reading code. Proving one means running the scenario against the app with a
  fault injected; that is not part of this tool.
