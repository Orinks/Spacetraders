from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="NavigateShipBody")


@_attrs_define
class NavigateShipBody:
    """
    Attributes:
        waypoint_symbol (str): The target destination.
    """

    waypoint_symbol: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        waypoint_symbol = self.waypoint_symbol

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "waypointSymbol": waypoint_symbol,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        waypoint_symbol = d.pop("waypointSymbol")

        navigate_ship_body = cls(
            waypoint_symbol=waypoint_symbol,
        )

        navigate_ship_body.additional_properties = d
        return navigate_ship_body

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
