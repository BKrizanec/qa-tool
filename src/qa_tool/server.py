"""MCP server exposing the suite trust audit to agents (stdio transport)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from .audit import audit, load
from .audit.analysis import is_check
from .audit.report import to_json, to_markdown

INSTRUCTIONS = """\
Audits legacy Cucumber-JVM + Selenium test suites by reading the code; nothing is executed.

1. Call `audit_suite` on the repository root for a plain-language report of where scenarios claim
   to verify something their code never checks.
2. For any scenario you want to judge yourself (especially INTENT_MISMATCH findings, which rely on
   word matching), call `trace_scenario` and compare each Then step's wording with what its code
   actually checks.

Findings come from static reading, so describe them as "the code shows", not as proven failures.
"""

READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True,
                            open_world_hint=False)

server = MCPServer("qa-tool", instructions=INSTRUCTIONS)


def _repo(repo_path: str) -> Path:
    repo = Path(repo_path).expanduser().resolve()
    if not repo.is_dir():
        raise ToolError(f"Not a directory: {repo}")
    return repo


@server.tool(annotations=READ_ONLY)
def audit_suite(repo_path: str, format: Literal["markdown", "json"] = "markdown") -> str:
    """Audit a Cucumber-JVM suite: trace every Gherkin step through step definitions and page
    objects, and report steps, scenarios and runners that cannot fail or check the wrong thing.

    Args:
        repo_path: Absolute path to the test repository root.
        format: "markdown" for a report a QA lead can read, "json" for findings as data.
    """
    repo = _repo(repo_path)
    analyzer = audit(repo)
    return to_json(analyzer) if format == "json" else to_markdown(analyzer, repo.name)


@server.tool(annotations=READ_ONLY)
def trace_scenario(repo_path: str, scenario: str) -> dict[str, Any]:
    """Show, step by step, what one scenario's code really does: the matched step definition,
    the assertions it reaches (and whether each can fail the test), the actions it performs and a
    plain-language list of what it checks. Use it to judge whether a step verifies its wording.

    Args:
        repo_path: Absolute path to the test repository root.
        scenario: Scenario name, or a case-insensitive part of it.
    """
    repo = _repo(repo_path)
    analyzer = load(repo)
    needle = scenario.casefold()
    matches = [(f, s) for f in analyzer.features for s in f.scenarios if needle in s.name.casefold()]
    exact = [(f, s) for f, s in matches if s.name.casefold() == needle]
    if len(exact) == 1:
        matches = exact
    if len(matches) != 1:
        names = sorted({f"{s.name} ({s.file.relative_to(repo)}:{s.line})" for _, s in matches})
        problem = "No scenario matches" if not matches else "Several scenarios match"
        raise ToolError(f"{problem} {scenario!r}." + (" Candidates: " + "; ".join(names) if names else ""))

    feature, sc = matches[0]
    steps = []
    for step in feature.background + sc.steps:
        t = analyzer.trace(step, sc)
        steps.append({
            "keyword": step.keyword,
            "effective": step.effective,
            "text": step.text,
            "from_background": step.background,
            "location": f"{step.file.relative_to(repo)}:{step.line}",
            "step_definition": t.stepdef and {"method": t.stepdef.short, "location": t.stepdef.location},
            "matching_definitions": len(t.candidates),
            "checks": t.checks,
            "assertions": [{"call": a.call, "kind": a.kind, "location": a.location,
                            "can_fail_test": is_check(a), "via": list(a.via)} for a in t.reach.assertions],
            "actions": sorted(t.reach.actions),
            "uses_step_parameter": t.uses_step_param,
        })
    return {"feature": feature.name, "scenario": sc.name,
            "location": f"{sc.file.relative_to(repo)}:{sc.line}", "steps": steps}


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
