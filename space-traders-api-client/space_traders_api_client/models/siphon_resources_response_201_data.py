from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.cooldown import Cooldown
    from ..models.ship_cargo import ShipCargo
    from ..models.ship_condition_event import ShipConditionEvent
    from ..models.siphon import Siphon


T = TypeVar("T", bound="SiphonResourcesResponse201Data")


@_attrs_define
class SiphonResourcesResponse201Data:
    """
    Attributes:
        cooldown (Cooldown): A cooldown is a period of time in which a ship cannot perform certain actions.
        siphon (Siphon): Siphon details.
        cargo (ShipCargo): Ship cargo details.
        events (list['ShipConditionEvent']):
    """

    cooldown: "Cooldown"
    siphon: "Siphon"
    cargo: "ShipCargo"
    events: list["ShipConditionEvent"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cooldown = self.cooldown.to_dict()

        siphon = self.siphon.to_dict()

        cargo = self.cargo.to_dict()

        events = []
        for events_item_data in self.events:
            events_item = events_item_data.to_dict()
            events.append(events_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cooldown": cooldown,
                "siphon": siphon,
                "cargo": cargo,
                "events": events,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.cooldown import Cooldown
        from ..models.ship_cargo import ShipCargo
        from ..models.ship_condition_event import ShipConditionEvent
        from ..models.siphon import Siphon

        d = src_dict.copy()
        cooldown = Cooldown.from_dict(d.pop("cooldown"))

        siphon = Siphon.from_dict(d.pop("siphon"))

        cargo = ShipCargo.from_dict(d.pop("cargo"))

        events = []
        _events = d.pop("events")
        for events_item_data in _events:
            events_item = ShipConditionEvent.from_dict(events_item_data)

            events.append(events_item)

        siphon_resources_response_201_data = cls(
            cooldown=cooldown,
            siphon=siphon,
            cargo=cargo,
            events=events,
        )

        siphon_resources_response_201_data.additional_properties = d
        return siphon_resources_response_201_data

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
