from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetStatusResponse200LeaderboardsMostCreditsItem")


@_attrs_define
class GetStatusResponse200LeaderboardsMostCreditsItem:
    """
    Attributes:
        agent_symbol (str): Symbol of the agent.
        credits_ (int): Amount of credits.
    """

    agent_symbol: str
    credits_: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent_symbol = self.agent_symbol

        credits_ = self.credits_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agentSymbol": agent_symbol,
                "credits": credits_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        agent_symbol = d.pop("agentSymbol")

        credits_ = d.pop("credits")

        get_status_response_200_leaderboards_most_credits_item = cls(
            agent_symbol=agent_symbol,
            credits_=credits_,
        )

        get_status_response_200_leaderboards_most_credits_item.additional_properties = d
        return get_status_response_200_leaderboards_most_credits_item

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
