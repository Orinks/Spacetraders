from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.faction_symbol import FactionSymbol

if TYPE_CHECKING:
    from ..models.faction_trait import FactionTrait


T = TypeVar("T", bound="Faction")


@_attrs_define
class Faction:
    """Faction details.

    Attributes:
        symbol (FactionSymbol): The symbol of the faction.
        name (str): Name of the faction.
        description (str): Description of the faction.
        headquarters (str): The waypoint in which the faction's HQ is located in.
        traits (list['FactionTrait']): List of traits that define this faction.
        is_recruiting (bool): Whether or not the faction is currently recruiting new agents.
    """

    symbol: FactionSymbol
    name: str
    description: str
    headquarters: str
    traits: list["FactionTrait"]
    is_recruiting: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol.value

        name = self.name

        description = self.description

        headquarters = self.headquarters

        traits = []
        for traits_item_data in self.traits:
            traits_item = traits_item_data.to_dict()
            traits.append(traits_item)

        is_recruiting = self.is_recruiting

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "name": name,
                "description": description,
                "headquarters": headquarters,
                "traits": traits,
                "isRecruiting": is_recruiting,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.faction_trait import FactionTrait

        d = src_dict.copy()
        symbol = FactionSymbol(d.pop("symbol"))

        name = d.pop("name")

        description = d.pop("description")

        headquarters = d.pop("headquarters")

        traits = []
        _traits = d.pop("traits")
        for traits_item_data in _traits:
            traits_item = FactionTrait.from_dict(traits_item_data)

            traits.append(traits_item)

        is_recruiting = d.pop("isRecruiting")

        faction = cls(
            symbol=symbol,
            name=name,
            description=description,
            headquarters=headquarters,
            traits=traits,
            is_recruiting=is_recruiting,
        )

        faction.additional_properties = d
        return faction

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
