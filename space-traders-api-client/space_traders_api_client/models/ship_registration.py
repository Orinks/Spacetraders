from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ship_role import ShipRole

T = TypeVar("T", bound="ShipRegistration")


@_attrs_define
class ShipRegistration:
    """The public registration information of the ship

    Attributes:
        name (str): The agent's registered name of the ship
        faction_symbol (str): The symbol of the faction the ship is registered with
        role (ShipRole): The registered role of the ship
    """

    name: str
    faction_symbol: str
    role: ShipRole
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        faction_symbol = self.faction_symbol

        role = self.role.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "factionSymbol": faction_symbol,
                "role": role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        faction_symbol = d.pop("factionSymbol")

        role = ShipRole(d.pop("role"))

        ship_registration = cls(
            name=name,
            faction_symbol=faction_symbol,
            role=role,
        )

        ship_registration.additional_properties = d
        return ship_registration

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
