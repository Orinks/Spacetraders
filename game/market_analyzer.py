"""
Market analysis and trading opportunity detection
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from space_traders_api_client.models.market import Market
from space_traders_api_client.models.market_trade_good import MarketTradeGood
from space_traders_api_client.models.supply_level import SupplyLevel
from space_traders_api_client.models.activity_level import ActivityLevel
from space_traders_api_client.models.market_trade_good_type import (
    MarketTradeGoodType
)
from space_traders_api_client.models.trade_symbol import TradeSymbol


@dataclass
class MarketPriceHistory:
    """Track price history for a good at a specific market"""
    market_symbol: str
    trade_symbol: TradeSymbol
    purchase_prices: List[Tuple[datetime, int]]  # (timestamp, price)
    sell_prices: List[Tuple[datetime, int]]
    volumes: List[Tuple[datetime, int]]
    supply_levels: List[Tuple[datetime, SupplyLevel]]
    activity_levels: List[
        Tuple[datetime, Optional[ActivityLevel]]
    ]  # May be unset

    def add_snapshot(
        self,
        trade_good: MarketTradeGood,
        timestamp: datetime
    ) -> None:
        """Add current market data snapshot"""
        self.purchase_prices.append((timestamp, trade_good.purchase_price))
        self.sell_prices.append((timestamp, trade_good.sell_price))
        self.volumes.append((timestamp, trade_good.trade_volume))
        self.supply_levels.append((timestamp, trade_good.supply))
        self.activity_levels.append((timestamp, trade_good.activity))

    def get_price_trend(self, window_hours: int = 24) -> float:
        """Calculate price trend over time window
        Returns: Trend coefficient (-1 to 1) indicating price direction and strength
        """
        if len(self.purchase_prices) < 2:
            return 0.0

        cutoff = datetime.now() - timedelta(hours=window_hours)
        recent_prices = [
            price for ts, price in self.purchase_prices
            if ts > cutoff
        ]

        if len(recent_prices) < 2:
            return 0.0

        # Calculate simple trend from first to last price
        price_change = recent_prices[-1] - recent_prices[0]
        max_price = max(recent_prices)
        min_price = min(recent_prices)
        price_range = max_price - min_price if max_price != min_price else 1

        return price_change / price_range  # Normalized trend


class TradeOpportunity:
    """Represents a potential trade route between markets"""
    def __init__(
        self,
        trade_symbol: TradeSymbol,
        source_market: str,
        target_market: str,
        purchase_price: int,
        sell_price: int,
        trade_volume: int,
        source_supply: SupplyLevel,
        target_demand: SupplyLevel,
        distance: int
    ):
        self.trade_symbol = trade_symbol
        self.source_market = source_market
        self.target_market = target_market
        self.purchase_price = purchase_price
        self.sell_price = sell_price
        self.trade_volume = trade_volume
        self.source_supply = source_supply
        self.target_demand = target_demand
        self.distance = distance

    @property
    def profit_per_unit(self) -> int:
        """Calculate profit per unit"""
        return self.sell_price - self.purchase_price

    @property
    def total_potential_profit(self) -> int:
        """Calculate total potential profit for max trade volume"""
        return self.profit_per_unit * self.trade_volume

    def score(self) -> float:
        """Calculate opportunity score (0-100)"""
        if self.purchase_price >= self.sell_price:
            return 0.0

        # Base score from profit margin
        margin = (
            (self.sell_price - self.purchase_price) /
            self.purchase_price
        )
        base_score = min(margin * 100, 100)

        # Adjust for supply/demand
        supply_multiplier = {
            SupplyLevel.ABUNDANT: 1.0,
            SupplyLevel.HIGH: 0.8,
            SupplyLevel.MODERATE: 0.6,
            SupplyLevel.LIMITED: 0.4,
            SupplyLevel.SCARCE: 0.2
        }.get(self.source_supply, 0.0)

        demand_multiplier = {
            SupplyLevel.SCARCE: 1.0,
            SupplyLevel.LIMITED: 0.8,
            SupplyLevel.MODERATE: 0.6,
            SupplyLevel.HIGH: 0.4,
            SupplyLevel.ABUNDANT: 0.2
        }.get(self.target_demand, 0.0)

        # Adjust for distance
        distance_factor = max(0.1, 1.0 - (self.distance / 100))

        # Adjust for trade volume
        volume_factor = min(1.0, self.trade_volume / 100)

        final_score = (
            base_score *
            supply_multiplier *
            demand_multiplier *
            distance_factor *
            volume_factor
        )

        return min(100.0, final_score)


class MarketAnalyzer:
    """Analyzes market data and identifies trading opportunities"""

    def __init__(
        self,
        cache_duration: timedelta = timedelta(hours=1)
    ):
        self.price_history: Dict[
            str,
            Dict[TradeSymbol, MarketPriceHistory]
        ] = {}
        self.market_cache: Dict[str, Tuple[datetime, Market]] = {}
        self.cache_duration = cache_duration

    def update_market_data(
        self,
        market: Market,
        timestamp: datetime = None
    ) -> None:
        """Update market data and price history"""
        if timestamp is None:
            timestamp = datetime.now()

        # Update market cache
        self.market_cache[market.symbol] = (timestamp, market)

        # Initialize price history for market if needed
        if market.symbol not in self.price_history:
            self.price_history[market.symbol] = {}

        # Update price history for each trade good
        if market.trade_goods:
            for trade_good in market.trade_goods:
                if trade_good.symbol not in self.price_history[market.symbol]:
                    self.price_history[market.symbol][trade_good.symbol] = (
                        MarketPriceHistory(
                            market_symbol=market.symbol,
                            trade_symbol=trade_good.symbol,
                            purchase_prices=[],
                            sell_prices=[],
                            volumes=[],
                            supply_levels=[],
                            activity_levels=[]
                        )
                    )
                self.price_history[market.symbol][trade_good.symbol].add_snapshot(
                    trade_good,
                    timestamp
                )

    def get_trade_opportunities(
        self,
        markets: List[Market],
        min_profit_margin: float = 0.1,
        max_distance: int = 100,
        max_units: int = None
    ) -> List[TradeOpportunity]:
        """Identify profitable trade opportunities between markets
        
        Args:
            markets: List of markets to analyze
            min_profit_margin: Minimum acceptable profit margin
            max_distance: Maximum travel distance to consider
            max_units: Maximum units that can be transported (e.g. ship cargo capacity)
            
        Returns:
            List[TradeOpportunity]: Sorted list of trade opportunities
        """
        opportunities = []

        for source_market in markets:
            if not source_market.trade_goods:
                print(f"Market {source_market.symbol} has no trade goods")
                continue

            print(f"\nChecking trades at {source_market.symbol}:")
            for good in source_market.trade_goods:
                print(f"- {good.symbol}: {good.type_}")
                print(f"  Buy: {good.purchase_price} | Sell: {good.sell_price}")
                print(f"  Supply: {good.supply} | Volume: {good.trade_volume}")

            # Consider both exports and exchange goods as potential purchases
            for trade_good in source_market.trade_goods:
                if trade_good.type_ in [
                    MarketTradeGoodType.EXPORT,
                    MarketTradeGoodType.EXCHANGE
                ]:
                    # Look for profitable sales at other markets
                    for target_market in markets:
                        if target_market.symbol == source_market.symbol:
                            continue

                        # Find matching import/exchange good
                        target_good = next(
                            (g for g in (target_market.trade_goods or [])
                             if g.symbol == trade_good.symbol and
                             g.type_ in (
                                 MarketTradeGoodType.IMPORT,
                                 MarketTradeGoodType.EXCHANGE
                             ) and
                             g.sell_price > trade_good.purchase_price),  # Must make profit
                            None
                        )

                        if not target_good:
                            continue

                        # Calculate profit margin and check if worth trading
                        purchase_price = trade_good.purchase_price
                        sell_price = target_good.sell_price
                        profit = sell_price - purchase_price
                        
                        if purchase_price == 0:
                            continue  # Avoid division by zero
                            
                        profit_margin = profit / purchase_price
                        
                        if profit_margin < min_profit_margin:
                            continue
                            
                        # Calculate valid trade volume
                        volume = min(
                            trade_good.trade_volume,
                            target_good.trade_volume
                        )
                        if max_units is not None:
                            volume = min(volume, max_units)
                            
                        if volume <= 0:
                            continue

                        distance = 50  # Placeholder distance
                        if distance > max_distance:
                            continue

                        opportunity = TradeOpportunity(
                            trade_symbol=trade_good.symbol,
                            source_market=source_market.symbol,
                            target_market=target_market.symbol,
                            purchase_price=purchase_price,
                            sell_price=sell_price,
                            trade_volume=volume,
                            source_supply=trade_good.supply,
                            target_demand=target_good.supply,
                            distance=distance
                        )

                        print(f"\nFound potential trade:")
                        print(f"- Good: {opportunity.trade_symbol}")
                        print(f"- Route: {opportunity.source_market} -> {opportunity.target_market}")
                        print(f"- Buy: {purchase_price} | Sell: {sell_price}")
                        print(f"- Profit/unit: {opportunity.profit_per_unit}")
                        print(f"- Volume: {volume}")
                        print(f"- Total potential profit: {opportunity.total_potential_profit}")
                        print(f"- Score: {opportunity.score()}")

                        opportunities.append(opportunity)

        # Sort by opportunity score
        opportunities.sort(key=lambda x: x.score(), reverse=True)
        print(f"\nFound {len(opportunities)} total trade opportunities")
        return opportunities

    def get_market_insights(self, market_symbol: str) -> Dict[str, any]:
        """Get market analysis insights"""
        if market_symbol not in self.price_history:
            return {}

        insights = {
            "price_trends": {},
            "trading_volume": {},
            "supply_levels": {},
            "recommendations": []
        }

        for trade_symbol, history in self.price_history[market_symbol].items():
            # Calculate price trends
            trend = history.get_price_trend()
            insights["price_trends"][trade_symbol.value] = {
                "trend": trend,
                "strength": abs(trend),
                "direction": (
                    "up" if trend > 0
                    else "down" if trend < 0
                    else "stable"
                )
            }

            # Get latest trading volume
            if history.volumes:
                insights["trading_volume"][trade_symbol.value] = (
                    history.volumes[-1][1]
                )

            # Get latest supply level
            if history.supply_levels:
                insights["supply_levels"][trade_symbol.value] = (
                    history.supply_levels[-1][1].value
                )

            # Generate recommendations
            if trend > 0.5:
                insights["recommendations"].append(
                    f"Consider selling {trade_symbol.value} - "
                    "Strong upward price trend"
                )
            elif trend < -0.5:
                insights["recommendations"].append(
                    f"Consider buying {trade_symbol.value} - "
                    "Strong downward price trend"
                )

        return insights
