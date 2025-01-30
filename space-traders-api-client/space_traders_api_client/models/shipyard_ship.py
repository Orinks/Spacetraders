from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.activity_level import ActivityLevel
from ..models.ship_type import ShipType
from ..models.supply_level import SupplyLevel
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ship_engine import ShipEngine
    from ..models.ship_frame import ShipFrame
    from ..models.ship_module import ShipModule
    from ..models.ship_mount import ShipMount
    from ..models.ship_reactor import ShipReactor
    from ..models.shipyard_ship_crew import ShipyardShipCrew


T = TypeVar("T", bound="ShipyardShip")


@_attrs_define
class ShipyardShip:
    """
    Attributes:
        type_ (ShipType): Type of ship
        name (str):
        description (str):
        supply (SupplyLevel): The supply level of a trade good.
        purchase_price (int):
        frame (ShipFrame): The frame of the ship. The frame determines the number of modules and mounting points of the
            ship, as well as base fuel capacity. As the condition of the frame takes more wear, the ship will become more
            sluggish and less maneuverable.
        reactor (ShipReactor): The reactor of the ship. The reactor is responsible for powering the ship's systems and
            weapons.
        engine (ShipEngine): The engine determines how quickly a ship travels between waypoints.
        modules (list['ShipModule']):
        mounts (list['ShipMount']):
        crew (ShipyardShipCrew):
        activity (Union[Unset, ActivityLevel]): The activity level of a trade good. If the good is an import, this
            represents how strong consumption is. If the good is an export, this represents how strong the production is for
            the good. When activity is strong, consumption or production is near maximum capacity. When activity is weak,
            consumption or production is near minimum capacity.
    """

    type_: ShipType
    name: str
    description: str
    supply: SupplyLevel
    purchase_price: int
    frame: "ShipFrame"
    reactor: "ShipReactor"
    engine: "ShipEngine"
    modules: list["ShipModule"]
    mounts: list["ShipMount"]
    crew: "ShipyardShipCrew"
    activity: Union[Unset, ActivityLevel] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        name = self.name

        description = self.description

        supply = self.supply.value

        purchase_price = self.purchase_price

        frame = self.frame.to_dict()

        reactor = self.reactor.to_dict()

        engine = self.engine.to_dict()

        modules = []
        for modules_item_data in self.modules:
            modules_item = modules_item_data.to_dict()
            modules.append(modules_item)

        mounts = []
        for mounts_item_data in self.mounts:
            mounts_item = mounts_item_data.to_dict()
            mounts.append(mounts_item)

        crew = self.crew.to_dict()

        activity: Union[Unset, str] = UNSET
        if not isinstance(self.activity, Unset):
            activity = self.activity.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "name": name,
                "description": description,
                "supply": supply,
                "purchasePrice": purchase_price,
                "frame": frame,
                "reactor": reactor,
                "engine": engine,
                "modules": modules,
                "mounts": mounts,
                "crew": crew,
            }
        )
        if activity is not UNSET:
            field_dict["activity"] = activity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ship_engine import ShipEngine
        from ..models.ship_frame import ShipFrame
        from ..models.ship_module import ShipModule
        from ..models.ship_mount import ShipMount
        from ..models.ship_reactor import ShipReactor
        from ..models.shipyard_ship_crew import ShipyardShipCrew

        d = src_dict.copy()
        type_ = ShipType(d.pop("type"))

        name = d.pop("name")

        description = d.pop("description")

        supply = SupplyLevel(d.pop("supply"))

        purchase_price = d.pop("purchasePrice")

        frame = ShipFrame.from_dict(d.pop("frame"))

        reactor = ShipReactor.from_dict(d.pop("reactor"))

        engine = ShipEngine.from_dict(d.pop("engine"))

        modules = []
        _modules = d.pop("modules")
        for modules_item_data in _modules:
            modules_item = ShipModule.from_dict(modules_item_data)

            modules.append(modules_item)

        mounts = []
        _mounts = d.pop("mounts")
        for mounts_item_data in _mounts:
            mounts_item = ShipMount.from_dict(mounts_item_data)

            mounts.append(mounts_item)

        crew = ShipyardShipCrew.from_dict(d.pop("crew"))

        _activity = d.pop("activity", UNSET)
        activity: Union[Unset, ActivityLevel]
        if isinstance(_activity, Unset):
            activity = UNSET
        else:
            activity = ActivityLevel(_activity)

        shipyard_ship = cls(
            type_=type_,
            name=name,
            description=description,
            supply=supply,
            purchase_price=purchase_price,
            frame=frame,
            reactor=reactor,
            engine=engine,
            modules=modules,
            mounts=mounts,
            crew=crew,
            activity=activity,
        )

        shipyard_ship.additional_properties = d
        return shipyard_ship

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
