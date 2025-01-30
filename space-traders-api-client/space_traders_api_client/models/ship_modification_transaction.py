import datetime
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="ShipModificationTransaction")


@_attrs_define
class ShipModificationTransaction:
    """Result of a transaction for a ship modification, such as installing a mount or a module.

    Attributes:
        waypoint_symbol (str): The symbol of the waypoint where the transaction took place.
        ship_symbol (str): The symbol of the ship that made the transaction.
        trade_symbol (str): The symbol of the trade good.
        total_price (int): The total price of the transaction.
        timestamp (datetime.datetime): The timestamp of the transaction.
    """

    waypoint_symbol: str
    ship_symbol: str
    trade_symbol: str
    total_price: int
    timestamp: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        waypoint_symbol = self.waypoint_symbol

        ship_symbol = self.ship_symbol

        trade_symbol = self.trade_symbol

        total_price = self.total_price

        timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "waypointSymbol": waypoint_symbol,
                "shipSymbol": ship_symbol,
                "tradeSymbol": trade_symbol,
                "totalPrice": total_price,
                "timestamp": timestamp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        waypoint_symbol = d.pop("waypointSymbol")

        ship_symbol = d.pop("shipSymbol")

        trade_symbol = d.pop("tradeSymbol")

        total_price = d.pop("totalPrice")

        timestamp = isoparse(d.pop("timestamp"))

        ship_modification_transaction = cls(
            waypoint_symbol=waypoint_symbol,
            ship_symbol=ship_symbol,
            trade_symbol=trade_symbol,
            total_price=total_price,
            timestamp=timestamp,
        )

        ship_modification_transaction.additional_properties = d
        return ship_modification_transaction

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
