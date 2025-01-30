import datetime
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.ship_nav_route_waypoint import ShipNavRouteWaypoint


T = TypeVar("T", bound="ShipNavRoute")


@_attrs_define
class ShipNavRoute:
    """The routing information for the ship's most recent transit or current location.

    Attributes:
        destination (ShipNavRouteWaypoint): The destination or departure of a ships nav route.
        origin (ShipNavRouteWaypoint): The destination or departure of a ships nav route.
        departure_time (datetime.datetime): The date time of the ship's departure.
        arrival (datetime.datetime): The date time of the ship's arrival. If the ship is in-transit, this is the
            expected time of arrival.
    """

    destination: "ShipNavRouteWaypoint"
    origin: "ShipNavRouteWaypoint"
    departure_time: datetime.datetime
    arrival: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        destination = self.destination.to_dict()

        origin = self.origin.to_dict()

        departure_time = self.departure_time.isoformat()

        arrival = self.arrival.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "destination": destination,
                "origin": origin,
                "departureTime": departure_time,
                "arrival": arrival,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ship_nav_route_waypoint import ShipNavRouteWaypoint

        d = src_dict.copy()
        destination = ShipNavRouteWaypoint.from_dict(d.pop("destination"))

        origin = ShipNavRouteWaypoint.from_dict(d.pop("origin"))

        departure_time = isoparse(d.pop("departureTime"))

        arrival = isoparse(d.pop("arrival"))

        ship_nav_route = cls(
            destination=destination,
            origin=origin,
            departure_time=departure_time,
            arrival=arrival,
        )

        ship_nav_route.additional_properties = d
        return ship_nav_route

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
