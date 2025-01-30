from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.waypoint_trait_symbol import WaypointTraitSymbol

T = TypeVar("T", bound="WaypointTrait")


@_attrs_define
class WaypointTrait:
    """
    Attributes:
        symbol (WaypointTraitSymbol): The unique identifier of the trait.
        name (str): The name of the trait.
        description (str): A description of the trait.
    """

    symbol: WaypointTraitSymbol
    name: str
    description: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol.value

        name = self.name

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "name": name,
                "description": description,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        symbol = WaypointTraitSymbol(d.pop("symbol"))

        name = d.pop("name")

        description = d.pop("description")

        waypoint_trait = cls(
            symbol=symbol,
            name=name,
            description=description,
        )

        waypoint_trait.additional_properties = d
        return waypoint_trait

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
