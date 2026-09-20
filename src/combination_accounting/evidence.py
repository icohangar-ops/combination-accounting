from __future__ import annotations

from control_spine import render_spine, seal
from combination_accounting.engine import Allocation

FOUNDATION = (
    "Fair values are inputs. This engine does not appraise identifiable assets.",
    "Accounting-acquirer determination is an input (acquisition vs reverse recap).",
    "Acquisition-mode transaction costs are expensed; reverse-recap issuance costs hit equity when flagged.",
    "Measurement-period adjustments change identifiable net and therefore goodwill.",
)

ENGINE_ID = "combination-accounting-engine"
ENGINE_VERSION = "0.1.0"


def evidence_pack(allocation: Allocation, period_label: str, owner: str, deal_id: str, invoked_via: str | None = None) -> dict:
    pack = {
        "control_id": "ICFR-ASC805-01",
        "control_objective": "Business combinations and reverse recapitalizations are measured from FV inputs; goodwill/bargain and measurement-period adjustments are complete.",
        "period": period_label,
        "deal_id": deal_id,
        "population_count": 1,
        "threshold": "100% of combinations in the period; every measurement-period item tracked until the window closes.",
        "mode": allocation.mode.value,
        "consideration": str(allocation.consideration),
        "nci": str(allocation.nci),
        "previously_held": str(allocation.previously_held),
        "identifiable_net": str(allocation.identifiable_net),
        "goodwill": str(allocation.goodwill),
        "bargain_gain": str(allocation.bargain_gain),
        "recap_equity": str(allocation.recap_equity),
        "transaction_costs_equity": str(allocation.transaction_costs_equity),
        "transaction_costs_expense": str(allocation.transaction_costs_expense),
        "adjustments": [
            {"item": a.item, "amount": str(a.amount), "notes": a.notes}
            for a in allocation.adjustments
        ],
        "prepared_by": ENGINE_ID,
        "owner_signoff": owner,
        "conclusion": (
            f"Mode {allocation.mode.value}. Goodwill {allocation.goodwill}, bargain {allocation.bargain_gain}. "
            "Owner confirms FV inputs and the accounting-acquirer determination."
        ),
    }
    if invoked_via is not None:
        pack["invoked_via"] = invoked_via
    return seal(
        pack,
        engine_id=ENGINE_ID,
        engine_version=ENGINE_VERSION,
        inputs={
            "deal_id": deal_id,
            "mode": allocation.mode.value,
            "consideration": str(allocation.consideration),
            "identifiable_net": str(allocation.identifiable_net),
        },
        foundation=FOUNDATION,
    )


def evidence_markdown(pack: dict) -> str:
    lines = [
        f"# ASC 805 / de-SPAC evidence pack — {pack['period']}",
        "",
        *render_spine(pack),
        f"**Control:** {pack['control_id']}  **Deal:** {pack['deal_id']}  **Mode:** {pack['mode']}",
        f"**Consideration:** {pack['consideration']}  **Identifiable net:** {pack['identifiable_net']}",
        f"**Goodwill:** {pack['goodwill']}  **Bargain gain:** {pack['bargain_gain']}  **Recap equity:** {pack['recap_equity']}",
        f"**Owner sign-off:** {pack['owner_signoff'] or '_unsigned_'}",
        "",
        "## Measurement-period adjustments",
        "",
    ]
    if not pack["adjustments"]:
        lines.append("None.")
    else:
        lines += [
            "| Item | Amount | Notes |",
            "|---|---:|---|",
        ]
        for row in pack["adjustments"]:
            lines.append(f"| {row['item']} | {row['amount']} | {row['notes']} |")
    lines += ["", pack["conclusion"], ""]
    return "\n".join(lines)
