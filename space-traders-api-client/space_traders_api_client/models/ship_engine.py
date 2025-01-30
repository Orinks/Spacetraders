from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ship_engine_symbol import ShipEngineSymbol

if TYPE_CHECKING:
    from ..models.ship_requirements import ShipRequirements


T = TypeVar("T", bound="ShipEngine")


@_attrs_define
class ShipEngine:
    """The engine determines how quickly a ship travels between waypoints.

    Attributes:
        symbol (ShipEngineSymbol): The symbol of the engine.
        name (str): The name of the engine.
        description (str): The description of the engine.
        condition (float): The repairable condition of a component. A value of 0 indicates the component needs
            significant repairs, while a value of 1 indicates the component is in near perfect condition. As the condition
            of a component is repaired, the overall integrity of the component decreases.
        integrity (float): The overall integrity of the component, which determines the performance of the component. A
            value of 0 indicates that the component is almost completely degraded, while a value of 1 indicates that the
            component is in near perfect condition. The integrity of the component is non-repairable, and represents
            permanent wear over time.
        speed (int): The speed stat of this engine. The higher the speed, the faster a ship can travel from one point to
            another. Reduces the time of arrival when navigating the ship.
        requirements (ShipRequirements): The requirements for installation on a ship
    """

    symbol: ShipEngineSymbol
    name: str
    description: str
    condition: float
    integrity: float
    speed: int
    requirements: "ShipRequirements"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol.value

        name = self.name

        description = self.description

        condition = self.condition

        integrity = self.integrity

        speed = self.speed

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
                "speed": speed,
                "requirements": requirements,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ship_requirements import ShipRequirements

        d = src_dict.copy()
        symbol = ShipEngineSymbol(d.pop("symbol"))

        name = d.pop("name")

        description = d.pop("description")

        condition = d.pop("condition")

        integrity = d.pop("integrity")

        speed = d.pop("speed")

        requirements = ShipRequirements.from_dict(d.pop("requirements"))

        ship_engine = cls(
            symbol=symbol,
            name=name,
            description=description,
            condition=condition,
            integrity=integrity,
            speed=speed,
            requirements=requirements,
        )

        ship_engine.additional_properties = d
        return ship_engine

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
