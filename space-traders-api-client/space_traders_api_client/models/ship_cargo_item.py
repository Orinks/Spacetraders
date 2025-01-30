from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.trade_symbol import TradeSymbol

T = TypeVar("T", bound="ShipCargoItem")


@_attrs_define
class ShipCargoItem:
    """The type of cargo item and the number of units.

    Attributes:
        symbol (TradeSymbol): The good's symbol.
        name (str): The name of the cargo item type.
        description (str): The description of the cargo item type.
        units (int): The number of units of the cargo item.
    """

    symbol: TradeSymbol
    name: str
    description: str
    units: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol.value

        name = self.name

        description = self.description

        units = self.units

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "name": name,
                "description": description,
                "units": units,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        symbol = TradeSymbol(d.pop("symbol"))

        name = d.pop("name")

        description = d.pop("description")

        units = d.pop("units")

        ship_cargo_item = cls(
            symbol=symbol,
            name=name,
            description=description,
            units=units,
        )

        ship_cargo_item.additional_properties = d
        return ship_cargo_item

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
