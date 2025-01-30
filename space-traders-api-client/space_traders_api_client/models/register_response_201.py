from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.register_response_201_data import RegisterResponse201Data


T = TypeVar("T", bound="RegisterResponse201")


@_attrs_define
class RegisterResponse201:
    """
    Attributes:
        data (RegisterResponse201Data):
    """

    data: "RegisterResponse201Data"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.register_response_201_data import RegisterResponse201Data

        d = src_dict.copy()
        data = RegisterResponse201Data.from_dict(d.pop("data"))

        register_response_201 = cls(
            data=data,
        )

        register_response_201.additional_properties = d
        return register_response_201

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
