"""The bundled fixture suite has one planted problem per check; the audit must find each of them
and nothing else."""
from pathlib import Path

import pytest

from qa_tool.audit import audit

FIXTURE = Path(__file__).parent / "fixtures" / "shop-suite"


@pytest.fixture(scope="module")
def findings():
    return audit(FIXTURE).findings


def codes_for(findings, needle):
    return {f.code for f in findings if needle in f.title}


def test_scenario_without_any_check(findings):
    assert "SCENARIO_VERIFIES_NOTHING" in codes_for(findings, '"Wrong password"')


def test_then_step_that_only_reads_the_error(findings):
    assert "HOLLOW_THEN" in codes_for(findings, "an error message is shown")


def test_commented_out_step_definition(findings):
    f = next(f for f in findings if f.code == "UNDEFINED_STEP")
    assert "account locked banner" in f.title
    assert "commented out" in " ".join(f.detail)


def test_empty_step(findings):
    assert codes_for(findings, "clicks the submit button") == {"EMPTY_STEP"}


def test_unused_page_object(findings):
    assert [f.title for f in findings if f.code == "ORPHAN_PAGE_OBJECT"] == [
        "Page object `OrdersPage` is never used by any scenario"]


def test_valid_login_is_trusted(findings):
    # DashboardPage.verifyDisplayed() asserts on the `h1.dashboard` locator: a real, matching check.
    assert not [f for f in findings if "Valid login" in (f.scenario or "") or "dashboard is displayed" in f.title]


def test_no_unexpected_findings(findings):
    assert {f.code for f in findings} == {"SCENARIO_VERIFIES_NOTHING", "HOLLOW_THEN", "UNDEFINED_STEP",
                                          "EMPTY_STEP", "ORPHAN_PAGE_OBJECT"}
