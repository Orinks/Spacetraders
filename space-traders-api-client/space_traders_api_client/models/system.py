from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.system_type import SystemType

if TYPE_CHECKING:
    from ..models.system_faction import SystemFaction
    from ..models.system_waypoint import SystemWaypoint


T = TypeVar("T", bound="System")


@_attrs_define
class System:
    """
    Attributes:
        symbol (str): The symbol of the system.
        sector_symbol (str): The symbol of the sector.
        type_ (SystemType): The type of system.
        x (int): Relative position of the system in the sector in the x axis.
        y (int): Relative position of the system in the sector in the y axis.
        waypoints (list['SystemWaypoint']): Waypoints in this system.
        factions (list['SystemFaction']): Factions that control this system.
    """

    symbol: str
    sector_symbol: str
    type_: SystemType
    x: int
    y: int
    waypoints: list["SystemWaypoint"]
    factions: list["SystemFaction"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol

        sector_symbol = self.sector_symbol

        type_ = self.type_.value

        x = self.x

        y = self.y

        waypoints = []
        for waypoints_item_data in self.waypoints:
            waypoints_item = waypoints_item_data.to_dict()
            waypoints.append(waypoints_item)

        factions = []
        for factions_item_data in self.factions:
            factions_item = factions_item_data.to_dict()
            factions.append(factions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "sectorSymbol": sector_symbol,
                "type": type_,
                "x": x,
                "y": y,
                "waypoints": waypoints,
                "factions": factions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.system_faction import SystemFaction
        from ..models.system_waypoint import SystemWaypoint

        d = src_dict.copy()
        symbol = d.pop("symbol")

        sector_symbol = d.pop("sectorSymbol")

        type_ = SystemType(d.pop("type"))

        x = d.pop("x")

        y = d.pop("y")

        waypoints = []
        _waypoints = d.pop("waypoints")
        for waypoints_item_data in _waypoints:
            waypoints_item = SystemWaypoint.from_dict(waypoints_item_data)

            waypoints.append(waypoints_item)

        factions = []
        _factions = d.pop("factions")
        for factions_item_data in _factions:
            factions_item = SystemFaction.from_dict(factions_item_data)

            factions.append(factions_item)

        system = cls(
            symbol=symbol,
            sector_symbol=sector_symbol,
            type_=type_,
            x=x,
            y=y,
            waypoints=waypoints,
            factions=factions,
        )

        system.additional_properties = d
        return system

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
