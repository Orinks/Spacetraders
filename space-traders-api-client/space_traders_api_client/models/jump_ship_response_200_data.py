from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.agent import Agent
    from ..models.cooldown import Cooldown
    from ..models.market_transaction import MarketTransaction
    from ..models.ship_nav import ShipNav


T = TypeVar("T", bound="JumpShipResponse200Data")


@_attrs_define
class JumpShipResponse200Data:
    """
    Attributes:
        nav (ShipNav): The navigation information of the ship.
        cooldown (Cooldown): A cooldown is a period of time in which a ship cannot perform certain actions.
        transaction (MarketTransaction): Result of a transaction with a market.
        agent (Agent): Agent details.
    """

    nav: "ShipNav"
    cooldown: "Cooldown"
    transaction: "MarketTransaction"
    agent: "Agent"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        nav = self.nav.to_dict()

        cooldown = self.cooldown.to_dict()

        transaction = self.transaction.to_dict()

        agent = self.agent.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nav": nav,
                "cooldown": cooldown,
                "transaction": transaction,
                "agent": agent,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.agent import Agent
        from ..models.cooldown import Cooldown
        from ..models.market_transaction import MarketTransaction
        from ..models.ship_nav import ShipNav

        d = src_dict.copy()
        nav = ShipNav.from_dict(d.pop("nav"))

        cooldown = Cooldown.from_dict(d.pop("cooldown"))

        transaction = MarketTransaction.from_dict(d.pop("transaction"))

        agent = Agent.from_dict(d.pop("agent"))

        jump_ship_response_200_data = cls(
            nav=nav,
            cooldown=cooldown,
            transaction=transaction,
            agent=agent,
        )

        jump_ship_response_200_data.additional_properties = d
        return jump_ship_response_200_data

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
