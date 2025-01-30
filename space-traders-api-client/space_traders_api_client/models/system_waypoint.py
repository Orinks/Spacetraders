from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.waypoint_type import WaypointType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.waypoint_orbital import WaypointOrbital


T = TypeVar("T", bound="SystemWaypoint")


@_attrs_define
class SystemWaypoint:
    """
    Attributes:
        symbol (str): The symbol of the waypoint.
        type_ (WaypointType): The type of waypoint.
        x (int): Relative position of the waypoint on the system's x axis. This is not an absolute position in the
            universe.
        y (int): Relative position of the waypoint on the system's y axis. This is not an absolute position in the
            universe.
        orbitals (list['WaypointOrbital']): Waypoints that orbit this waypoint.
        orbits (Union[Unset, str]): The symbol of the parent waypoint, if this waypoint is in orbit around another
            waypoint. Otherwise this value is undefined.
    """

    symbol: str
    type_: WaypointType
    x: int
    y: int
    orbitals: list["WaypointOrbital"]
    orbits: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol

        type_ = self.type_.value

        x = self.x

        y = self.y

        orbitals = []
        for orbitals_item_data in self.orbitals:
            orbitals_item = orbitals_item_data.to_dict()
            orbitals.append(orbitals_item)

        orbits = self.orbits

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "type": type_,
                "x": x,
                "y": y,
                "orbitals": orbitals,
            }
        )
        if orbits is not UNSET:
            field_dict["orbits"] = orbits

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.waypoint_orbital import WaypointOrbital

        d = src_dict.copy()
        symbol = d.pop("symbol")

        type_ = WaypointType(d.pop("type"))

        x = d.pop("x")

        y = d.pop("y")

        orbitals = []
        _orbitals = d.pop("orbitals")
        for orbitals_item_data in _orbitals:
            orbitals_item = WaypointOrbital.from_dict(orbitals_item_data)

            orbitals.append(orbitals_item)

        orbits = d.pop("orbits", UNSET)

        system_waypoint = cls(
            symbol=symbol,
            type_=type_,
            x=x,
            y=y,
            orbitals=orbitals,
            orbits=orbits,
        )

        system_waypoint.additional_properties = d
        return system_waypoint

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
