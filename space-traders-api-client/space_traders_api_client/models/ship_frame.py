from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ship_frame_symbol import ShipFrameSymbol

if TYPE_CHECKING:
    from ..models.ship_requirements import ShipRequirements


T = TypeVar("T", bound="ShipFrame")


@_attrs_define
class ShipFrame:
    """The frame of the ship. The frame determines the number of modules and mounting points of the ship, as well as base
    fuel capacity. As the condition of the frame takes more wear, the ship will become more sluggish and less
    maneuverable.

        Attributes:
            symbol (ShipFrameSymbol): Symbol of the frame.
            name (str): Name of the frame.
            description (str): Description of the frame.
            condition (float): The repairable condition of a component. A value of 0 indicates the component needs
                significant repairs, while a value of 1 indicates the component is in near perfect condition. As the condition
                of a component is repaired, the overall integrity of the component decreases.
            integrity (float): The overall integrity of the component, which determines the performance of the component. A
                value of 0 indicates that the component is almost completely degraded, while a value of 1 indicates that the
                component is in near perfect condition. The integrity of the component is non-repairable, and represents
                permanent wear over time.
            module_slots (int): The amount of slots that can be dedicated to modules installed in the ship. Each installed
                module take up a number of slots, and once there are no more slots, no new modules can be installed.
            mounting_points (int): The amount of slots that can be dedicated to mounts installed in the ship. Each installed
                mount takes up a number of points, and once there are no more points remaining, no new mounts can be installed.
            fuel_capacity (int): The maximum amount of fuel that can be stored in this ship. When refueling, the ship will
                be refueled to this amount.
            requirements (ShipRequirements): The requirements for installation on a ship
    """

    symbol: ShipFrameSymbol
    name: str
    description: str
    condition: float
    integrity: float
    module_slots: int
    mounting_points: int
    fuel_capacity: int
    requirements: "ShipRequirements"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol.value

        name = self.name

        description = self.description

        condition = self.condition

        integrity = self.integrity

        module_slots = self.module_slots

        mounting_points = self.mounting_points

        fuel_capacity = self.fuel_capacity

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
                "moduleSlots": module_slots,
                "mountingPoints": mounting_points,
                "fuelCapacity": fuel_capacity,
                "requirements": requirements,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ship_requirements import ShipRequirements

        d = src_dict.copy()
        symbol = ShipFrameSymbol(d.pop("symbol"))

        name = d.pop("name")

        description = d.pop("description")

        condition = d.pop("condition")

        integrity = d.pop("integrity")

        module_slots = d.pop("moduleSlots")

        mounting_points = d.pop("mountingPoints")

        fuel_capacity = d.pop("fuelCapacity")

        requirements = ShipRequirements.from_dict(d.pop("requirements"))

        ship_frame = cls(
            symbol=symbol,
            name=name,
            description=description,
            condition=condition,
            integrity=integrity,
            module_slots=module_slots,
            mounting_points=mounting_points,
            fuel_capacity=fuel_capacity,
            requirements=requirements,
        )

        ship_frame.additional_properties = d
        return ship_frame

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
