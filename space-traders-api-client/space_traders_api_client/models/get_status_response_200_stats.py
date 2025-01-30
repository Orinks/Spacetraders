from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetStatusResponse200Stats")


@_attrs_define
class GetStatusResponse200Stats:
    """
    Attributes:
        agents (int): Number of registered agents in the game.
        ships (int): Total number of ships in the game.
        systems (int): Total number of systems in the game.
        waypoints (int): Total number of waypoints in the game.
    """

    agents: int
    ships: int
    systems: int
    waypoints: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agents = self.agents

        ships = self.ships

        systems = self.systems

        waypoints = self.waypoints

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agents": agents,
                "ships": ships,
                "systems": systems,
                "waypoints": waypoints,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        agents = d.pop("agents")

        ships = d.pop("ships")

        systems = d.pop("systems")

        waypoints = d.pop("waypoints")

        get_status_response_200_stats = cls(
            agents=agents,
            ships=ships,
            systems=systems,
            waypoints=waypoints,
        )

        get_status_response_200_stats.additional_properties = d
        return get_status_response_200_stats

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
