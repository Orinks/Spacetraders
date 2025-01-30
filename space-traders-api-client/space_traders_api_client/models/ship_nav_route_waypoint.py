from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.waypoint_type import WaypointType

T = TypeVar("T", bound="ShipNavRouteWaypoint")


@_attrs_define
class ShipNavRouteWaypoint:
    """The destination or departure of a ships nav route.

    Attributes:
        symbol (str): The symbol of the waypoint.
        type_ (WaypointType): The type of waypoint.
        system_symbol (str): The symbol of the system.
        x (int): Position in the universe in the x axis.
        y (int): Position in the universe in the y axis.
    """

    symbol: str
    type_: WaypointType
    system_symbol: str
    x: int
    y: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol

        type_ = self.type_.value

        system_symbol = self.system_symbol

        x = self.x

        y = self.y

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "type": type_,
                "systemSymbol": system_symbol,
                "x": x,
                "y": y,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        symbol = d.pop("symbol")

        type_ = WaypointType(d.pop("type"))

        system_symbol = d.pop("systemSymbol")

        x = d.pop("x")

        y = d.pop("y")

        ship_nav_route_waypoint = cls(
            symbol=symbol,
            type_=type_,
            system_symbol=system_symbol,
            x=x,
            y=y,
        )

        ship_nav_route_waypoint.additional_properties = d
        return ship_nav_route_waypoint

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
