from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.ship_condition_event import ShipConditionEvent
    from ..models.ship_fuel import ShipFuel
    from ..models.ship_nav import ShipNav


T = TypeVar("T", bound="NavigateShipResponse200Data")


@_attrs_define
class NavigateShipResponse200Data:
    """
    Attributes:
        fuel (ShipFuel): Details of the ship's fuel tanks including how much fuel was consumed during the last transit
            or action.
        nav (ShipNav): The navigation information of the ship.
        events (list['ShipConditionEvent']):
    """

    fuel: "ShipFuel"
    nav: "ShipNav"
    events: list["ShipConditionEvent"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fuel = self.fuel.to_dict()

        nav = self.nav.to_dict()

        events = []
        for events_item_data in self.events:
            events_item = events_item_data.to_dict()
            events.append(events_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fuel": fuel,
                "nav": nav,
                "events": events,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ship_condition_event import ShipConditionEvent
        from ..models.ship_fuel import ShipFuel
        from ..models.ship_nav import ShipNav

        d = src_dict.copy()
        fuel = ShipFuel.from_dict(d.pop("fuel"))

        nav = ShipNav.from_dict(d.pop("nav"))

        events = []
        _events = d.pop("events")
        for events_item_data in _events:
            events_item = ShipConditionEvent.from_dict(events_item_data)

            events.append(events_item)

        navigate_ship_response_200_data = cls(
            fuel=fuel,
            nav=nav,
            events=events,
        )

        navigate_ship_response_200_data.additional_properties = d
        return navigate_ship_response_200_data

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
