from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from control_spine import exit_code

from combination_accounting.engine import (
    Consideration,
    Identifiable,
    MeasurementAdjustment,
    Mode,
    allocate,
)
from combination_accounting.evidence import evidence_markdown, evidence_pack


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="ASC 805 / de-SPAC allocation + evidence pack")
    p.add_argument("deal_json")
    p.add_argument("--period", default="current")
    p.add_argument("--owner", default="")
    args = p.parse_args(argv)
    raw = json.loads(Path(args.deal_json).read_text())
    adjustments = tuple(
        MeasurementAdjustment(a["item"], a["amount"], a.get("notes", ""))
        for a in raw.get("adjustments") or ()
    )
    result = allocate(
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
    pack = evidence_pack(result, args.period, args.owner, raw.get("deal_id", "deal"))
    print(evidence_markdown(pack))
    print(pack["lock_state"], file=sys.stderr)
    return exit_code(pack)


if __name__ == "__main__":
    raise SystemExit(main())
