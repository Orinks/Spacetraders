from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SupplyConstructionBody")


@_attrs_define
class SupplyConstructionBody:
    """
    Attributes:
        ship_symbol (str): Symbol of the ship to use.
        trade_symbol (str): The symbol of the good to supply.
        units (int): Amount of units to supply.
    """

    ship_symbol: str
    trade_symbol: str
    units: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ship_symbol = self.ship_symbol

        trade_symbol = self.trade_symbol

        units = self.units

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "shipSymbol": ship_symbol,
                "tradeSymbol": trade_symbol,
                "units": units,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        ship_symbol = d.pop("shipSymbol")

        trade_symbol = d.pop("tradeSymbol")

        units = d.pop("units")

        supply_construction_body = cls(
            ship_symbol=ship_symbol,
            trade_symbol=trade_symbol,
            units=units,
        )

        supply_construction_body.additional_properties = d
        return supply_construction_body

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
