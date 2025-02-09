"""
SpaceTraders automated game client
"""
import asyncio
from datetime import timedelta
from typing import Optional

from space_traders_api_client.models.ship import Ship
from space_traders_api_client.models.ship_nav_status import ShipNavStatus
from space_traders_api_client.models.system import System
from space_traders_api_client.models.agent import Agent
from space_traders_api_client.api.systems import get_systems

from .agent_manager import AgentManager
from .contract_manager import ContractManager
from .fleet_manager import FleetManager
from .market_analyzer import MarketAnalyzer, TradeOpportunity
from .mining import SurveyManager
from .trade_manager import TradeManager


class SpaceTrader:
    """Main game automation class"""

    def __init__(self, token: Optional[str] = None):
        """Initialize the SpaceTrader with optional token

        Args:
            token: Optional API token. If not provided, will read from env var.
        """
        # Initialize managers
        self.agent_manager = AgentManager(token)
        self.fleet_manager = FleetManager(self.agent_manager.client)
        self.market_analyzer = MarketAnalyzer(
            cache_duration=timedelta(minutes=15)
        )
        self.trade_manager = TradeManager(
            self.agent_manager.client,
            self.market_analyzer
        )
        self.contract_manager = ContractManager(self.agent_manager.client)
        self.survey_manager = SurveyManager(
            client=self.agent_manager.client
        )

        # Initialize state
        self.current_system: Optional[System] = None
        self.agent: Optional[Agent] = None

    @property
    def ships(self):
        """Get the current ships dictionary"""
        return self.fleet_manager.ships

    async def initialize(self):
        """Initialize the game state and verify connection"""
        await self.agent_manager.initialize()
        self.agent = self.agent_manager.agent
        await self.fleet_manager.update_fleet()
        await self.contract_manager.update_contracts()

    async def scan_systems(self, limit: int = 5) -> list[System]:
        """Scan nearby star systems

        Args:
            limit: Maximum number of systems to return

        Returns:
            List of System objects

        Raises:
            Exception: If unable to retrieve system data
        """
        try:
            response = await get_systems.asyncio_detailed(
                client=self.agent_manager.client,
                limit=limit
            )

            if response.status_code != 200 or not response.parsed:
                raise Exception(
                    f'Failed to get systems (code: {response.status_code})'
                )

            return response.parsed.data

        except Exception as e:
            print(f"Error scanning systems: {e}")
            return []

    async def manage_fleet(self):
        """Manage fleet operations

        This method:
        1. Updates ship statuses
        2. Updates contracts
        3. Processes each ship
        4. Handles contract deliveries
        """
        try:
            # Update ship statuses
            await self.fleet_manager.update_fleet()

            # Update contracts
            await self.contract_manager.update_contracts()

            # Process each ship
            for ship in self.fleet_manager.ships.values():
                await self._process_ship(ship)

            # Check for deliverable contracts
            for contract_id, contract in self.contract_manager.contracts.items():
                if not contract.accepted:
                    print(f"Found unaccepted contract {contract_id}")
                    await self.contract_manager.accept_contract(contract_id)
                elif contract.fulfilled:
                    print(f"Contract {contract_id} is already fulfilled")
                else:
                    print(f"Processing contract {contract_id}")
                    await self.contract_manager.process_contract(
                        contract,
                        self.fleet_manager.ships,
                        self.survey_manager
                    )

        except Exception as e:
            import traceback
            print('Error managing fleet:')
            print(traceback.format_exc())

    async def _process_ship(self, ship: Ship):
        """Process individual ship actions based on its state

        Args:
            ship: The ship to process
        """
        try:
            if not hasattr(ship, 'nav'):
                print('Ship {} has no navigation data'.format(ship.symbol))
                return

            # If ship is in transit, wait for it to arrive
            if ship.nav.status == ShipNavStatus.IN_TRANSIT:
                print(
                    'Ship {} is in transit to {}'.format(
                        ship.symbol,
                        ship.nav.waypoint_symbol
                    )
                )
                return

            # If ship is at a market waypoint, consider trading
            if ship.nav.status == ShipNavStatus.DOCKED:
                print(
                    'Ship {} is docked at {}'.format(
                        ship.symbol,
                        ship.nav.waypoint_symbol
                    )
                )
                await self._handle_market_actions(ship)
            else:
                print(
                    'Ship {} is {} at {}'.format(
                        ship.symbol,
                        ship.nav.status,
                        ship.nav.waypoint_symbol
                    )
                )

        except Exception as e:
            print('Error processing ship {}: {}'.format(ship.symbol, e))

    async def _handle_market_actions(self, ship: Ship):
        """Handle market-related actions for a ship"""
        try:
            if not hasattr(ship, 'cargo'):
                print('Ship {} has no cargo data'.format(ship.symbol))
                return

            print('Analyzing market options for ship {}'.format(ship.symbol))
            print('Current cargo: {}/{} units'.format(
                ship.cargo.units,
                ship.cargo.capacity
            ))

            # Update market data
            await self.trade_manager.update_market_data(
                ship.nav.waypoint_symbol
            )

            # Get market insights
            insights = self.market_analyzer.get_market_insights(
                ship.nav.waypoint_symbol
            )

            # Log recommendations
            if insights.get("recommendations"):
                print("Market recommendations:")
                for rec in insights["recommendations"]:
                    print(f"- {rec}")

            # Find best trade route if cargo space available
            if ship.cargo.units < ship.cargo.capacity:
                best_route = await self.trade_manager.find_best_trade_route(
                    ship.symbol
                )
                if best_route:
                    print(
                        f"Found route: {best_route.source_market} -> "
                        f"{best_route.target_market}"
                    )
                    print(
                        f"Expected profit: {best_route.profit_per_unit} "
                        f"credits per unit"
                    )
                    await self._execute_trade_route(ship, best_route)

        except Exception as e:
            print(f"Error handling market actions for ship {ship.symbol}: {e}")

    async def _execute_trade_route(
        self,
        ship: Ship,
        route: TradeOpportunity
    ) -> bool:
        """Execute a trade route with a ship"""
        try:
            print(f"Executing trade route with ship {ship.symbol}")

            # Navigate to source market
            success = await self.fleet_manager.navigate_to_waypoint(
                ship.symbol,
                route.source_market
            )
            if not success:
                print("Failed to navigate to source market")
                return False

            # Wait for arrival and dock
            ship_data = await self.fleet_manager.wait_for_arrival(ship.symbol)
            if not ship_data:
                return False

            success = await self.fleet_manager.dock_ship(ship.symbol)
            if not success:
                print("Failed to dock at source market")
                return False

            # Purchase goods
            success = await self.trade_manager.execute_purchase(
                ship.symbol,
                route.trade_symbol,
                route.trade_volume
            )
            if not success:
                print("Failed to purchase goods")
                return False

            # Navigate to target market
            success = await self.fleet_manager.navigate_to_waypoint(
                ship.symbol,
                route.target_market
            )
            if not success:
                print("Failed to navigate to target market")
                return False

            # Wait for arrival and dock
            ship_data = await self.fleet_manager.wait_for_arrival(ship.symbol)
            if not ship_data:
                return False

            success = await self.fleet_manager.dock_ship(ship.symbol)
            if not success:
                print("Failed to dock at target market")
                return False

            # Sell goods
            success = await self.trade_manager.execute_sale(
                ship.symbol,
                route.trade_symbol,
                route.trade_volume
            )
            if not success:
                print("Failed to sell goods")
                return False

            print(
                f"Trade route completed. "
                f"Profit: {route.profit_per_unit * route.trade_volume} credits"
            )
            return True

        except Exception as e:
            print(f"Error executing trade route: {e}")
            return False

    async def trade_loop(self):
        """Main trading loop"""
        while True:
            try:
                print("\n--- Starting new trading cycle ---\n")

                # Update agent status
                await self.agent_manager.get_agent_status()

                # Manage fleet operations
                await self.manage_fleet()

                # Add delay to avoid rate limiting
                print("\nWaiting 5 seconds before next cycle...")
                await asyncio.sleep(5)

            except Exception as e:
                import traceback
                print('Error in trade loop:')
                print(traceback.format_exc())
                print('\nWaiting 10 seconds after error...')
                await asyncio.sleep(10)
