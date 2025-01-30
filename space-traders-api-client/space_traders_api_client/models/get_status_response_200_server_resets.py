from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetStatusResponse200ServerResets")


@_attrs_define
class GetStatusResponse200ServerResets:
    """
    Attributes:
        next_ (str): The date and time when the game server will reset.
        frequency (str): How often we intend to reset the game server.
    """

    next_: str
    frequency: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        next_ = self.next_

        frequency = self.frequency

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "next": next_,
                "frequency": frequency,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        next_ = d.pop("next")

        frequency = d.pop("frequency")

        get_status_response_200_server_resets = cls(
            next_=next_,
            frequency=frequency,
        )

        get_status_response_200_server_resets.additional_properties = d
        return get_status_response_200_server_resets

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
