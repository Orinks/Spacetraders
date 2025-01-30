from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.faction_symbol import FactionSymbol

T = TypeVar("T", bound="WaypointFaction")


@_attrs_define
class WaypointFaction:
    """The faction that controls the waypoint.

    Attributes:
        symbol (FactionSymbol): The symbol of the faction.
    """

    symbol: FactionSymbol
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        symbol = FactionSymbol(d.pop("symbol"))

        waypoint_faction = cls(
            symbol=symbol,
        )

        waypoint_faction.additional_properties = d
        return waypoint_faction

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
