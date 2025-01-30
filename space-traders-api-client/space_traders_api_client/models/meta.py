from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Meta")


@_attrs_define
class Meta:
    """Meta details for pagination.

    Attributes:
        total (int): Shows the total amount of items of this kind that exist.
        page (int): A page denotes an amount of items, offset from the first item. Each page holds an amount of items
            equal to the `limit`. Default: 1.
        limit (int): The amount of items in each page. Limits how many items can be fetched at once. Default: 10.
    """

    total: int
    page: int = 1
    limit: int = 10
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total = self.total

        page = self.page

        limit = self.limit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total": total,
                "page": page,
                "limit": limit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        total = d.pop("total")

        page = d.pop("page")

        limit = d.pop("limit")

        meta = cls(
            total=total,
            page=page,
            limit=limit,
        )

        meta.additional_properties = d
        return meta

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
