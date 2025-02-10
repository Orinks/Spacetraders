"""
Trade route and market management for SpaceTraders
"""
import logging
from typing import List, Optional

from space_traders_api_client import AuthenticatedClient
from space_traders_api_client.api.fleet import (
    purchase_cargo,
    sell_cargo,
)
from space_traders_api_client.api.systems import (
    get_system_waypoints,
    get_systems,
    get_market,
    get_waypoint,
)
from space_traders_api_client.models.market import Market
from space_traders_api_client.models.ship import Ship
from space_traders_api_client.models.waypoint_trait_symbol import (
    WaypointTraitSymbol,
)
from space_traders_api_client.models import (
    purchase_cargo_purchase_cargo_request as cargo_request,
    sell_cargo_sell_cargo_request as sell_request,
    trade_symbol as trade_types
)

from .market_analyzer import MarketAnalyzer, TradeOpportunity
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class TradeManager:
    """Manages market analysis and trade execution"""

    def __init__(
        self,
        client: AuthenticatedClient,
        market_analyzer: MarketAnalyzer
    ):
        """Initialize TradeManager

        Args:
            client: Authenticated API client
            market_analyzer: Market analysis component
        """
        self.client = client
        self.market_analyzer = market_analyzer
        self.rate_limiter = RateLimiter()

    async def get_market_details(self, waypoint_symbol: str) -> Optional[Market]:
        """Get details for a specific market
        
        Args:
            waypoint_symbol: Symbol of waypoint to get market data for
            
        Returns:
            Optional[Market]: Market data if available
        """
        try:
            system_symbol = "-".join(waypoint_symbol.split("-")[:2])
            response = await self.rate_limiter.execute_with_retry(
                get_market.asyncio_detailed,
                task_name="get_market_details",
                system_symbol=system_symbol,
                waypoint_symbol=waypoint_symbol,
                client=self.client
            )
            if response.status_code == 200 and response.parsed:
                return response.parsed.data
            return None
        except Exception as e:
            logger.error(f"Error getting market details: {e}")
            return None

    async def update_market_data(self, waypoint_symbol: str) -> bool:
        """Update market data for analysis
        
        Args:
            waypoint_symbol: Symbol of waypoint to update
            
        Returns:
            bool: True if market was updated successfully
        """
        try:
            # Extract system symbol from waypoint symbol (format: SYSTEM-X-X)
            system_symbol = "-".join(waypoint_symbol.split("-")[:2])
            
            # Get waypoint info first to check if it has a marketplace
            waypoint_response = await self.rate_limiter.execute_with_retry(
                get_waypoint.asyncio_detailed,
                task_name="get_waypoint",
                system_symbol=system_symbol,
                waypoint_symbol=waypoint_symbol,
                client=self.client
            )
            
            if waypoint_response.status_code != 200 or not waypoint_response.parsed:
                logger.error(f"Failed to get waypoint info for {waypoint_symbol}")
                return False
                
            # Check if waypoint has marketplace trait
            if not any(
                trait.symbol == WaypointTraitSymbol.MARKETPLACE 
                for trait in waypoint_response.parsed.data.traits
            ):
                logger.info(f"Waypoint {waypoint_symbol} has no marketplace")
                return False
            
            # Has marketplace, get market data
            response = await self.rate_limiter.execute_with_retry(
                get_market.asyncio_detailed,
                task_name="update_market_data",
                system_symbol=system_symbol,
                waypoint_symbol=waypoint_symbol,
                client=self.client
            )
            if response.status_code == 200 and response.parsed:
                self.market_analyzer.update_market_data(response.parsed.data)
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
            return False

    async def find_best_trade_route(
        self,
        ship: Ship,
        min_profit: int = 100
    ) -> Optional[TradeOpportunity]:
        """Find the most profitable trade route for a ship
        
        Args:
            ship: The ship to find a trade route for
            min_profit: Minimum profit per unit required
            
        Returns:
            Optional[TradeOpportunity]: Best trade opportunity found
        """
        try:
            # First check if the current market has data
            current_market_response = await self.get_market_details(ship.nav.waypoint_symbol)
            
            markets: List[Market] = []
            if current_market_response is not None:
                markets.append(current_market_response)
                logger.info(f"Found market at current location {ship.nav.waypoint_symbol}")
                
                if current_market_response.trade_goods:
                    logger.info(f"Current market has {len(current_market_response.trade_goods)} goods:")
                    for good in current_market_response.trade_goods:
                        logger.info(f"- {good.symbol}: {good.type_} {good.supply}")
               
            # Get all waypoints in current system
            system_symbol = "-".join(ship.nav.waypoint_symbol.split("-")[:2])
            waypoints_response = await self.rate_limiter.execute_with_retry(
                get_system_waypoints.asyncio_detailed,
                task_name="get_system_waypoints",
                system_symbol=system_symbol,
                client=self.client
            )
            
            if waypoints_response.status_code != 200 or not waypoints_response.parsed:
                logger.error(f"Failed to get waypoints for system {system_symbol}")
                return None
                
            # Check each waypoint for a marketplace
            for waypoint in waypoints_response.parsed.data:
                if waypoint.symbol == ship.nav.waypoint_symbol:
                    continue  # Skip current waypoint, already checked
                    
                if WaypointTraitSymbol.MARKETPLACE in [t.symbol for t in waypoint.traits]:
                    market_response = await self.get_market_details(waypoint.symbol)
                    if market_response is not None:
                        markets.append(market_response)
                        logger.info(f"Found market at {waypoint.symbol}")
                        
                        if market_response.trade_goods:
                            logger.info(f"Market has {len(market_response.trade_goods)} goods:")
                            for good in market_response.trade_goods:
                                logger.info(f"- {good.symbol}: {good.type_} {good.supply}")
                        
            if len(markets) > 0:
                logger.info(f"Found {len(markets)} markets in system {system_symbol}")
            else:
                logger.warning(f"No valid markets found in system {system_symbol}")
                        
            # Find trade opportunities
            opportunities = self.market_analyzer.get_trade_opportunities(
                markets=markets,
                min_profit_margin=0.1,  # Lower margin to find more opportunities
                max_distance=100,
                max_units=ship.cargo.capacity  # Consider ship's cargo capacity
            )

            if not opportunities:
                return None

            # Return best opportunity
            return opportunities[0]

        except Exception as e:
            logger.error(f"Error finding trade route: {e}")
            return None

    async def execute_purchase(
        self,
        ship_symbol: str,
        trade_symbol: str,
        units: int
    ) -> bool:
        """Execute a purchase at current market"""
        try:
            body = cargo_request.PurchaseCargoPurchaseCargoRequest(
                symbol=trade_types.TradeSymbol(trade_symbol),
                units=units
            )
            response = await self.rate_limiter.execute_with_retry(
                purchase_cargo.asyncio_detailed,
                task_name="execute_purchase",
                ship_symbol=ship_symbol,
                client=self.client,
                body=body
            )
            return response.status_code == 201
        except Exception as e:
            logger.error(f"Error purchasing cargo: {e}")
            return False

    async def execute_sale(
        self,
        ship_symbol: str,
        trade_symbol: str,
        units: int
    ) -> bool:
        """Execute a sale at current market"""
        try:
            body = sell_request.SellCargoSellCargoRequest(
                symbol=trade_types.TradeSymbol(trade_symbol),
                units=units
            )
            response = await self.rate_limiter.execute_with_retry(
                sell_cargo.asyncio_detailed,
                task_name="execute_sale",
                ship_symbol=ship_symbol,
                client=self.client,
                body=body
            )
            return response.status_code == 201
        except Exception as e:
            logger.error(f"Error selling cargo: {e}")
            return False
