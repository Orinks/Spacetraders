"""
Contract management for SpaceTraders
"""
from typing import Dict, Optional, Any, List, Tuple
import logging

from space_traders_api_client import AuthenticatedClient
from space_traders_api_client.models.contract import Contract
from space_traders_api_client.models.ship import Ship
from space_traders_api_client.models.ship_nav_status import ShipNavStatus
from space_traders_api_client.models.navigate_ship_body import NavigateShipBody
from space_traders_api_client.models.refuel_ship_body import RefuelShipBody
from space_traders_api_client.models.waypoint_trait_symbol import WaypointTraitSymbol
from space_traders_api_client.api.contracts import (
    accept_contract,
    deliver_contract,
    fulfill_contract,
    get_contract,
    get_contracts,
)
from space_traders_api_client.api.fleet import (
    orbit_ship,
    navigate_ship,
    get_ship_nav,
    dock_ship,
    refuel_ship,
    get_my_ships
)
from space_traders_api_client.api.systems import (
    get_system_waypoints,
    get_waypoint,
    get_systems
)

from .mining import SurveyManager
from .shipyard import ShipyardManager
from .rate_limiter import RateLimiter
from .fleet_manager import FleetManager

logger = logging.getLogger(__name__)


class ContractManager:
    """Manages contract operations and fulfillment"""

    def __init__(self, client: AuthenticatedClient):
        """Initialize ContractManager

        Args:
            client: Authenticated API client
        """
        self.client = client
        self.contracts: Dict[str, Contract] = {}
        self.shipyard_manager = ShipyardManager(client)
        self.rate_limiter = RateLimiter()

    async def update_contracts(self) -> None:
        """Update the list of available contracts"""
        try:
            response = await self.rate_limiter.execute_with_retry(
                get_contracts.asyncio_detailed,
                task_name="update_contracts",
                client=self.client
            )

            if response.status_code == 200 and response.parsed:
                self.contracts = {
                    contract.id: contract
                    for contract in response.parsed.data
                }
                logger.info(f"Found {len(self.contracts)} active contracts")
            else:
                # Log error but don't throw exception
                logger.error(f"Failed to get contracts: {response.status_code}")
                self.contracts = {}  # Clear contracts on error

        except Exception as e:
            logger.error(f"Error updating contracts: {e}")
            self.contracts = {}  # Clear contracts on error

    async def accept_contract(self, contract_id: str) -> bool:
        """Accept a contract by ID"""
        response = await self.rate_limiter.execute_with_retry(
            accept_contract.asyncio_detailed,
            task_name="accept_contract",
            contract_id=contract_id,
            client=self.client
        )

        if response.status_code == 200:
            logger.info(f"Successfully accepted contract {contract_id}")
            await self.update_contracts()  # Refresh contracts
            return True
        else:
            logger.error(f"Failed to accept contract: {response.status_code}")
            return False

    async def deliver_contract_cargo(
        self,
        contract_id: str,
        ship_symbol: str,
        trade_symbol: str,
        units: int
    ) -> bool:
        """Deliver cargo for a contract

        Args:
            contract_id: ID of the contract
            ship_symbol: Symbol of the ship delivering cargo
            trade_symbol: Symbol of the trade good
            units: Number of units to deliver
        """
        # First dock the ship
        dock_response = await self.rate_limiter.execute_with_retry(
            dock_ship.asyncio_detailed,
            task_name="dock_ship_for_delivery",
            ship_symbol=ship_symbol,
            client=self.client
        )

        if dock_response.status_code != 200:
            logger.error(f"Failed to dock ship: {dock_response.status_code}")
            return False

        # Then deliver the cargo
        response = await self.rate_limiter.execute_with_retry(
            deliver_contract.asyncio_detailed,
            task_name="deliver_contract_cargo",
            contract_id=contract_id,
            client=self.client,
            json_body={
                "shipSymbol": ship_symbol,
                "tradeSymbol": trade_symbol,
                "units": units
            }
        )

        if response.status_code == 200:
            logger.info(
                f"Successfully delivered {units} units of {trade_symbol} "
                f"for contract {contract_id}"
            )
            return True
        else:
            logger.error(f"Failed to deliver cargo: {response.status_code}")
            if response.content:
                logger.error(f"Response: {response.content.decode()}")
            return False

    async def fulfill_contract(self, contract_id: str) -> bool:
        """Fulfill a completed contract"""
        response = await self.rate_limiter.execute_with_retry(
            fulfill_contract.asyncio_detailed,
            task_name="fulfill_contract",
            contract_id=contract_id,
            client=self.client
        )

        if response.status_code == 200:
            logger.info(f"Successfully fulfilled contract {contract_id}")
            await self.update_contracts()  # Refresh contracts
            return True
        else:
            logger.error(f"Failed to fulfill contract: {response.status_code}")
            return False

    async def process_contract(
        self,
        contract: Contract,
        ships: Dict[str, Ship],
        survey_manager: SurveyManager
    ) -> None:
        """Process a specific contract's requirements

        Args:
            contract: The contract to process
            ships: Dictionary of available ships
            survey_manager: Survey manager for mining operations
        """
        try:
            # Check if contract is valid
            if not contract or not hasattr(contract, 'terms'):
                logger.error('Contract has invalid format')
                return

            # Get updated contract status
            get_response = await self.rate_limiter.execute_with_retry(
                get_contract.asyncio_detailed,
                task_name="get_contract_status",
                contract_id=contract.id,
                client=self.client
            )

            if get_response.status_code != 200 or not get_response.parsed:
                logger.error(f"Failed to get contract status: {get_response.status_code}")
                return

            contract_details = get_response.parsed.data

            # Check if already fulfilled
            if contract_details.fulfilled:
                logger.info(f"Contract {contract.id} is already fulfilled")
                await self.fulfill_contract(contract.id)
                return

            # Not yet fulfilled, process requirements
            if not hasattr(contract_details.terms, 'deliver'):
                logger.error('Contract has no delivery requirements')
                return

            for delivery in contract_details.terms.deliver:
                if delivery.units_fulfilled < delivery.units_required:
                    remaining = delivery.units_required - delivery.units_fulfilled
                    logger.info(
                        f"Processing delivery: {remaining} units of "
                        f"{delivery.trade_symbol} to {delivery.destination_symbol}"
                    )

                    # Get ships capable of mining and hauling
                    fleet_manager = FleetManager(self.client)
                    mining_ships, hauler_ships = fleet_manager.get_ships_by_type()

                    if not mining_ships:
                        logger.info("No mining ships available, attempting to purchase one...")
                        current_system = next(iter(ships.values())).nav.system_symbol
                        purchase_response = await self.shipyard_manager.purchase_mining_ship(
                            system_symbol=current_system
                        )
                        if not purchase_response:
                            logger.error("Failed to acquire mining ship")
                            return
                        else:
                            logger.info("Mining ship purchased, restart processing with updated fleet")
                            return

                    if not hauler_ships:
                        logger.info("No hauler ships available, attempting to purchase one...")
                        current_system = mining_ships[0].nav.system_symbol
                        purchase_response = await self.shipyard_manager.purchase_command_ship(
                            system_symbol=current_system,
                            min_cargo_capacity=remaining
                        )
                        if not purchase_response:
                            logger.error("Failed to acquire hauler ship")
                            return
                        else:
                            logger.info("Hauler ship purchased, restart processing with updated fleet")
                            return

                    # Process with each mining ship...
                    return  # TODO: Implement full mining and delivery logic

        except Exception as e:
            contract_id = contract.id if hasattr(contract, 'id') else 'unknown'
            logger.error(f'Error processing contract {contract_id}: {e}')
            logger.error('Full traceback:', exc_info=True)
