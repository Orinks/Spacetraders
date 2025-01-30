from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.agent import Agent
    from ..models.ship_cargo import ShipCargo
    from ..models.ship_modification_transaction import ShipModificationTransaction
    from ..models.ship_mount import ShipMount


T = TypeVar("T", bound="RemoveMountRemoveMount201ResponseData")


@_attrs_define
class RemoveMountRemoveMount201ResponseData:
    """
    Attributes:
        agent (Agent): Agent details.
        mounts (list['ShipMount']): List of installed mounts after the removal of the selected mount.
        cargo (ShipCargo): Ship cargo details.
        transaction (ShipModificationTransaction): Result of a transaction for a ship modification, such as installing a
            mount or a module.
    """

    agent: "Agent"
    mounts: list["ShipMount"]
    cargo: "ShipCargo"
    transaction: "ShipModificationTransaction"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent = self.agent.to_dict()

        mounts = []
        for mounts_item_data in self.mounts:
            mounts_item = mounts_item_data.to_dict()
            mounts.append(mounts_item)

        cargo = self.cargo.to_dict()

        transaction = self.transaction.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent": agent,
                "mounts": mounts,
                "cargo": cargo,
                "transaction": transaction,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.agent import Agent
        from ..models.ship_cargo import ShipCargo
        from ..models.ship_modification_transaction import ShipModificationTransaction
        from ..models.ship_mount import ShipMount

        d = src_dict.copy()
        agent = Agent.from_dict(d.pop("agent"))

        mounts = []
        _mounts = d.pop("mounts")
        for mounts_item_data in _mounts:
            mounts_item = ShipMount.from_dict(mounts_item_data)

            mounts.append(mounts_item)

        cargo = ShipCargo.from_dict(d.pop("cargo"))

        transaction = ShipModificationTransaction.from_dict(d.pop("transaction"))

        remove_mount_remove_mount_201_response_data = cls(
            agent=agent,
            mounts=mounts,
            cargo=cargo,
            transaction=transaction,
        )

        remove_mount_remove_mount_201_response_data.additional_properties = d
        return remove_mount_remove_mount_201_response_data

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
