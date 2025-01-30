from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RefuelShipBody")


@_attrs_define
class RefuelShipBody:
    """
    Attributes:
        units (Union[Unset, int]): The amount of fuel to fill in the ship's tanks. When not specified, the ship will be
            refueled to its maximum fuel capacity. If the amount specified is greater than the ship's remaining capacity,
            the ship will only be refueled to its maximum fuel capacity. The amount specified is not in market units but in
            ship fuel units. Example: 100.
        from_cargo (Union[Unset, bool]): Wether to use the FUEL thats in your cargo or not. Default: false
    """

    units: Union[Unset, int] = UNSET
    from_cargo: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        units = self.units

        from_cargo = self.from_cargo

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if units is not UNSET:
            field_dict["units"] = units
        if from_cargo is not UNSET:
            field_dict["fromCargo"] = from_cargo

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        units = d.pop("units", UNSET)

        from_cargo = d.pop("fromCargo", UNSET)

        refuel_ship_body = cls(
            units=units,
            from_cargo=from_cargo,
        )

        refuel_ship_body.additional_properties = d
        return refuel_ship_body

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
