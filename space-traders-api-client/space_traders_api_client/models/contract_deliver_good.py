from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ContractDeliverGood")


@_attrs_define
class ContractDeliverGood:
    """The details of a delivery contract. Includes the type of good, units needed, and the destination.

    Attributes:
        trade_symbol (str): The symbol of the trade good to deliver.
        destination_symbol (str): The destination where goods need to be delivered.
        units_required (int): The number of units that need to be delivered on this contract.
        units_fulfilled (int): The number of units fulfilled on this contract.
    """

    trade_symbol: str
    destination_symbol: str
    units_required: int
    units_fulfilled: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        trade_symbol = self.trade_symbol

        destination_symbol = self.destination_symbol

        units_required = self.units_required

        units_fulfilled = self.units_fulfilled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tradeSymbol": trade_symbol,
                "destinationSymbol": destination_symbol,
                "unitsRequired": units_required,
                "unitsFulfilled": units_fulfilled,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        trade_symbol = d.pop("tradeSymbol")

        destination_symbol = d.pop("destinationSymbol")

        units_required = d.pop("unitsRequired")

        units_fulfilled = d.pop("unitsFulfilled")

        contract_deliver_good = cls(
            trade_symbol=trade_symbol,
            destination_symbol=destination_symbol,
            units_required=units_required,
            units_fulfilled=units_fulfilled,
        )

        contract_deliver_good.additional_properties = d
        return contract_deliver_good

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
