"""ASC 805 business combination and de-SPAC reverse recapitalization.

Purchase accounting: consideration, identifiable net assets at FV, NCI,
previously held interest, goodwill or bargain, measurement-period
adjustments, and the reverse-recap path used in a typical de-SPAC.
Pre-combination control gaps do not disappear at close.

Fair values are inputs. The engine does not appraise anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum


CENTS = Decimal("0.01")


def money(value: object) -> Decimal:
    return Decimal(str(value)).quantize(CENTS, rounding=ROUND_HALF_UP)


class Mode(str, Enum):
    ACQUISITION = "acquisition"
    REVERSE_RECAP = "reverse_recap"


@dataclass(frozen=True)
class Consideration:
    cash: Decimal = Decimal("0")
    equity_fv: Decimal = Decimal("0")
    contingent_fv: Decimal = Decimal("0")
    replacement_awards_precombo: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        for name in ("cash", "equity_fv", "contingent_fv", "replacement_awards_precombo"):
            object.__setattr__(self, name, money(getattr(self, name)))

    @property
    def total(self) -> Decimal:
        return money(self.cash + self.equity_fv + self.contingent_fv + self.replacement_awards_precombo)


@dataclass(frozen=True)
class Identifiable:
    assets_fv: Decimal
    liabilities_fv: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "assets_fv", money(self.assets_fv))
        object.__setattr__(self, "liabilities_fv", money(self.liabilities_fv))

    @property
    def net(self) -> Decimal:
        return money(self.assets_fv - self.liabilities_fv)


@dataclass(frozen=True)
class MeasurementAdjustment:
    item: str
    amount: Decimal
    notes: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "amount", money(self.amount))


@dataclass(frozen=True)
class Allocation:
    mode: Mode
    consideration: Decimal
    nci: Decimal
    previously_held: Decimal
    identifiable_net: Decimal
    goodwill: Decimal
    bargain_gain: Decimal
    recap_equity: Decimal
    transaction_costs_equity: Decimal
    transaction_costs_expense: Decimal
    adjustments: tuple[MeasurementAdjustment, ...]


def allocate(
    mode: Mode,
    consideration: Consideration,
    identifiable: Identifiable,
    nci: object = 0,
    previously_held: object = 0,
    transaction_costs: object = 0,
    costs_are_equity_issuance: bool = False,
    adjustments: tuple[MeasurementAdjustment, ...] = (),
) -> Allocation:
    nci_m = money(nci)
    prev = money(previously_held)
    costs = money(transaction_costs)
    adj_net = money(sum((a.amount for a in adjustments), Decimal("0")))
    identifiable_net = money(identifiable.net + adj_net)

    if mode is Mode.REVERSE_RECAP:
        # Typical de-SPAC: operating company is the accounting acquirer.
        # SPAC/PIPE net assets are recorded at FV; no goodwill; recap of equity.
        # Put cash received in identifiable assets — do not also put it in consideration.
        eq_costs = costs if costs_are_equity_issuance else Decimal("0.00")
        exp_costs = Decimal("0.00") if costs_are_equity_issuance else costs
        return Allocation(
            mode=mode,
            consideration=consideration.total,
            nci=nci_m,
            previously_held=prev,
            identifiable_net=identifiable_net,
            goodwill=Decimal("0.00"),
            bargain_gain=Decimal("0.00"),
            recap_equity=money(identifiable_net - eq_costs),
            transaction_costs_equity=eq_costs,
            transaction_costs_expense=exp_costs,
            adjustments=adjustments,
        )

    aggregate = money(consideration.total + nci_m + prev)
    difference = money(aggregate - identifiable_net)
    goodwill = difference if difference > 0 else Decimal("0.00")
    bargain = money(-difference) if difference < 0 else Decimal("0.00")
    return Allocation(
        mode=mode,
        consideration=consideration.total,
        nci=nci_m,
        previously_held=prev,
        identifiable_net=identifiable_net,
        goodwill=goodwill,
        bargain_gain=bargain,
        recap_equity=Decimal("0.00"),
        transaction_costs_equity=Decimal("0.00"),
        transaction_costs_expense=costs,
        adjustments=adjustments,
    )
