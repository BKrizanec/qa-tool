"""Exercise the MCP server through a real client session (in-process)."""
import json
from pathlib import Path

import pytest
from mcp import Client

from qa_tool.server import server

FIXTURE = str(Path(__file__).parent / "fixtures" / "shop-suite")

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def call(name, args):
    async with Client(server) as client:
        return await client.call_tool(name, args)


async def test_tools_are_listed_as_read_only():
    async with Client(server) as client:
        tools = {t.name: t for t in (await client.list_tools()).tools}
    assert set(tools) == {"audit_suite", "trace_scenario"}
    assert all(t.annotations.read_only_hint for t in tools.values())


async def test_audit_suite_markdown():
    result = await call("audit_suite", {"repo_path": FIXTURE})
    assert not result.is_error
    report = result.content[0].text
    assert report.startswith("# Suite trust audit: shop-suite")
    assert 'Scenario "Wrong password" verifies nothing' in report


async def test_audit_suite_json():
    result = await call("audit_suite", {"repo_path": FIXTURE, "format": "json"})
    data = json.loads(result.content[0].text)
    assert data["summary"]["scenarios"] == 3
    assert {f["code"] for f in data["findings"]} >= {"HOLLOW_THEN", "EMPTY_STEP"}


async def test_trace_scenario_shows_what_each_step_checks():
    result = await call("trace_scenario", {"repo_path": FIXTURE, "scenario": "valid login"})
    trace = result.structured_content
    assert trace["scenario"] == "Valid login"
    then = trace["steps"][-1]
    assert then["text"] == "the dashboard is displayed"
    assert then["step_definition"]["method"] == "LoginSteps.dashboardIsDisplayed"
    assert [a["can_fail_test"] for a in then["assertions"]] == [True]
    assert "h1.dashboard" in " ".join(then["checks"])


async def test_trace_scenario_hollow_then_has_no_failing_assertion():
    trace = (await call("trace_scenario", {"repo_path": FIXTURE, "scenario": "Wrong password"})).structured_content
    then = trace["steps"][-1]
    assert not any(a["can_fail_test"] for a in then["assertions"])
    assert trace["steps"][2]["actions"] == []    # "clicks the submit button" is empty


async def test_trace_scenario_ambiguous_name_lists_candidates():
    result = await call("trace_scenario", {"repo_path": FIXTURE, "scenario": "a"})   # in all three names
    assert result.is_error
    assert "Several scenarios match" in result.content[0].text
    assert "Valid login (src/test/resources/features/login.feature:3)" in result.content[0].text


async def test_trace_scenario_unknown_name():
    result = await call("trace_scenario", {"repo_path": FIXTURE, "scenario": "checkout"})
    assert result.is_error
    assert "No scenario matches" in result.content[0].text


async def test_bad_path_is_an_error():
    result = await call("audit_suite", {"repo_path": "/nonexistent/suite"})
    assert result.is_error
    assert result.content[0].text.endswith("Not a directory: /nonexistent/suite")
