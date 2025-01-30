import datetime
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Cooldown")


@_attrs_define
class Cooldown:
    """A cooldown is a period of time in which a ship cannot perform certain actions.

    Attributes:
        ship_symbol (str): The symbol of the ship that is on cooldown
        total_seconds (int): The total duration of the cooldown in seconds
        remaining_seconds (int): The remaining duration of the cooldown in seconds
        expiration (Union[Unset, datetime.datetime]): The date and time when the cooldown expires in ISO 8601 format
    """

    ship_symbol: str
    total_seconds: int
    remaining_seconds: int
    expiration: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ship_symbol = self.ship_symbol

        total_seconds = self.total_seconds

        remaining_seconds = self.remaining_seconds

        expiration: Union[Unset, str] = UNSET
        if not isinstance(self.expiration, Unset):
            expiration = self.expiration.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "shipSymbol": ship_symbol,
                "totalSeconds": total_seconds,
                "remainingSeconds": remaining_seconds,
            }
        )
        if expiration is not UNSET:
            field_dict["expiration"] = expiration

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        ship_symbol = d.pop("shipSymbol")

        total_seconds = d.pop("totalSeconds")

        remaining_seconds = d.pop("remainingSeconds")

        _expiration = d.pop("expiration", UNSET)
        expiration: Union[Unset, datetime.datetime]
        if isinstance(_expiration, Unset):
            expiration = UNSET
        else:
            expiration = isoparse(_expiration)

        cooldown = cls(
            ship_symbol=ship_symbol,
            total_seconds=total_seconds,
            remaining_seconds=remaining_seconds,
            expiration=expiration,
        )

        cooldown.additional_properties = d
        return cooldown

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
