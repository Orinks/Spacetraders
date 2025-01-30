from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ship_module_symbol import ShipModuleSymbol
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ship_requirements import ShipRequirements


T = TypeVar("T", bound="ShipModule")


@_attrs_define
class ShipModule:
    """A module can be installed in a ship and provides a set of capabilities such as storage space or quarters for crew.
    Module installations are permanent.

        Attributes:
            symbol (ShipModuleSymbol): The symbol of the module.
            name (str): Name of this module.
            description (str): Description of this module.
            requirements (ShipRequirements): The requirements for installation on a ship
            capacity (Union[Unset, int]): Modules that provide capacity, such as cargo hold or crew quarters will show this
                value to denote how much of a bonus the module grants.
            range_ (Union[Unset, int]): Modules that have a range will such as a sensor array show this value to denote how
                far can the module reach with its capabilities.
    """

    symbol: ShipModuleSymbol
    name: str
    description: str
    requirements: "ShipRequirements"
    capacity: Union[Unset, int] = UNSET
    range_: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol.value

        name = self.name

        description = self.description

        requirements = self.requirements.to_dict()

        capacity = self.capacity

        range_ = self.range_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "name": name,
                "description": description,
                "requirements": requirements,
            }
        )
        if capacity is not UNSET:
            field_dict["capacity"] = capacity
        if range_ is not UNSET:
            field_dict["range"] = range_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ship_requirements import ShipRequirements

        d = src_dict.copy()
        symbol = ShipModuleSymbol(d.pop("symbol"))

        name = d.pop("name")

        description = d.pop("description")

        requirements = ShipRequirements.from_dict(d.pop("requirements"))

        capacity = d.pop("capacity", UNSET)

        range_ = d.pop("range", UNSET)

        ship_module = cls(
            symbol=symbol,
            name=name,
            description=description,
            requirements=requirements,
            capacity=capacity,
            range_=range_,
        )

        ship_module.additional_properties = d
        return ship_module

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
