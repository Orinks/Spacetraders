from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.trade_symbol import TradeSymbol

T = TypeVar("T", bound="PurchaseCargoPurchaseCargoRequest")


@_attrs_define
class PurchaseCargoPurchaseCargoRequest:
    """
    Attributes:
        symbol (TradeSymbol): The good's symbol.
        units (int): Amounts of units to purchase.
    """

    symbol: TradeSymbol
    units: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol.value

        units = self.units

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "units": units,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        symbol = TradeSymbol(d.pop("symbol"))

        units = d.pop("units")

        purchase_cargo_purchase_cargo_request = cls(
            symbol=symbol,
            units=units,
        )

        purchase_cargo_purchase_cargo_request.additional_properties = d
        return purchase_cargo_purchase_cargo_request

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
