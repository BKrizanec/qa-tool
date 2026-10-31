"""Render findings as a plain-language Markdown report, or as JSON for an MCP client."""
from __future__ import annotations

import json
from dataclasses import asdict

from .analysis import Analyzer, Finding

SEVERITY_LABEL = {"high": "🔴 High", "medium": "🟠 Medium", "low": "🟡 Low", "info": "ℹ️ Info"}


def summary(analyzer: Analyzer) -> dict:
    scenarios = sum(len(f.scenarios) for f in analyzer.features)
    return {
        "features": len(analyzer.features),
        "scenarios": scenarios,
        "step_definitions": len(analyzer.stepdefs),
        "page_object_classes": sum(1 for c in analyzer.index.classes.values()
                                   if any(f.locator for f in c.fields.values())),
        "findings": {s: sum(1 for f in analyzer.findings if f.severity == s) for s in SEVERITY_LABEL},
    }


def to_json(analyzer: Analyzer) -> str:
    return json.dumps({"summary": summary(analyzer), "findings": [asdict(f) for f in analyzer.findings]}, indent=2)


def to_markdown(analyzer: Analyzer, title: str) -> str:
    s = summary(analyzer)
    out = [f"# Suite trust audit: {title}", "",
           f"Read **{s['scenarios']} scenarios** in {s['features']} feature files, traced through "
           f"{s['step_definitions']} step definitions and {s['page_object_classes']} page objects.", "",
           "| Severity | Findings |", "|---|---|"]
    out += [f"| {SEVERITY_LABEL[k]} | {v} |" for k, v in s["findings"].items() if v]
    out.append("")

    def block(f: Finding) -> list[str]:
        lines = [f"### {SEVERITY_LABEL[f.severity]}: {f.title}", ""]
        if len(f.occurrences) == 1:
            lines.append(f"*Scenario:* {f.occurrences[0]}  ")
        elif f.occurrences:
            shown = "; ".join(f.occurrences[:4]) + ("; …" if len(f.occurrences) > 4 else "")
            lines.append(f"*Affects {len(f.occurrences)} scenarios:* {shown}  ")
        lines.append(f"*Where:* `{f.location}` · *Check:* `{f.code}`")
        lines.append("")
        lines += [f"- {d}" for d in f.detail]
        lines.append("")
        return lines

    scenario_level = [f for f in analyzer.findings if f.scenario]
    suite_level = [f for f in analyzer.findings if not f.scenario]
    if scenario_level:
        out += ["## What the scenarios claim vs. what they check", ""]
        for f in scenario_level:
            out += block(f)
    if suite_level:
        out += ["## Across the suite", ""]
        for f in suite_level:
            out += block(f)
    return "\n".join(out)
