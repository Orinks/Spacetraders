"""
Trade route and market management for SpaceTraders
"""
from typing import List, Optional

from space_traders_api_client import AuthenticatedClient
from space_traders_api_client.api.fleet import (
    get_market,
    purchase_cargo,
    sell_cargo,
)
from space_traders_api_client.api.systems import (
    get_system_waypoints,
    get_systems,
)
from space_traders_api_client.models.market import Market
from space_traders_api_client.models.waypoint_trait_symbol import (
    WaypointTraitSymbol,
)

from .market_analyzer import MarketAnalyzer, TradeOpportunity


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
        
    async def update_market_data(self, waypoint_symbol: str) -> None:
        """Update market data for analysis"""
        try:
            response = await get_market.asyncio_detailed(
                waypoint_symbol=waypoint_symbol,
                client=self.client,
                json_body={}
            )
            if response.status_code == 200 and response.parsed:
                self.market_analyzer.update_market_data(response.parsed.data)
        except Exception as e:
            print(f"Error updating market data: {e}")

    async def find_best_trade_route(
        self,
        ship_symbol: str,
        min_profit: int = 100
    ) -> Optional[TradeOpportunity]:
        """Find the most profitable trade route for a ship"""
        try:
            # Get nearby systems
            systems_response = await get_systems.asyncio_detailed(
                client=self.client,
                json_body={},
                limit=5
            )
            if (
                systems_response.status_code != 200 
                or not systems_response.parsed
            ):
                return None
                
            systems = systems_response.parsed.data
            
            # Get market data for each system
            markets: List[Market] = []
            for system in systems:
                waypoints = await get_system_waypoints.asyncio_detailed(
                    system_symbol=system.symbol,
                    client=self.client,
                    json_body={}
                )
                if waypoints.status_code != 200 or not waypoints.parsed:
                    continue
                    
                for waypoint in waypoints.parsed.data:
                    if WaypointTraitSymbol.MARKETPLACE in [
                        t.symbol for t in waypoint.traits
                    ]:
                        market_response = await get_market.asyncio_detailed(
                            waypoint_symbol=waypoint.symbol,
                            client=self.client,
                            json_body={}
                        )
                        if (
                            market_response.status_code == 200 
                            and market_response.parsed
                        ):
                            markets.append(market_response.parsed.data)
                            
            # Find trade opportunities
            opportunities = self.market_analyzer.get_trade_opportunities(
                markets=markets,
                min_profit_margin=0.2,
                max_distance=100
            )
            
            if not opportunities:
                return None
                
            # Return best opportunity
            return opportunities[0]
            
        except Exception as e:
            print(f"Error finding trade route: {e}")
            return None
            
    async def execute_purchase(
        self,
        ship_symbol: str,
        trade_symbol: str,
        units: int
    ) -> bool:
        """Execute a purchase at current market"""
        try:
            response = await purchase_cargo.asyncio_detailed(
                ship_symbol=ship_symbol,
                client=self.client,
                json_body={
                    "symbol": trade_symbol,
                    "units": units
                }
            )
            return response.status_code == 201
        except Exception as e:
            print(f"Error purchasing cargo: {e}")
            return False
            
    async def execute_sale(
        self,
        ship_symbol: str,
        trade_symbol: str,
        units: int
    ) -> bool:
        """Execute a sale at current market"""
        try:
            response = await sell_cargo.asyncio_detailed(
                ship_symbol=ship_symbol,
                client=self.client,
                json_body={
                    "symbol": trade_symbol,
                    "units": units
                }
            )
            return response.status_code == 201
        except Exception as e:
            print(f"Error selling cargo: {e}")
            return False