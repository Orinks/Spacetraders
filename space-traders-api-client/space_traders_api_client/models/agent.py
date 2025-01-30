from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Agent")


@_attrs_define
class Agent:
    """Agent details.

    Attributes:
        symbol (str): Symbol of the agent.
        headquarters (str): The headquarters of the agent.
        credits_ (int): The number of credits the agent has available. Credits can be negative if funds have been
            overdrawn.
        starting_faction (str): The faction the agent started with.
        ship_count (int): How many ships are owned by the agent.
        account_id (Union[Unset, str]): Account ID that is tied to this agent. Only included on your own agent.
    """

    symbol: str
    headquarters: str
    credits_: int
    starting_faction: str
    ship_count: int
    account_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol

        headquarters = self.headquarters

        credits_ = self.credits_

        starting_faction = self.starting_faction

        ship_count = self.ship_count

        account_id = self.account_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "headquarters": headquarters,
                "credits": credits_,
                "startingFaction": starting_faction,
                "shipCount": ship_count,
            }
        )
        if account_id is not UNSET:
            field_dict["accountId"] = account_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        symbol = d.pop("symbol")

        headquarters = d.pop("headquarters")

        credits_ = d.pop("credits")

        starting_faction = d.pop("startingFaction")

        ship_count = d.pop("shipCount")

        account_id = d.pop("accountId", UNSET)

        agent = cls(
            symbol=symbol,
            headquarters=headquarters,
            credits_=credits_,
            starting_faction=starting_faction,
            ship_count=ship_count,
            account_id=account_id,
        )

        agent.additional_properties = d
        return agent

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
