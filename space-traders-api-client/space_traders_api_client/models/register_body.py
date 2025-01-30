from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.faction_symbol import FactionSymbol
from ..types import UNSET, Unset

T = TypeVar("T", bound="RegisterBody")


@_attrs_define
class RegisterBody:
    """
    Attributes:
        faction (FactionSymbol): The symbol of the faction.
        symbol (str): Your desired agent symbol. This will be a unique name used to represent your agent, and will be
            the prefix for your ships. Example: BADGER.
        email (Union[Unset, str]): Your email address. This is used if you reserved your call sign between resets.
    """

    faction: FactionSymbol
    symbol: str
    email: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        faction = self.faction.value

        symbol = self.symbol

        email = self.email

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "faction": faction,
                "symbol": symbol,
            }
        )
        if email is not UNSET:
            field_dict["email"] = email

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        faction = FactionSymbol(d.pop("faction"))

        symbol = d.pop("symbol")

        email = d.pop("email", UNSET)

        register_body = cls(
            faction=faction,
            symbol=symbol,
            email=email,
        )

        register_body.additional_properties = d
        return register_body

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
