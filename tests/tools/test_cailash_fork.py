"""Behaviour specific to the Cailash fork, which targets self-hosted Plane Community.

Kept in one file so a rebase onto upstream has a single place to look.
"""

from __future__ import annotations

import asyncio

import pytest
from fastmcp import FastMCP

from plane_mcp.tools import register_tools
from plane_mcp.tools.editions import COMMUNITY_HIDDEN, hidden_tools

# Intake triage: Community has no `/intake-issues/{id}/status` route, so triage
# goes through the classic PATCH on the intake record.


def test_an_accept_goes_through_the_classic_intake_patch(registered, spy):
    registered["intake"].fn(action="update", project_id="p", workitem_id="w", status=1)

    call = spy.recorder.only()
    assert call.method == "intake.update"
    assert call.kwargs["work_item_id"] == "w"
    assert call.kwargs["data"].status == 1


def test_a_snooze_sends_its_date_through_the_classic_patch(registered, spy):
    registered["intake"].fn(
        action="update", project_id="p", workitem_id="w", status=0, snoozed_till="2026-12-01T00:00:00Z"
    )

    call = spy.recorder.only()
    assert call.method == "intake.update"
    assert call.kwargs["data"].snoozed_till == "2026-12-01T00:00:00Z"


def test_a_duplicate_sends_its_target_through_the_classic_patch(registered, spy):
    registered["intake"].fn(action="update", project_id="p", workitem_id="w", status=2, duplicate_to="d")

    call = spy.recorder.only()
    assert call.method == "intake.update"
    assert call.kwargs["data"].duplicate_to == "d"


def test_the_status_route_is_never_called(registered, spy):
    for status in (-2, -1, 1):
        registered["intake"].fn(action="update", project_id="p", workitem_id="w", status=status)

    assert {call.method for call in spy.recorder.calls} == {"intake.update"}


@pytest.mark.parametrize(("status", "needed"), [(0, "snoozed_till"), (2, "duplicate_to")])
def test_a_triage_decision_still_requires_its_companion_field(registered, spy, status, needed):
    result = registered["intake"].fn(action="update", project_id="p", workitem_id="w", status=status)

    assert isinstance(result, str) and result.startswith("Error:") and needed in result
    assert not spy.recorder.calls


# Editions: tools whose routes do not exist on Community are not advertised there.


def _names(monkeypatch, edition: str | None) -> set[str]:
    if edition is None:
        monkeypatch.delenv("PLANE_EDITION", raising=False)
    else:
        monkeypatch.setenv("PLANE_EDITION", edition)
    mcp = FastMCP("edition")
    register_tools(mcp, legacy_names=False)
    return {tool.name for tool in asyncio.new_event_loop().run_until_complete(mcp.list_tools())}


def test_community_hides_the_tools_that_always_404(monkeypatch):
    names = _names(monkeypatch, "community")

    assert not names & COMMUNITY_HIDDEN
    assert "intake" in names and "workitem" in names


def test_the_fork_defaults_to_community(monkeypatch):
    assert _names(monkeypatch, None) == _names(monkeypatch, "community")


@pytest.mark.parametrize("edition", ["full", "cloud", "FULL"])
def test_a_non_community_edition_advertises_everything(monkeypatch, edition):
    assert COMMUNITY_HIDDEN <= _names(monkeypatch, edition)


def test_the_hidden_set_names_real_tools(resource_modules):
    assert COMMUNITY_HIDDEN <= {mod.NAME for mod in resource_modules}
    assert COMMUNITY_HIDDEN == {
        "project_estimate",
        "workitem_type",
        "workitem_property",
        "customer",
        "customer_property",
        "customer_request",
    }


def test_hidden_tools_reads_the_env(monkeypatch):
    monkeypatch.setenv("PLANE_EDITION", " Community ")
    assert hidden_tools() == COMMUNITY_HIDDEN
    monkeypatch.setenv("PLANE_EDITION", "full")
    assert hidden_tools() == frozenset()


def test_a_retired_name_of_a_hidden_tool_does_not_resolve(monkeypatch):
    monkeypatch.setenv("PLANE_EDITION", "community")
    mcp = FastMCP("edition")
    register_tools(mcp)
    loop = asyncio.new_event_loop()
    assert loop.run_until_complete(mcp.get_tool("list_customers")) is None
    assert loop.run_until_complete(mcp.get_tool("list_intake_work_items")) is not None
