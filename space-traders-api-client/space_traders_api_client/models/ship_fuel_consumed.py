import datetime
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="ShipFuelConsumed")


@_attrs_define
class ShipFuelConsumed:
    """An object that only shows up when an action has consumed fuel in the process. Shows the fuel consumption data.

    Attributes:
        amount (int): The amount of fuel consumed by the most recent transit or action.
        timestamp (datetime.datetime): The time at which the fuel was consumed.
    """

    amount: int
    timestamp: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        amount = self.amount

        timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount": amount,
                "timestamp": timestamp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        amount = d.pop("amount")

        timestamp = isoparse(d.pop("timestamp"))

        ship_fuel_consumed = cls(
            amount=amount,
            timestamp=timestamp,
        )

        ship_fuel_consumed.additional_properties = d
        return ship_fuel_consumed

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
