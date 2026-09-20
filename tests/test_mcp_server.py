"""The MCP server registers the engine's deterministic allocation as callable tools.

Pins the test suite's canonical goodwill case (85m consideration + 2m NCI -
70m identifiable net = 17m goodwill) through the MCP tool path. Skipped
cleanly when the optional ``mcp`` SDK is not installed.
"""

from __future__ import annotations

import asyncio

import pytest

pytest.importorskip("mcp")

from combination_accounting import mcp_server  # noqa: E402
from control_spine import canonical_hash


def _tool_names() -> set[str]:
    tools = asyncio.run(mcp_server.mcp.list_tools())
    return {t.name for t in tools}


def _deal() -> dict:
    return {
        "deal_id": "DEAL-1",
        "mode": "acquisition",
        "cash": "50000000",
        "equity_fv": "30000000",
        "contingent_fv": "5000000",
        "assets_fv": "90000000",
        "liabilities_fv": "20000000",
        "nci": "2000000",
    }


def test_expected_tools_registered() -> None:
    assert _tool_names() >= {"allocate_deal", "deal_evidence_pack"}


def test_allocate_deal_pins_the_suite_numbers() -> None:
    result = mcp_server.allocate_deal(_deal())
    assert result["consideration"] == "85000000.00"
    assert result["identifiable_net"] == "70000000.00"
    assert result["goodwill"] == "17000000.00"
    assert result["bargain_gain"] == "0.00"


def test_evidence_pack_pins_deal_id() -> None:
    pack = mcp_server.deal_evidence_pack(_deal(), period_label="H1 2026")
    assert pack["deal_id"] == "DEAL-1"
    assert pack["lock_state"] == "EXPLORING"
    assert pack["is_evidence"] is False
    assert pack["invoked_via"] == "mcp"
    assert pack["spine"]["envelope_hash"] == canonical_hash(
        {k: v for k, v in pack["spine"].items() if k != "envelope_hash"}
    )
    assert pack["goodwill"] == "17000000.00"
