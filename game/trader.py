import asyncio
from datetime import timedelta, datetime # Added datetime
from typing import Optional, List # Added List

from space_traders_api_client.models.ship import Ship
from space_traders_api_client.models.ship_nav_status import ShipNavStatus
from space_traders_api_client.models.system import System
from space_traders_api_client.models.agent import Agent
# Removed: from space_traders_api_client.api.systems import get_systems (now handled by SystemManager)
# Added WaypointType for _manage_mining_ship
from space_traders_api_client.models.waypoint_type import WaypointType

from .agent_manager import AgentManager
from .contract_manager import ContractManager
from .fleet_manager import FleetManager
from .market_analyzer import MarketAnalyzer, TradeOpportunity
from .mining import MiningManager # Updated import
from .trade_manager import TradeManager
from .system_manager import SystemManager # Added SystemManager import
import logging # Added logging

logger = logging.getLogger(__name__) # Added logger

class SpaceTrader:
    """Main game automation class"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize the SpaceTrader with optional token
        
        Args:
            token: Optional API token. If not provided, will read from env var.
        """
        # Initialize managers
        self.agent_manager = AgentManager(token)
        self.system_manager = SystemManager(self.agent_manager.client) # Instantiate SystemManager
        self.fleet_manager = FleetManager(self.agent_manager.client)
        self.market_analyzer = MarketAnalyzer(
            cache_duration=timedelta(minutes=15)
        )
        self.trade_manager = TradeManager(
            self.agent_manager.client,
            self.market_analyzer
        )
        self.contract_manager = ContractManager(self.agent_manager.client)
        # self.survey_manager = SurveyManager( # Old
        #     client=self.agent_manager.client
        # )
        self.mining_manager = MiningManager( # New
            client=self.agent_manager.client,
            system_manager=self.system_manager
        )
        
        # Initialize state
        self.agent: Optional[Agent] = None
        self.last_system_scan_time: Optional[datetime] = None
        self.system_scan_interval: timedelta = timedelta(hours=1) # Scan systems every hour


    @property
    def ships(self):
        """Get the current ships dictionary"""
        return self.fleet_manager.ships

    @property
    def current_system(self) -> Optional[System]:
        """Gets the current system based on agent's headquarters or a default."""
        if self.agent and self.agent.headquarters:
            system_symbol = "-".join(self.agent.headquarters.split("-")[:2])
            return self.system_manager.get_system(system_symbol)
        elif self.system_manager.get_all_systems():
            return self.system_manager.get_all_systems()[0] # Fallback to first known system
        return None


    async def initialize(self):
        """Initialize the game state and verify connection"""
        await self.agent_manager.initialize()
        self.agent = self.agent_manager.agent
        await self.fleet_manager.update_fleet()
        await self.contract_manager.update_contracts()
        # Initial system scan
        await self.scan_systems_and_waypoints(initial_scan=True)


    async def scan_systems_and_waypoints(self, initial_scan: bool = False):
        """Scans for systems and their waypoints using SystemManager."""
        now = datetime.now()
        if not initial_scan and self.last_system_scan_time and \
           (now - self.last_system_scan_time) < self.system_scan_interval:
            logger.info("System scan interval not yet reached. Skipping scan.")
            return

        logger.info("Starting system and waypoint scan...")
        await self.system_manager.discover_systems(limit=10) # Discover initial/nearby systems
        
        discovered_systems = self.system_manager.get_all_systems()
        if not discovered_systems:
            logger.warning("No systems discovered. Waypoint scan will be skipped.")
            return

        # Prioritize scanning current system first if available
        current_system_symbol = None
        if self.agent and self.agent.headquarters:
            current_system_symbol = "-".join(self.agent.headquarters.split("-")[:2])
            system_to_scan = self.system_manager.get_system(current_system_symbol)
            if system_to_scan:
                logger.info(f"Prioritizing waypoint scan for current system: {current_system_symbol}")
                await self.system_manager.discover_waypoints_in_system(current_system_symbol)

        # Scan waypoints for other discovered systems
        for system in discovered_systems:
            if system.symbol == current_system_symbol: # Already scanned
                continue
            logger.info(f"Scanning waypoints for system: {system.symbol}")
            await self.system_manager.discover_waypoints_in_system(system.symbol)

        self.last_system_scan_time = now
        logger.info(f"System and waypoint scan complete. Total systems: {len(self.system_manager.get_all_systems())}, Total waypoints: {self.system_manager.get_total_waypoints_count()}")

    # This method replaces the old scan_systems
    async def get_nearby_systems(self, limit: int = 5) -> List[System]:
        """
        Retrieves a list of nearby or known systems from SystemManager.
        This method no longer performs an API call itself but relies on SystemManager's cache.
        Ensure scan_systems_and_waypoints has been called appropriately.
        """
        all_systems = self.system_manager.get_all_systems()
        # Implement more sophisticated logic if system proximity is available.
        # For now, returns a subset of known systems.
        logger.info(f"Retrieved {len(all_systems[:limit])} systems from SystemManager.")
        return all_systems[:limit]

            
    async def manage_fleet(self):
        """Manage fleet operations
        
        This method:
        1. Updates ship statuses
        2. Updates contracts
        3. Periodically scans systems and waypoints
        4. Processes each ship
        5. Handles contract deliveries
        """
        try:
            # Periodically scan for systems and waypoints
            await self.scan_systems_and_waypoints()

            # Update ship statuses
            await self.fleet_manager.update_fleet()
            
            # Update contracts
            await self.contract_manager.update_contracts()
            
            # Process each ship
            for ship in self.fleet_manager.ships.values():
                await self._process_ship(ship)
                
            # Check for deliverable contracts
            # ... (rest of the method remains the same)
            for contract_id, contract in self.contract_manager.contracts.items():
                if not contract.accepted:
                    logger.info(f"Found unaccepted contract {contract_id}") # Changed print to logger.info
                    await self.contract_manager.accept_contract(contract_id)
                elif contract.fulfilled:
                    logger.info(f"Contract {contract_id} is already fulfilled") # Changed print to logger.info
                else:
                    logger.info(f"Processing contract {contract_id}") # Changed print to logger.info
                    await self.contract_manager.process_contract(
                        contract,
                        self.fleet_manager.ships,
                        self.mining_manager, # Updated to mining_manager
                        self.system_manager
                    )
                    
        except Exception as e:
            import traceback
            logger.error('Error managing fleet:', exc_info=True) # Changed print to logger.error

    async def _process_ship(self, ship: Ship):
        """Process individual ship actions based on its state
        
        Args:
            ship: The ship to process
        """
        try:
            if not hasattr(ship, 'nav'):
                logger.warning('Ship {} has no navigation data'.format(ship.symbol)) # Changed print to logger.warning
                return
                
            if ship.nav.status == ShipNavStatus.IN_TRANSIT:
                logger.info( # Changed print to logger.info
                    'Ship {} is in transit to {}'.format(
                        ship.symbol,
                        ship.nav.waypoint_symbol
                    )
                )
                return
                
            if ship.nav.status == ShipNavStatus.DOCKED:
                logger.info( # Changed print to logger.info
                    'Ship {} is docked at {}'.format(
                        ship.symbol,
                        ship.nav.waypoint_symbol
                    )
                )
                await self._handle_market_actions(ship)
            # This is a simplified role check. Could be based on ship registration or other metadata.
            elif "MINER" in ship.symbol.upper() or "PROBE" in ship.symbol.upper() or "SURVEYOR" in ship.symbol.upper():
                 await self._manage_mining_ship(ship)
            else: # Ship is IN_ORBIT and not a designated miner
                logger.info( # Changed print to logger.info
                    'Ship {} is {} at {}'.format(
                        ship.symbol,
                        ship.nav.status,
                        ship.nav.waypoint_symbol
                    )
                )
                # Potentially add logic here for ships that are IN_ORBIT but not DOCKED,
                # e.g., if they need to dock or perform other actions.
                # For now, we assume market actions require docking.
                # Example: dock if at a marketplace to check trades
                # current_waypoint_obj = self.system_manager.get_waypoint(ship.nav.waypoint_symbol) # Needs get_waypoint by symbol in SystemManager
                # For now, let's find it manually, assuming waypoints are loaded in system_manager
                current_waypoint_obj = None
                for system_obj in self.system_manager.get_all_systems():
                    for wp in self.system_manager.get_waypoints_in_system(system_obj.symbol):
                        if wp.symbol == ship.nav.waypoint_symbol:
                            current_waypoint_obj = wp
                            break
                    if current_waypoint_obj:
                        break
                
                if current_waypoint_obj and WaypointType.MARKETPLACE in [t.symbol for t in current_waypoint_obj.traits]:
                     logger.info(f"Ship {ship.symbol} is in orbit at a marketplace. Docking to check trades.")
                     await self.fleet_manager.dock_ship(ship.symbol)
                     # The ship will be processed again in the next cycle, now docked.


        except Exception as e:
            logger.error('Error processing ship {}: {}'.format(ship.symbol, e), exc_info=True) # Changed print to logger.error

    async def _manage_mining_ship(self, ship: Ship):
        logger.info(f"Managing mining ship: {ship.symbol} at {ship.nav.waypoint_symbol}, Status: {ship.nav.status}")

        # Ensure ship is in orbit or docked to perform actions
        if ship.nav.status == ShipNavStatus.IN_TRANSIT:
            logger.info(f"Mining ship {ship.symbol} is in transit. Waiting for arrival.")
            return # Wait for it to arrive

        # Ensure ship is at a suitable location (e.g., asteroid field)
        # This logic might be more complex, e.g. finding the best target first.

        # A better way to get current waypoint:
        current_waypoint_obj = None
        for system_obj in self.system_manager.get_all_systems():
            for wp in self.system_manager.get_waypoints_in_system(system_obj.symbol):
                if wp.symbol == ship.nav.waypoint_symbol:
                    current_waypoint_obj = wp
                    break
            if current_waypoint_obj:
                break

        if not current_waypoint_obj or current_waypoint_obj.type != WaypointType.ASTEROID_FIELD:
            # Find a suitable mining target if not already at one
            # Define desired resources and priorities (this could be configurable)
            desired_resources = ["IRON_ORE", "ALUMINUM_ORE", "COPPER_ORE", "SILICON_CRYSTALS", "QUARTZ_SAND"]
            priority_map = {"IRON_ORE": 3, "ALUMINUM_ORE": 2, "COPPER_ORE": 2, "SILICON_CRYSTALS": 5, "QUARTZ_SAND":4} # Example priorities

            current_ship_system = ship.nav.system_symbol
            mining_targets = self.mining_manager.find_mining_targets(desired_resources, priority_map, current_ship_system)

            if not mining_targets:
                logger.warning(f"No suitable mining targets found for ship {ship.symbol}.")
                # Perhaps move to a system with more asteroid fields or rescan
                return

            # Select the best target (first in the sorted list)
            target_waypoint_symbol = mining_targets[0].waypoint_symbol
            logger.info(f"Selected mining target for {ship.symbol}: {target_waypoint_symbol} (Resource: {mining_targets[0].resource_type})")

            if ship.nav.waypoint_symbol != target_waypoint_symbol:
                logger.info(f"Navigating mining ship {ship.symbol} to {target_waypoint_symbol}.")
                await self.fleet_manager.navigate_to_waypoint(ship.symbol, target_waypoint_symbol)
                return # Will process on next cycle after arrival
            # If already at the target waypoint, ensure it's an asteroid field
            elif current_waypoint_obj and current_waypoint_obj.type != WaypointType.ASTEROID_FIELD: # current_waypoint_obj might be None if target was in another system
                 logger.warning(f"Ship {ship.symbol} is at {current_waypoint_obj.symbol} which is type {current_waypoint_obj.type}, not ASTEROID_FIELD. Re-evaluating targets.")
                 # This case should ideally be caught by the target selection, but as a safeguard.
                 return


        # Ship is at an asteroid field (current_waypoint_obj should be populated here if ship didn't navigate)
        if not current_waypoint_obj : # Repopulate if ship just arrived
            for system_obj in self.system_manager.get_all_systems():
                for wp in self.system_manager.get_waypoints_in_system(system_obj.symbol):
                    if wp.symbol == ship.nav.waypoint_symbol:
                        current_waypoint_obj = wp
                        break
                if current_waypoint_obj:
                    break

        if not current_waypoint_obj : # Still not found (should not happen if navigation was successful)
            logger.error(f"Could not find waypoint object for {ship.nav.waypoint_symbol} after navigation or current location check.")
            return


        # 1. Refuel if needed (and if possible at this waypoint)
        can_refuel_here = WaypointType.MARKETPLACE in [t.symbol for t in current_waypoint_obj.traits]

        if ship.fuel.current < ship.fuel.capacity * 0.25: # Refuel if less than 25%
            if can_refuel_here:
                logger.info(f"Ship {ship.symbol} fuel low ({ship.fuel.current}/{ship.fuel.capacity}). Attempting to refuel at {ship.nav.waypoint_symbol}.")
                if ship.nav.status != ShipNavStatus.DOCKED:
                    await self.fleet_manager.dock_ship(ship.symbol)

                refuel_success = await self.fleet_manager.refuel_ship(ship.symbol)
                if refuel_success:
                    logger.info(f"Ship {ship.symbol} refueled.")
                else:
                    logger.warning(f"Failed to refuel ship {ship.symbol} at {ship.nav.waypoint_symbol}. Proceeding with caution.")
                # Whether refuel succeeded or not, ensure ship is in orbit for next actions unless delivering
                if ship.nav.status == ShipNavStatus.DOCKED:
                     await self.fleet_manager.orbit_ship(ship.symbol)
                     ship.nav.status = ShipNavStatus.IN_ORBIT # Update local status
            else:
                logger.warning(f"Ship {ship.symbol} fuel low ({ship.fuel.current}/{ship.fuel.capacity}) but cannot refuel at {ship.nav.waypoint_symbol} (no marketplace).")


        # 2. Check cargo space
        if ship.cargo.units >= ship.cargo.capacity:
            logger.info(f"Ship {ship.symbol} cargo is full ({ship.cargo.units}/{ship.cargo.capacity}). Needs to deliver or jettison.")
            # Implement delivery logic here or in a separate method
            # For now, let's assume it will try to deliver to HQ or a contract location.
            hq_waypoint_symbol = self.agent.headquarters if self.agent else None
            if not hq_waypoint_symbol:
                logger.warning(f"Agent HQ not set, cannot determine delivery location for ship {ship.symbol}.")
                return

            if ship.nav.waypoint_symbol != hq_waypoint_symbol:
                 logger.info(f"Navigating ship {ship.symbol} to HQ {hq_waypoint_symbol} to deliver cargo.")
                 await self.fleet_manager.navigate_to_waypoint(ship.symbol, hq_waypoint_symbol)
            else: # Already at HQ
                if ship.nav.status != ShipNavStatus.DOCKED:
                    await self.fleet_manager.dock_ship(ship.symbol)
                # Sell all cargo - this is a simplification.
                # Should ideally sell specific goods based on market or contract.
                if ship.cargo.inventory: # Check if there's anything to sell
                    for item in ship.cargo.inventory:
                        logger.info(f"Attempting to sell {item.units} of {item.symbol} from ship {ship.symbol} at HQ.")
                        sale_success = await self.trade_manager.execute_sale(ship.symbol, item.symbol, item.units)
                        if not sale_success:
                            logger.warning(f"Failed to sell {item.symbol} from ship {ship.symbol} at HQ.")
                            # Consider what to do if sale fails (e.g. jettison if stuck)
                else:
                    logger.info(f"Ship {ship.symbol} is at HQ with full cargo, but inventory is empty. This is unexpected.")

                # After selling, orbit again if planning more actions, or stay docked if cycle ends.
                if ship.nav.status == ShipNavStatus.DOCKED:
                    await self.fleet_manager.orbit_ship(ship.symbol)
                    ship.nav.status = ShipNavStatus.IN_ORBIT # Update local status
            return

        # 3. Survey if no good active surveys for this location / desired resource
        # This requires knowing what resource we are targeting at this waypoint.
        # Let's assume the MiningTarget provided this, or we pick a common one.

        # Determine target resource for this location (e.g. from a MiningTarget or contract)
        # This is a placeholder - replace with actual resource targeting logic.
        targeted_resource = "ALUMINUM_ORE" # Example, should be dynamic

        active_survey_for_resource = self.mining_manager.get_best_survey_for_resource_at_waypoint(
            resource_type=targeted_resource,
            waypoint_symbol=ship.nav.waypoint_symbol
        )

        if not active_survey_for_resource:
            logger.info(f"No good active survey for {targeted_resource} at {ship.nav.waypoint_symbol} for ship {ship.symbol}. Attempting to create one.")
            if ship.nav.status == ShipNavStatus.DOCKED: # Surveying requires orbit
                await self.fleet_manager.orbit_ship(ship.symbol)
                ship.nav.status = ShipNavStatus.IN_ORBIT

            new_survey = await self.mining_manager.create_survey(ship.symbol, ship.nav.waypoint_symbol)
            if new_survey:
                logger.info(f"Ship {ship.symbol} created new survey: {new_survey.signature}")
                active_survey_for_resource = new_survey # Use this new survey for the upcoming extraction
            else:
                logger.warning(f"Ship {ship.symbol} failed to create a survey at {ship.nav.waypoint_symbol}.")
                # Could try mining without survey or wait for cooldown

        # 4. Mine
        if ship.nav.status == ShipNavStatus.DOCKED: # Mining requires orbit
            await self.fleet_manager.orbit_ship(ship.symbol)
            ship.nav.status = ShipNavStatus.IN_ORBIT # Update local status

        logger.info(f"Ship {ship.symbol} attempting to mine at {ship.nav.waypoint_symbol}.")
        extraction_result = await self.mining_manager.extract_resources_at_waypoint(
            ship=ship, # Pass the ship object
            survey=active_survey_for_resource # Pass the best survey if available
        )

        if extraction_result:
            logger.info(f"Ship {ship.symbol} extracted {extraction_result.yield_.units} of {extraction_result.yield_.symbol}.")
            # Ship's cargo is updated within extract_resources_at_waypoint by manager
        else:
            logger.warning(f"Mining attempt by {ship.symbol} at {ship.nav.waypoint_symbol} did not yield results or failed. Cooldown might be active.")
            # Cooldown or other issues are logged by extract_resources_at_waypoint
            
    async def _handle_market_actions(self, ship: Ship):
        """Handle market-related actions for a ship"""
        try:
            if not hasattr(ship, 'cargo'):
                logger.warning('Ship {} has no cargo data'.format(ship.symbol)) # Changed print to logger.warning
                return
                
            logger.info('Analyzing market options for ship {}'.format(ship.symbol)) # Changed print to logger.info
            logger.info('Current cargo: {}/{} units'.format( # Changed print to logger.info
                ship.cargo.units,
                ship.cargo.capacity
            ))
            
            await self.trade_manager.update_market_data(
                ship.nav.waypoint_symbol
            )
            
            insights = self.market_analyzer.get_market_insights(
                ship.nav.waypoint_symbol
            )
            
            if insights.get("recommendations"):
                logger.info("Market recommendations:") # Changed print to logger.info
                for rec in insights["recommendations"]:
                    logger.info(f"- {rec}") # Changed print to logger.info
                    
            if ship.cargo.units < ship.cargo.capacity:
                # Pass SystemManager to find_best_trade_route if it needs to calculate distances
                # based on system/waypoint data. For now, assuming it doesn't.
                best_route = await self.trade_manager.find_best_trade_route(
                    ship_symbol=ship.symbol,
                    # current_system_symbol=self.current_system.symbol if self.current_system else None,
                    # system_manager=self.system_manager # Pass if needed
                )
                if best_route:
                    logger.info( # Changed print to logger.info
                        f"Found route: {best_route.source_market} -> "
                        f"{best_route.target_market}"
                    )
                    logger.info( # Changed print to logger.info
                        f"Expected profit: {best_route.profit_per_unit} "
                        f"credits per unit"
                    )
                    await self._execute_trade_route(ship, best_route)
            
        except Exception as e:
            logger.error(f"Error handling market actions for ship {ship.symbol}: {e}", exc_info=True) # Changed print to logger.error
            
    async def _execute_trade_route(
        self,
        ship: Ship,
        route: TradeOpportunity
    ) -> bool:
        """Execute a trade route with a ship"""
        try:
            logger.info(f"Executing trade route with ship {ship.symbol}") # Changed print to logger.info
            
            # Navigate to source market
            # Check if ship is already at the source market to avoid unnecessary navigation
            if ship.nav.waypoint_symbol != route.source_market:
                logger.info(f"Navigating ship {ship.symbol} to source market {route.source_market}")
                success = await self.fleet_manager.navigate_to_waypoint(
                    ship.symbol,
                    route.source_market
                )
                if not success:
                    logger.error("Failed to navigate to source market") # Changed print to logger.error
                    return False
                
                ship_data = await self.fleet_manager.wait_for_arrival(ship.symbol)
                if not ship_data:
                    return False
                # Update ship object with new nav data
                ship.nav = ship_data.nav

            # Ensure ship is docked at source market
            if ship.nav.status != ShipNavStatus.DOCKED:
                logger.info(f"Docking ship {ship.symbol} at {route.source_market}")
                success = await self.fleet_manager.dock_ship(ship.symbol)
                if not success:
                    logger.error("Failed to dock at source market") # Changed print to logger.error
                    return False
                ship.nav.status = ShipNavStatus.DOCKED # Update local status

            # Purchase goods
            logger.info(f"Purchasing {route.trade_volume} of {route.trade_symbol} at {route.source_market}")
            success = await self.trade_manager.execute_purchase(
                ship.symbol,
                route.trade_symbol,
                route.trade_volume
            )
            if not success:
                logger.error("Failed to purchase goods") # Changed print to logger.error
                return False
                
            # Navigate to target market
            if ship.nav.waypoint_symbol != route.target_market:
                logger.info(f"Navigating ship {ship.symbol} to target market {route.target_market}")
                success = await self.fleet_manager.navigate_to_waypoint(
                    ship.symbol,
                    route.target_market
                )
                if not success:
                    logger.error("Failed to navigate to target market") # Changed print to logger.error
                    return False
                
                ship_data = await self.fleet_manager.wait_for_arrival(ship.symbol)
                if not ship_data:
                    return False
                ship.nav = ship_data.nav

            # Ensure ship is docked at target market
            if ship.nav.status != ShipNavStatus.DOCKED:
                logger.info(f"Docking ship {ship.symbol} at {route.target_market}")
                success = await self.fleet_manager.dock_ship(ship.symbol)
                if not success:
                    logger.error("Failed to dock at target market") # Changed print to logger.error
                    return False
                ship.nav.status = ShipNavStatus.DOCKED # Update local status

            # Sell goods
            logger.info(f"Selling {route.trade_volume} of {route.trade_symbol} at {route.target_market}")
            success = await self.trade_manager.execute_sale(
                ship.symbol,
                route.trade_symbol,
                route.trade_volume
            )
            if not success:
                logger.error("Failed to sell goods") # Changed print to logger.error
                return False
                
            logger.info( # Changed print to logger.info
                f"Trade route completed. "
                f"Profit: {route.profit_per_unit * route.trade_volume} credits"
            )
            # Update agent's credits (optional, API should reflect this)
            # if self.agent:
            # self.agent.credits_ += route.profit_per_unit * route.trade_volume
            return True
            
        except Exception as e:
            logger.error(f"Error executing trade route: {e}", exc_info=True) # Changed print to logger.error
            return False
            
    async def trade_loop(self):
        """Main trading loop"""
        while True:
            try:
                logger.info("\n--- Starting new trading cycle ---\n") # Changed print to logger.info
                
                # Update agent status
                await self.agent_manager.get_agent_status()
                if self.agent_manager.agent: # Update local agent copy
                    self.agent = self.agent_manager.agent
                
                # Manage fleet operations (includes system scan)
                await self.manage_fleet()
                
                # Add delay to avoid rate limiting
                logger.info("\nWaiting 5 seconds before next cycle...") # Changed print to logger.info
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error('Error in trade loop:', exc_info=True) # Changed print to logger.error
                logger.info('\nWaiting 10 seconds after error...') # Changed print to logger.error
                await asyncio.sleep(10)