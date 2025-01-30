from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.scrap_transaction import ScrapTransaction


T = TypeVar("T", bound="GetScrapShipResponse200Data")


@_attrs_define
class GetScrapShipResponse200Data:
    """
    Attributes:
        transaction (ScrapTransaction): Result of a scrap transaction.
    """

    transaction: "ScrapTransaction"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        transaction = self.transaction.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "transaction": transaction,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.scrap_transaction import ScrapTransaction

        d = src_dict.copy()
        transaction = ScrapTransaction.from_dict(d.pop("transaction"))

        get_scrap_ship_response_200_data = cls(
            transaction=transaction,
        )

        get_scrap_ship_response_200_data.additional_properties = d
        return get_scrap_ship_response_200_data

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
