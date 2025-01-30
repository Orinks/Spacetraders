from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.extraction_yield import ExtractionYield


T = TypeVar("T", bound="Extraction")


@_attrs_define
class Extraction:
    """Extraction details.

    Attributes:
        ship_symbol (str): Symbol of the ship that executed the extraction.
        yield_ (ExtractionYield): A yield from the extraction operation.
    """

    ship_symbol: str
    yield_: "ExtractionYield"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ship_symbol = self.ship_symbol

        yield_ = self.yield_.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "shipSymbol": ship_symbol,
                "yield": yield_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.extraction_yield import ExtractionYield

        d = src_dict.copy()
        ship_symbol = d.pop("shipSymbol")

        yield_ = ExtractionYield.from_dict(d.pop("yield"))

        extraction = cls(
            ship_symbol=ship_symbol,
            yield_=yield_,
        )

        extraction.additional_properties = d
        return extraction

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
