from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ship_mount_deposits_item import ShipMountDepositsItem
from ..models.ship_mount_symbol import ShipMountSymbol
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ship_requirements import ShipRequirements


T = TypeVar("T", bound="ShipMount")


@_attrs_define
class ShipMount:
    """A mount is installed on the exterier of a ship.

    Attributes:
        symbol (ShipMountSymbol): Symbo of this mount.
        name (str): Name of this mount.
        requirements (ShipRequirements): The requirements for installation on a ship
        description (Union[Unset, str]): Description of this mount.
        strength (Union[Unset, int]): Mounts that have this value, such as mining lasers, denote how powerful this
            mount's capabilities are.
        deposits (Union[Unset, list[ShipMountDepositsItem]]): Mounts that have this value denote what goods can be
            produced from using the mount.
    """

    symbol: ShipMountSymbol
    name: str
    requirements: "ShipRequirements"
    description: Union[Unset, str] = UNSET
    strength: Union[Unset, int] = UNSET
    deposits: Union[Unset, list[ShipMountDepositsItem]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol.value

        name = self.name

        requirements = self.requirements.to_dict()

        description = self.description

        strength = self.strength

        deposits: Union[Unset, list[str]] = UNSET
        if not isinstance(self.deposits, Unset):
            deposits = []
            for deposits_item_data in self.deposits:
                deposits_item = deposits_item_data.value
                deposits.append(deposits_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "name": name,
                "requirements": requirements,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if strength is not UNSET:
            field_dict["strength"] = strength
        if deposits is not UNSET:
            field_dict["deposits"] = deposits

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ship_requirements import ShipRequirements

        d = src_dict.copy()
        symbol = ShipMountSymbol(d.pop("symbol"))

        name = d.pop("name")

        requirements = ShipRequirements.from_dict(d.pop("requirements"))

        description = d.pop("description", UNSET)

        strength = d.pop("strength", UNSET)

        deposits = []
        _deposits = d.pop("deposits", UNSET)
        for deposits_item_data in _deposits or []:
            deposits_item = ShipMountDepositsItem(deposits_item_data)

            deposits.append(deposits_item)

        ship_mount = cls(
            symbol=symbol,
            name=name,
            requirements=requirements,
            description=description,
            strength=strength,
            deposits=deposits,
        )

        ship_mount.additional_properties = d
        return ship_mount

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
