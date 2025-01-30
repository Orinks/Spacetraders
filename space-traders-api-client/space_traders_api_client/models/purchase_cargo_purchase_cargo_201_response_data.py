from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.agent import Agent
    from ..models.market_transaction import MarketTransaction
    from ..models.ship_cargo import ShipCargo


T = TypeVar("T", bound="PurchaseCargoPurchaseCargo201ResponseData")


@_attrs_define
class PurchaseCargoPurchaseCargo201ResponseData:
    """
    Attributes:
        agent (Agent): Agent details.
        cargo (ShipCargo): Ship cargo details.
        transaction (MarketTransaction): Result of a transaction with a market.
    """

    agent: "Agent"
    cargo: "ShipCargo"
    transaction: "MarketTransaction"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent = self.agent.to_dict()

        cargo = self.cargo.to_dict()

        transaction = self.transaction.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent": agent,
                "cargo": cargo,
                "transaction": transaction,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.agent import Agent
        from ..models.market_transaction import MarketTransaction
        from ..models.ship_cargo import ShipCargo

        d = src_dict.copy()
        agent = Agent.from_dict(d.pop("agent"))

        cargo = ShipCargo.from_dict(d.pop("cargo"))

        transaction = MarketTransaction.from_dict(d.pop("transaction"))

        purchase_cargo_purchase_cargo_201_response_data = cls(
            agent=agent,
            cargo=cargo,
            transaction=transaction,
        )

        purchase_cargo_purchase_cargo_201_response_data.additional_properties = d
        return purchase_cargo_purchase_cargo_201_response_data

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
