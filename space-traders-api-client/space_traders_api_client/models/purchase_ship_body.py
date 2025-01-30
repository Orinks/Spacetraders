from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ship_type import ShipType

T = TypeVar("T", bound="PurchaseShipBody")


@_attrs_define
class PurchaseShipBody:
    """
    Attributes:
        ship_type (ShipType): Type of ship
        waypoint_symbol (str): The symbol of the waypoint you want to purchase the ship at.
    """

    ship_type: ShipType
    waypoint_symbol: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ship_type = self.ship_type.value

        waypoint_symbol = self.waypoint_symbol

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "shipType": ship_type,
                "waypointSymbol": waypoint_symbol,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        ship_type = ShipType(d.pop("shipType"))

        waypoint_symbol = d.pop("waypointSymbol")

        purchase_ship_body = cls(
            ship_type=ship_type,
            waypoint_symbol=waypoint_symbol,
        )

        purchase_ship_body.additional_properties = d
        return purchase_ship_body

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
