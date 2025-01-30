from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.ship_cargo_item import ShipCargoItem


T = TypeVar("T", bound="ShipCargo")


@_attrs_define
class ShipCargo:
    """Ship cargo details.

    Attributes:
        capacity (int): The max number of items that can be stored in the cargo hold.
        units (int): The number of items currently stored in the cargo hold.
        inventory (list['ShipCargoItem']): The items currently in the cargo hold.
    """

    capacity: int
    units: int
    inventory: list["ShipCargoItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        capacity = self.capacity

        units = self.units

        inventory = []
        for inventory_item_data in self.inventory:
            inventory_item = inventory_item_data.to_dict()
            inventory.append(inventory_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "capacity": capacity,
                "units": units,
                "inventory": inventory,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ship_cargo_item import ShipCargoItem

        d = src_dict.copy()
        capacity = d.pop("capacity")

        units = d.pop("units")

        inventory = []
        _inventory = d.pop("inventory")
        for inventory_item_data in _inventory:
            inventory_item = ShipCargoItem.from_dict(inventory_item_data)

            inventory.append(inventory_item)

        ship_cargo = cls(
            capacity=capacity,
            units=units,
            inventory=inventory,
        )

        ship_cargo.additional_properties = d
        return ship_cargo

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
