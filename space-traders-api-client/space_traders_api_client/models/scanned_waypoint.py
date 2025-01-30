from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.waypoint_type import WaypointType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chart import Chart
    from ..models.waypoint_faction import WaypointFaction
    from ..models.waypoint_orbital import WaypointOrbital
    from ..models.waypoint_trait import WaypointTrait


T = TypeVar("T", bound="ScannedWaypoint")


@_attrs_define
class ScannedWaypoint:
    """A waypoint that was scanned by a ship.

    Attributes:
        symbol (str): The symbol of the waypoint.
        type_ (WaypointType): The type of waypoint.
        system_symbol (str): The symbol of the system.
        x (int): Position in the universe in the x axis.
        y (int): Position in the universe in the y axis.
        orbitals (list['WaypointOrbital']): List of waypoints that orbit this waypoint.
        traits (list['WaypointTrait']): The traits of the waypoint.
        faction (Union[Unset, WaypointFaction]): The faction that controls the waypoint.
        chart (Union[Unset, Chart]): The chart of a system or waypoint, which makes the location visible to other
            agents.
    """

    symbol: str
    type_: WaypointType
    system_symbol: str
    x: int
    y: int
    orbitals: list["WaypointOrbital"]
    traits: list["WaypointTrait"]
    faction: Union[Unset, "WaypointFaction"] = UNSET
    chart: Union[Unset, "Chart"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol

        type_ = self.type_.value

        system_symbol = self.system_symbol

        x = self.x

        y = self.y

        orbitals = []
        for orbitals_item_data in self.orbitals:
            orbitals_item = orbitals_item_data.to_dict()
            orbitals.append(orbitals_item)

        traits = []
        for traits_item_data in self.traits:
            traits_item = traits_item_data.to_dict()
            traits.append(traits_item)

        faction: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.faction, Unset):
            faction = self.faction.to_dict()

        chart: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.chart, Unset):
            chart = self.chart.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "type": type_,
                "systemSymbol": system_symbol,
                "x": x,
                "y": y,
                "orbitals": orbitals,
                "traits": traits,
            }
        )
        if faction is not UNSET:
            field_dict["faction"] = faction
        if chart is not UNSET:
            field_dict["chart"] = chart

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.chart import Chart
        from ..models.waypoint_faction import WaypointFaction
        from ..models.waypoint_orbital import WaypointOrbital
        from ..models.waypoint_trait import WaypointTrait

        d = src_dict.copy()
        symbol = d.pop("symbol")

        type_ = WaypointType(d.pop("type"))

        system_symbol = d.pop("systemSymbol")

        x = d.pop("x")

        y = d.pop("y")

        orbitals = []
        _orbitals = d.pop("orbitals")
        for orbitals_item_data in _orbitals:
            orbitals_item = WaypointOrbital.from_dict(orbitals_item_data)

            orbitals.append(orbitals_item)

        traits = []
        _traits = d.pop("traits")
        for traits_item_data in _traits:
            traits_item = WaypointTrait.from_dict(traits_item_data)

            traits.append(traits_item)

        _faction = d.pop("faction", UNSET)
        faction: Union[Unset, WaypointFaction]
        if isinstance(_faction, Unset):
            faction = UNSET
        else:
            faction = WaypointFaction.from_dict(_faction)

        _chart = d.pop("chart", UNSET)
        chart: Union[Unset, Chart]
        if isinstance(_chart, Unset):
            chart = UNSET
        else:
            chart = Chart.from_dict(_chart)

        scanned_waypoint = cls(
            symbol=symbol,
            type_=type_,
            system_symbol=system_symbol,
            x=x,
            y=y,
            orbitals=orbitals,
            traits=traits,
            faction=faction,
            chart=chart,
        )

        scanned_waypoint.additional_properties = d
        return scanned_waypoint

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
