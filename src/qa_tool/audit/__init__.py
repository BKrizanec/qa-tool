"""Suite trust audit: compare what Cucumber-JVM scenarios claim to verify with what their code checks."""
from __future__ import annotations

from pathlib import Path

from .analysis import Analyzer
from .gherkin import find_features
from .java_index import JavaIndex


def load(repo: Path) -> Analyzer:
    """Parse a suite without judging it, for tracing individual scenarios."""
    return Analyzer(JavaIndex(repo), find_features(repo))


def audit(repo: Path) -> Analyzer:
    analyzer = load(repo)
    analyzer.run()
    return analyzer
