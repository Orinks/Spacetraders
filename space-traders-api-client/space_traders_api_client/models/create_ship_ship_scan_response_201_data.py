from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.cooldown import Cooldown
    from ..models.scanned_ship import ScannedShip


T = TypeVar("T", bound="CreateShipShipScanResponse201Data")


@_attrs_define
class CreateShipShipScanResponse201Data:
    """
    Attributes:
        cooldown (Cooldown): A cooldown is a period of time in which a ship cannot perform certain actions.
        ships (list['ScannedShip']): List of scanned ships.
    """

    cooldown: "Cooldown"
    ships: list["ScannedShip"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cooldown = self.cooldown.to_dict()

        ships = []
        for ships_item_data in self.ships:
            ships_item = ships_item_data.to_dict()
            ships.append(ships_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cooldown": cooldown,
                "ships": ships,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.cooldown import Cooldown
        from ..models.scanned_ship import ScannedShip

        d = src_dict.copy()
        cooldown = Cooldown.from_dict(d.pop("cooldown"))

        ships = []
        _ships = d.pop("ships")
        for ships_item_data in _ships:
            ships_item = ScannedShip.from_dict(ships_item_data)

            ships.append(ships_item)

        create_ship_ship_scan_response_201_data = cls(
            cooldown=cooldown,
            ships=ships,
        )

        create_ship_ship_scan_response_201_data.additional_properties = d
        return create_ship_ship_scan_response_201_data

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
