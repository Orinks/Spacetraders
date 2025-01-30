from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.activity_level import ActivityLevel
from ..models.market_trade_good_type import MarketTradeGoodType
from ..models.supply_level import SupplyLevel
from ..models.trade_symbol import TradeSymbol
from ..types import UNSET, Unset

T = TypeVar("T", bound="MarketTradeGood")


@_attrs_define
class MarketTradeGood:
    """
    Attributes:
        symbol (TradeSymbol): The good's symbol.
        type_ (MarketTradeGoodType): The type of trade good (export, import, or exchange).
        trade_volume (int): This is the maximum number of units that can be purchased or sold at this market in a single
            trade for this good. Trade volume also gives an indication of price volatility. A market with a low trade volume
            will have large price swings, while high trade volume will be more resilient to price changes.
        supply (SupplyLevel): The supply level of a trade good.
        purchase_price (int): The price at which this good can be purchased from the market.
        sell_price (int): The price at which this good can be sold to the market.
        activity (Union[Unset, ActivityLevel]): The activity level of a trade good. If the good is an import, this
            represents how strong consumption is. If the good is an export, this represents how strong the production is for
            the good. When activity is strong, consumption or production is near maximum capacity. When activity is weak,
            consumption or production is near minimum capacity.
    """

    symbol: TradeSymbol
    type_: MarketTradeGoodType
    trade_volume: int
    supply: SupplyLevel
    purchase_price: int
    sell_price: int
    activity: Union[Unset, ActivityLevel] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol.value

        type_ = self.type_.value

        trade_volume = self.trade_volume

        supply = self.supply.value

        purchase_price = self.purchase_price

        sell_price = self.sell_price

        activity: Union[Unset, str] = UNSET
        if not isinstance(self.activity, Unset):
            activity = self.activity.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "type": type_,
                "tradeVolume": trade_volume,
                "supply": supply,
                "purchasePrice": purchase_price,
                "sellPrice": sell_price,
            }
        )
        if activity is not UNSET:
            field_dict["activity"] = activity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        symbol = TradeSymbol(d.pop("symbol"))

        type_ = MarketTradeGoodType(d.pop("type"))

        trade_volume = d.pop("tradeVolume")

        supply = SupplyLevel(d.pop("supply"))

        purchase_price = d.pop("purchasePrice")

        sell_price = d.pop("sellPrice")

        _activity = d.pop("activity", UNSET)
        activity: Union[Unset, ActivityLevel]
        if isinstance(_activity, Unset):
            activity = UNSET
        else:
            activity = ActivityLevel(_activity)

        market_trade_good = cls(
            symbol=symbol,
            type_=type_,
            trade_volume=trade_volume,
            supply=supply,
            purchase_price=purchase_price,
            sell_price=sell_price,
            activity=activity,
        )

        market_trade_good.additional_properties = d
        return market_trade_good

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
