from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.agent import Agent
    from ..models.repair_transaction import RepairTransaction
    from ..models.ship import Ship


T = TypeVar("T", bound="RepairShipResponse200Data")


@_attrs_define
class RepairShipResponse200Data:
    """
    Attributes:
        agent (Agent): Agent details.
        ship (Ship): Ship details.
        transaction (RepairTransaction): Result of a repair transaction.
    """

    agent: "Agent"
    ship: "Ship"
    transaction: "RepairTransaction"
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
        from ..models.repair_transaction import RepairTransaction
        from ..models.ship import Ship

        d = src_dict.copy()
        agent = Agent.from_dict(d.pop("agent"))

        ship = Ship.from_dict(d.pop("ship"))

        transaction = RepairTransaction.from_dict(d.pop("transaction"))

        repair_ship_response_200_data = cls(
            agent=agent,
            ship=ship,
            transaction=transaction,
        )

        repair_ship_response_200_data.additional_properties = d
        return repair_ship_response_200_data

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
