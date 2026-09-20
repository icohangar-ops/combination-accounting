"""MCP server for the combination-accounting engine.

Exposes deterministic ASC 805 purchase accounting as Model Context Protocol
tools. Thin wrapper — all measurement logic lives in
``combination_accounting.engine`` and ``combination_accounting.evidence``
and is reused verbatim; nothing here touches the network, and fair values
plus the accounting-acquirer determination stay inputs the control owner
signs.

Follows the same publishing path proven by invoice-audit-engine /
codesentinel: namespace ``io.github.Cubiczan``, stdio transport, published
via the ``mcp-publisher`` CLI.

Run it:

    uvx --from 'combination-accounting[mcp]' combination-accounting-mcp
    # or, from a checkout:
    uv run --with 'mcp>=1.2,<2' --with . python -m combination_accounting.mcp_server
"""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from enum import Enum
from typing import Any

from mcp.server.fastmcp import FastMCP

from combination_accounting.engine import (
    Consideration,
    Identifiable,
    MeasurementAdjustment,
    Mode,
    allocate,
)
from combination_accounting.evidence import evidence_pack

mcp = FastMCP(
    "combination-accounting",
    instructions=(
        "Deterministic ASC 805 business-combination and de-SPAC reverse-recap "
        "measurement. Supply the deal terms; the tools allocate consideration "
        "to identifiable net assets at fair value, compute goodwill or "
        "bargain-purchase gain, apply measurement-period adjustments, and "
        "render the evidence pack a tester can reperform. Fair values are "
        "inputs — the engine does not appraise anything."
    ),
)


def _allocate_from_dict(raw: dict[str, Any]) -> Any:
    """Build the deal from the CLI/JSON shape (same keys as the CLI's input file)."""
    adjustments = tuple(
        MeasurementAdjustment(a["item"], a["amount"], a.get("notes", ""))
        for a in raw.get("adjustments") or ()
    )
    return allocate(
        Mode(raw["mode"]),
        Consideration(
            cash=raw.get("cash", 0),
            equity_fv=raw.get("equity_fv", 0),
            contingent_fv=raw.get("contingent_fv", 0),
            replacement_awards_precombo=raw.get("replacement_awards_precombo", 0),
        ),
        Identifiable(raw["assets_fv"], raw["liabilities_fv"]),
        nci=raw.get("nci", 0),
        previously_held=raw.get("previously_held", 0),
        transaction_costs=raw.get("transaction_costs", 0),
        costs_are_equity_issuance=raw.get("costs_are_equity_issuance", False),
        adjustments=adjustments,
    )


def _jsonify(value: Any) -> Any:
    """JSON-safe conversion: Decimals become strings so cents survive exactly."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {k: _jsonify(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonify(v) for v in value]
    return value


@mcp.tool()
def allocate_deal(deal: dict[str, Any]) -> dict[str, Any]:
    """Run ASC 805 purchase accounting for one combination (acquisition or reverse recap).

    Returns total consideration, NCI, previously held interest, identifiable
    net assets, goodwill / bargain-purchase gain, recap equity, and the
    transaction-cost split. Amounts are exact decimal strings.

    Args:
        deal: Deal terms. Expected keys mirror the CLI input file:
            mode ("acquisition" | "reverse_recap"), cash, equity_fv,
            contingent_fv, replacement_awards_precombo, assets_fv,
            liabilities_fv, nci, previously_held, transaction_costs,
            costs_are_equity_issuance, adjustments, deal_id.
    """
    return _jsonify(asdict(_allocate_from_dict(deal)))


@mcp.tool()
def deal_evidence_pack(
    deal: dict[str, Any],
    period_label: str = "current",
) -> dict[str, Any]:
    """Build the ASC 805 evidence pack a tester can reperform without the source code.

    Runs the allocation and renders the control-spine pack (mode, goodwill /
    bargain, measurement-period adjustments, owner sign-off).

    Args:
        deal: Deal terms, same shape as allocate_deal's input.
        period_label: Close period label (e.g. "H1 2026").
        Sign-off: MCP never accepts an owner — packs built here are always
        unsigned (EXPLORING, not evidence). A named human signs via the CLI
        (--owner), never through MCP.
    """
    allocation = _allocate_from_dict(deal)
    pack = evidence_pack(
        allocation, period_label, "", deal.get("deal_id", "deal"),
        invoked_via="mcp",
    )
    return _jsonify(pack)


def main() -> None:
    """Console-script entry point: run the server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
