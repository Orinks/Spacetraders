from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.agent import Agent
    from ..models.ship import Ship
    from ..models.shipyard_transaction import ShipyardTransaction


T = TypeVar("T", bound="PurchaseShipResponse201Data")


@_attrs_define
class PurchaseShipResponse201Data:
    """
    Attributes:
        agent (Agent): Agent details.
        ship (Ship): Ship details.
        transaction (ShipyardTransaction): Results of a transaction with a shipyard.
    """

    agent: "Agent"
    ship: "Ship"
    transaction: "ShipyardTransaction"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent = self.agent.to_dict()

        ship = self.ship.to_dict()

        transaction = self.transaction.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent": agent,
                "ship": ship,
                "transaction": transaction,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.agent import Agent
        from ..models.ship import Ship
        from ..models.shipyard_transaction import ShipyardTransaction

        d = src_dict.copy()
        agent = Agent.from_dict(d.pop("agent"))

        ship = Ship.from_dict(d.pop("ship"))

        transaction = ShipyardTransaction.from_dict(d.pop("transaction"))

        purchase_ship_response_201_data = cls(
            agent=agent,
            ship=ship,
            transaction=transaction,
        )

        purchase_ship_response_201_data.additional_properties = d
        return purchase_ship_response_201_data

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
