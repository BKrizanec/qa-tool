"""Minimal Gherkin parser: features, backgrounds, scenarios (outlines), steps, examples."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

STEP_KEYWORDS = ("Given", "When", "Then", "And", "But", "*")


@dataclass
class Step:
    keyword: str            # as written
    effective: str          # Given/When/Then after resolving And/But
    text: str
    file: Path
    line: int
    background: bool = False


@dataclass
class Scenario:
    name: str
    file: Path
    line: int
    steps: list[Step] = field(default_factory=list)
    examples: list[dict[str, str]] = field(default_factory=list)  # rows
    is_outline: bool = False


@dataclass
class Feature:
    name: str
    file: Path
    background: list[Step] = field(default_factory=list)
    scenarios: list[Scenario] = field(default_factory=list)


def _row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_feature(path: Path) -> Feature:
    feature = Feature(name=path.stem, file=path)
    section: str | None = None        # "background" | "scenario"
    current: Scenario | None = None
    last_effective = "Given"
    header: list[str] | None = None
    in_examples = False
    in_docstring = False

    for lineno, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        line = raw.strip()
        if line.startswith(('"""', "```")):
            in_docstring = not in_docstring
            continue
        if in_docstring or not line or line.startswith("#") or line.startswith("@"):
            continue
        if line.startswith("Feature:"):
            feature.name = line.split(":", 1)[1].strip()
            continue
        if line.startswith("Background:"):
            section, current, in_examples, last_effective = "background", None, False, "Given"
            continue
        m = re.match(r"(Scenario Outline|Scenario Template|Scenario|Example):(.*)", line)
        if m:
            current = Scenario(name=m.group(2).strip(), file=path, line=lineno,
                               is_outline=m.group(1) != "Scenario" and m.group(1) != "Example")
            feature.scenarios.append(current)
            section, in_examples, header, last_effective = "scenario", False, None, "Given"
            continue
        if line.startswith(("Examples:", "Scenarios:")):
            in_examples, header = True, None
            continue
        if line.startswith("|"):
            if in_examples and current is not None:
                cells = _row(line)
                if header is None:
                    header = cells
                else:
                    current.examples.append(dict(zip(header, cells)))
            continue  # data tables attached to steps are ignored for now
        kw = next((k for k in STEP_KEYWORDS if line.startswith(k + " ") or line == k), None)
        if kw:
            text = line[len(kw):].strip()
            effective = last_effective if kw in ("And", "But", "*") else kw
            last_effective = effective
            step = Step(kw, effective, text, path, lineno, background=section == "background")
            if section == "background":
                feature.background.append(step)
            elif current is not None:
                current.steps.append(step)
    return feature


def find_features(root: Path) -> list[Feature]:
    return [parse_feature(p) for p in sorted(root.rglob("*.feature")) if ".git" not in p.parts]
