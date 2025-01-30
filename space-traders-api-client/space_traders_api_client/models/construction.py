from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.construction_material import ConstructionMaterial


T = TypeVar("T", bound="Construction")


@_attrs_define
class Construction:
    """The construction details of a waypoint.

    Attributes:
        symbol (str): The symbol of the waypoint.
        materials (list['ConstructionMaterial']): The materials required to construct the waypoint.
        is_complete (bool): Whether the waypoint has been constructed.
    """

    symbol: str
    materials: list["ConstructionMaterial"]
    is_complete: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol

        materials = []
        for materials_item_data in self.materials:
            materials_item = materials_item_data.to_dict()
            materials.append(materials_item)

        is_complete = self.is_complete

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "materials": materials,
                "isComplete": is_complete,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.construction_material import ConstructionMaterial

        d = src_dict.copy()
        symbol = d.pop("symbol")

        materials = []
        _materials = d.pop("materials")
        for materials_item_data in _materials:
            materials_item = ConstructionMaterial.from_dict(materials_item_data)

            materials.append(materials_item)

        is_complete = d.pop("isComplete")

        construction = cls(
            symbol=symbol,
            materials=materials,
            is_complete=is_complete,
        )

        construction.additional_properties = d
        return construction

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
