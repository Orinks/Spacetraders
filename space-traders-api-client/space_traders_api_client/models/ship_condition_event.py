from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ship_condition_event_component import ShipConditionEventComponent
from ..models.ship_condition_event_symbol import ShipConditionEventSymbol

T = TypeVar("T", bound="ShipConditionEvent")


@_attrs_define
class ShipConditionEvent:
    """An event that represents damage or wear to a ship's reactor, frame, or engine, reducing the condition of the ship.

    Attributes:
        symbol (ShipConditionEventSymbol):
        component (ShipConditionEventComponent):
        name (str): The name of the event.
        description (str): A description of the event.
    """

    symbol: ShipConditionEventSymbol
    component: ShipConditionEventComponent
    name: str
    description: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol.value

        component = self.component.value

        name = self.name

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "component": component,
                "name": name,
                "description": description,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        symbol = ShipConditionEventSymbol(d.pop("symbol"))

        component = ShipConditionEventComponent(d.pop("component"))

        name = d.pop("name")

        description = d.pop("description")

        ship_condition_event = cls(
            symbol=symbol,
            component=component,
            name=name,
            description=description,
        )

        ship_condition_event.additional_properties = d
        return ship_condition_event

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
