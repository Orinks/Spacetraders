from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.system_type import SystemType

T = TypeVar("T", bound="ScannedSystem")


@_attrs_define
class ScannedSystem:
    """Details of a system was that scanned.

    Attributes:
        symbol (str): Symbol of the system.
        sector_symbol (str): Symbol of the system's sector.
        type_ (SystemType): The type of system.
        x (int): Position in the universe in the x axis.
        y (int): Position in the universe in the y axis.
        distance (int): The system's distance from the scanning ship.
    """

    symbol: str
    sector_symbol: str
    type_: SystemType
    x: int
    y: int
    distance: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol

        sector_symbol = self.sector_symbol

        type_ = self.type_.value

        x = self.x

        y = self.y

        distance = self.distance

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "sectorSymbol": sector_symbol,
                "type": type_,
                "x": x,
                "y": y,
                "distance": distance,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        symbol = d.pop("symbol")

        sector_symbol = d.pop("sectorSymbol")

        type_ = SystemType(d.pop("type"))

        x = d.pop("x")

        y = d.pop("y")

        distance = d.pop("distance")

        scanned_system = cls(
            symbol=symbol,
            sector_symbol=sector_symbol,
            type_=type_,
            x=x,
            y=y,
            distance=distance,
        )

        scanned_system.additional_properties = d
        return scanned_system

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
