from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetStatusResponse200LeaderboardsMostSubmittedChartsItem")


@_attrs_define
class GetStatusResponse200LeaderboardsMostSubmittedChartsItem:
    """
    Attributes:
        agent_symbol (str): Symbol of the agent.
        chart_count (int): Amount of charts done by the agent.
    """

    agent_symbol: str
    chart_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent_symbol = self.agent_symbol

        chart_count = self.chart_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agentSymbol": agent_symbol,
                "chartCount": chart_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        agent_symbol = d.pop("agentSymbol")

        chart_count = d.pop("chartCount")

        get_status_response_200_leaderboards_most_submitted_charts_item = cls(
            agent_symbol=agent_symbol,
            chart_count=chart_count,
        )

        get_status_response_200_leaderboards_most_submitted_charts_item.additional_properties = d
        return get_status_response_200_leaderboards_most_submitted_charts_item

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
