from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.agent import Agent
    from ..models.scrap_transaction import ScrapTransaction


T = TypeVar("T", bound="ScrapShipResponse200Data")


@_attrs_define
class ScrapShipResponse200Data:
    """
    Attributes:
        agent (Agent): Agent details.
        transaction (ScrapTransaction): Result of a scrap transaction.
    """

    agent: "Agent"
    transaction: "ScrapTransaction"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent = self.agent.to_dict()

        transaction = self.transaction.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent": agent,
                "transaction": transaction,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.agent import Agent
        from ..models.scrap_transaction import ScrapTransaction

        d = src_dict.copy()
        agent = Agent.from_dict(d.pop("agent"))

        transaction = ScrapTransaction.from_dict(d.pop("transaction"))

        scrap_ship_response_200_data = cls(
            agent=agent,
            transaction=transaction,
        )

        scrap_ship_response_200_data.additional_properties = d
        return scrap_ship_response_200_data

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
