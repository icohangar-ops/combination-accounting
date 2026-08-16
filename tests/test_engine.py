from decimal import Decimal

from combination_accounting.engine import (
    Consideration,
    Identifiable,
    MeasurementAdjustment,
    Mode,
    allocate,
)
from combination_accounting.evidence import evidence_pack


def test_goodwill_acquisition() -> None:
    result = allocate(
        Mode.ACQUISITION,
        Consideration(cash="50000000", equity_fv="30000000", contingent_fv="5000000"),
        Identifiable(assets_fv="90000000", liabilities_fv="20000000"),
        nci="2000000",
    )
    # consideration 85m + NCI 2m - identifiable net 70m = 17m goodwill
    assert result.consideration == Decimal("85000000.00")
    assert result.identifiable_net == Decimal("70000000.00")
    assert result.goodwill == Decimal("17000000.00")
    assert result.bargain_gain == Decimal("0.00")


def test_bargain_purchase() -> None:
    result = allocate(
        Mode.ACQUISITION,
        Consideration(cash="60000000"),
        Identifiable(assets_fv="90000000", liabilities_fv="20000000"),
    )
    assert result.goodwill == Decimal("0.00")
    assert result.bargain_gain == Decimal("10000000.00")


def test_measurement_period_adjustment_changes_goodwill() -> None:
    result = allocate(
        Mode.ACQUISITION,
        Consideration(cash="80000000"),
        Identifiable(assets_fv="90000000", liabilities_fv="20000000"),
        adjustments=(
            MeasurementAdjustment("customer-relationships FV true-up", "3000000"),
        ),
    )
    # identifiable net 70m + 3m = 73m; consideration 80m; goodwill 7m
    assert result.identifiable_net == Decimal("73000000.00")
    assert result.goodwill == Decimal("7000000.00")


def test_reverse_recap_has_no_goodwill() -> None:
    result = allocate(
        Mode.REVERSE_RECAP,
        Consideration(cash="200000000", equity_fv="0"),
        Identifiable(assets_fv="200000000", liabilities_fv="0"),
        transaction_costs="15000000",
        costs_are_equity_issuance=True,
    )
    assert result.goodwill == Decimal("0.00")
    assert result.bargain_gain == Decimal("0.00")
    assert result.transaction_costs_equity == Decimal("15000000.00")
    assert result.transaction_costs_expense == Decimal("0.00")
    # recap equity = identifiable net 200m - 15m issuance costs = 185m
    assert result.recap_equity == Decimal("185000000.00")


def test_acquisition_transaction_costs_are_expensed() -> None:
    result = allocate(
        Mode.ACQUISITION,
        Consideration(cash="10000000"),
        Identifiable("10000000", "0"),
        transaction_costs="500000",
    )
    assert result.transaction_costs_expense == Decimal("500000.00")
    assert result.transaction_costs_equity == Decimal("0.00")


def test_evidence_pack() -> None:
    result = allocate(
        Mode.ACQUISITION,
        Consideration(cash="100"),
        Identifiable("80", "0"),
    )
    pack = evidence_pack(result, "H1 2026", "Controller", "DEAL-1")
    assert pack["goodwill"] == "20.00"
    assert pack["control_id"] == "ICFR-ASC805-01"
    assert pack["lock_state"] == "LOCKED"
    assert pack["is_evidence"] is True


def test_unsigned_pack_is_exploring_not_evidence() -> None:
    result = allocate(
        Mode.ACQUISITION,
        Consideration(cash="100"),
        Identifiable("80", "0"),
    )
    pack = evidence_pack(result, "H1 2026", "", "DEAL-1")
    assert pack["lock_state"] == "EXPLORING"
    assert pack["is_evidence"] is False
