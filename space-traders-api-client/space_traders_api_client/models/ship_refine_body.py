from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ship_refine_body_produce import ShipRefineBodyProduce

T = TypeVar("T", bound="ShipRefineBody")


@_attrs_define
class ShipRefineBody:
    """
    Attributes:
        produce (ShipRefineBodyProduce): The type of good to produce out of the refining process.
    """

    produce: ShipRefineBodyProduce
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        produce = self.produce.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "produce": produce,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        produce = ShipRefineBodyProduce(d.pop("produce"))

        ship_refine_body = cls(
            produce=produce,
        )

        ship_refine_body.additional_properties = d
        return ship_refine_body

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
