from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ship_reactor_symbol import ShipReactorSymbol

if TYPE_CHECKING:
    from ..models.ship_requirements import ShipRequirements


T = TypeVar("T", bound="ShipReactor")


@_attrs_define
class ShipReactor:
    """The reactor of the ship. The reactor is responsible for powering the ship's systems and weapons.

    Attributes:
        symbol (ShipReactorSymbol): Symbol of the reactor.
        name (str): Name of the reactor.
        description (str): Description of the reactor.
        condition (float): The repairable condition of a component. A value of 0 indicates the component needs
            significant repairs, while a value of 1 indicates the component is in near perfect condition. As the condition
            of a component is repaired, the overall integrity of the component decreases.
        integrity (float): The overall integrity of the component, which determines the performance of the component. A
            value of 0 indicates that the component is almost completely degraded, while a value of 1 indicates that the
            component is in near perfect condition. The integrity of the component is non-repairable, and represents
            permanent wear over time.
        power_output (int): The amount of power provided by this reactor. The more power a reactor provides to the ship,
            the lower the cooldown it gets when using a module or mount that taxes the ship's power.
        requirements (ShipRequirements): The requirements for installation on a ship
    """

    symbol: ShipReactorSymbol
    name: str
    description: str
    condition: float
    integrity: float
    power_output: int
    requirements: "ShipRequirements"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol.value

        name = self.name

        description = self.description

        condition = self.condition

        integrity = self.integrity

        power_output = self.power_output

        requirements = self.requirements.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "name": name,
                "description": description,
                "condition": condition,
                "integrity": integrity,
                "powerOutput": power_output,
                "requirements": requirements,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ship_requirements import ShipRequirements

        d = src_dict.copy()
        symbol = ShipReactorSymbol(d.pop("symbol"))

        name = d.pop("name")

        description = d.pop("description")

        condition = d.pop("condition")

        integrity = d.pop("integrity")

        power_output = d.pop("powerOutput")

        requirements = ShipRequirements.from_dict(d.pop("requirements"))

        ship_reactor = cls(
            symbol=symbol,
            name=name,
            description=description,
            condition=condition,
            integrity=integrity,
            power_output=power_output,
            requirements=requirements,
        )

        ship_reactor.additional_properties = d
        return ship_reactor

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
