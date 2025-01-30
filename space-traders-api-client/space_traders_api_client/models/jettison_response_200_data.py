from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.ship_cargo import ShipCargo


T = TypeVar("T", bound="JettisonResponse200Data")


@_attrs_define
class JettisonResponse200Data:
    """
    Attributes:
        cargo (ShipCargo): Ship cargo details.
    """

    cargo: "ShipCargo"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cargo = self.cargo.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cargo": cargo,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ship_cargo import ShipCargo

        d = src_dict.copy()
        cargo = ShipCargo.from_dict(d.pop("cargo"))

        jettison_response_200_data = cls(
            cargo=cargo,
        )

        jettison_response_200_data.additional_properties = d
        return jettison_response_200_data

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
