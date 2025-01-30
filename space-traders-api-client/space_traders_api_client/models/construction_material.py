from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.trade_symbol import TradeSymbol

T = TypeVar("T", bound="ConstructionMaterial")


@_attrs_define
class ConstructionMaterial:
    """The details of the required construction materials for a given waypoint under construction.

    Attributes:
        trade_symbol (TradeSymbol): The good's symbol.
        required (int): The number of units required.
        fulfilled (int): The number of units fulfilled toward the required amount.
    """

    trade_symbol: TradeSymbol
    required: int
    fulfilled: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        trade_symbol = self.trade_symbol.value

        required = self.required

        fulfilled = self.fulfilled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tradeSymbol": trade_symbol,
                "required": required,
                "fulfilled": fulfilled,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        trade_symbol = TradeSymbol(d.pop("tradeSymbol"))

        required = d.pop("required")

        fulfilled = d.pop("fulfilled")

        construction_material = cls(
            trade_symbol=trade_symbol,
            required=required,
            fulfilled=fulfilled,
        )

        construction_material.additional_properties = d
        return construction_material

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
