"""
Fleet and navigation management for SpaceTraders
"""
import asyncio
import logging
from typing import Dict, Optional, List, Tuple

from space_traders_api_client import AuthenticatedClient
from space_traders_api_client.api.fleet import (
    dock_ship,
    get_my_ships,
    navigate_ship,
    orbit_ship,
    refuel_ship,
    transfer_cargo,
)
from space_traders_api_client.models.ship import Ship
from space_traders_api_client.models.ship_nav_status import ShipNavStatus
from space_traders_api_client.models.navigate_ship_body import NavigateShipBody
from space_traders_api_client.models.refuel_ship_body import RefuelShipBody
from space_traders_api_client.models.transfer_cargo_transfer_cargo_request import TransferCargoTransferCargoRequest

from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class FleetManager:
    """Manages ship operations and navigation"""

    def __init__(self, client: AuthenticatedClient):
        """Initialize FleetManager

        Args:
            client: Authenticated API client
        """
        self.client = client
        self.ships: Dict[str, Ship] = {}
        self.rate_limiter = RateLimiter()

    async def update_fleet(self) -> None:
        """Update status of all ships

        Raises:
            Exception: If unable to retrieve ship data after retries
        """
        response = await self.rate_limiter.execute_with_retry(
            get_my_ships.asyncio_detailed,
            task_name="update_fleet",
            client=self.client
        )

        if response.status_code == 200 and response.parsed:
            self.ships = {
                ship.symbol: ship
                for ship in response.parsed.data
            }
            ship_list = "\n".join(f"- {symbol}" for symbol in self.ships.keys())
            logger.info(f"Updated fleet status. Current ships:\n{ship_list}")
        else:
            raise Exception(f'Failed to get ships (code: {response.status_code})')

    def get_ships_by_type(self) -> Tuple[List[Ship], List[Ship]]:
        """Separate ships into mining and command ships based on role and equipment

        Returns:
            Tuple of (mining_ships, command_ships)
        """
        mining_ships = []
        command_ships = []

        for ship in self.ships.values():
            # Check frame and cargo capacity
            if not hasattr(ship, 'frame') or not hasattr(ship, 'cargo'):
                logger.warning(f"Ship {ship.symbol} missing frame or cargo attributes")
                continue

            # Log ship details for debugging
            frame_type = ship.frame.symbol if hasattr(ship.frame, 'symbol') else ''
            logger.info(
                f"Analyzing ship {ship.symbol}:"
                f"\n  Frame: {frame_type}"
                f"\n  Mounts: {[m.symbol for m in ship.mounts] if hasattr(ship, 'mounts') else 'None'}"
                f"\n  Cargo capacity: {ship.cargo.capacity if hasattr(ship, 'cargo') else 'Unknown'}"
            )

            # A ship is considered a mining ship if:
            # 1. It has a mining frame/type, or
            # 2. It has mining equipment installed
            has_mining_frame = (
                'MINING' in frame_type.upper()
                or 'DRONE' in frame_type.upper()
                or frame_type in ['FRAME_MINER']
            )

            has_mining_mount = False
            if hasattr(ship, 'mounts'):
                for mount in ship.mounts:
                    mount_symbol = mount.symbol if hasattr(mount, 'symbol') else ''
                    if 'MINING' in mount_symbol.upper() or 'DRILL' in mount_symbol.upper():
                        has_mining_mount = True
                        break

            if has_mining_frame or has_mining_mount:
                mining_ships.append(ship)
            # Larger ships with cargo capacity used for transport
            elif ship.cargo.capacity >= 50:
                command_ships.append(ship)
            # Small ships without mining equipment go to general pool
            else:
                command_ships.append(ship)

        logger.info(
            f"Ship categories:"
            f"\nMining ships: {[s.symbol for s in mining_ships]} "
            f"(frames: {[s.frame.symbol for s in mining_ships]})"
            f"\nCommand ships: {[s.symbol for s in command_ships]} "
            f"(frames: {[s.frame.symbol for s in command_ships]})"
        )
        return mining_ships, command_ships

    async def transfer_cargo(
        self,
        from_ship: Ship,
        to_ship: Ship,
        symbol: str,
        units: int
    ) -> bool:
        """Transfer cargo between ships

        Args:
            from_ship: Ship transferring cargo
            to_ship: Ship receiving cargo
            symbol: Trade symbol to transfer
            units: Number of units to transfer

        Returns:
            bool: True if transfer successful
        """
        if not hasattr(from_ship, 'symbol') or not hasattr(to_ship, 'symbol'):
            logger.error("Invalid ship objects for transfer")
            return False

        if not hasattr(from_ship, 'nav') or not hasattr(to_ship, 'nav'):
            logger.error("Ships missing navigation data")
            return False

        # Ensure ships are at same waypoint
        if from_ship.nav.waypoint_symbol != to_ship.nav.waypoint_symbol:
            logger.error(
                f"Ships must be at same waypoint for transfer. "
                f"From: {from_ship.nav.waypoint_symbol}, "
                f"To: {to_ship.nav.waypoint_symbol}"
            )
            return False

        # Ensure both ships are docked
        for ship in [from_ship, to_ship]:
            if ship.nav.status != ShipNavStatus.DOCKED:
                dock_response = await self.rate_limiter.execute_with_retry(
                    dock_ship.asyncio_detailed,
                    task_name=f"dock_ship_{ship.symbol}",
                    ship_symbol=ship.symbol,
                    client=self.client
                )
                if dock_response.status_code != 200:
                    logger.error(f"Failed to dock {ship.symbol}: {dock_response.status_code}")
                    return False

        # Execute transfer
        transfer_body = TransferCargoTransferCargoRequest(
            trade_symbol=symbol,
            units=units,
            ship_symbol=to_ship.symbol
        )

        response = await self.rate_limiter.execute_with_retry(
            transfer_cargo.asyncio_detailed,
            task_name="transfer_cargo",
            ship_symbol=from_ship.symbol,
            client=self.client,
            json_body=transfer_body
        )

        if response.status_code == 200:
            logger.info(
                f"Successfully transferred {units} units of {symbol} "
                f"from {from_ship.symbol} to {to_ship.symbol}"
            )
            return True
        else:
            logger.error(f"Failed to transfer cargo: {response.status_code}")
            if response.content:
                logger.error(f"Response: {response.content.decode()}")
            return False

    async def navigate_to_waypoint(
        self,
        ship_symbol: str,
        waypoint_symbol: str
    ) -> bool:
        """Navigate ship to a specific waypoint

        Args:
            ship_symbol: Symbol of the ship to navigate
            waypoint_symbol: Symbol of the destination waypoint

        Returns:
            bool: True if navigation was successful
        """
        # Get current ship status
        ship = self.ships.get(ship_symbol)
        if not ship:
            logger.error(f"Ship {ship_symbol} not found in fleet")
            return False

        # Check if already at destination
        if ship.nav.waypoint_symbol == waypoint_symbol:
            logger.info(f"Ship {ship_symbol} is already at {waypoint_symbol}")
            return True

        # Ensure ship is in orbit before navigation
        if ship.nav.status != ShipNavStatus.IN_ORBIT:
            orbit_success = await self.orbit_ship(ship_symbol)
            if not orbit_success:
                return False

        logger.info(f"Navigating {ship_symbol} to {waypoint_symbol}")
        nav_body = NavigateShipBody(waypoint_symbol=waypoint_symbol)
        response = await self.rate_limiter.execute_with_retry(
            navigate_ship.asyncio_detailed,
            task_name="navigate_ship",
            ship_symbol=ship_symbol,
            client=self.client,
            body=nav_body
        )

        if response.status_code == 200:
            logger.info(f"Successfully initiated navigation to {waypoint_symbol}")
            return True
        else:
            logger.error(f"Navigation failed: {response.status_code}")
            if response.content:
                logger.error(f"Response: {response.content.decode()}")
            return False

    async def dock_ship(self, ship_symbol: str) -> bool:
        """Dock the ship at current waypoint

        Args:
            ship_symbol: Symbol of the ship to dock

        Returns:
            bool: True if docking was successful
        """
        response = await self.rate_limiter.execute_with_retry(
            dock_ship.asyncio_detailed,
            task_name="dock_ship",
            ship_symbol=ship_symbol,
            client=self.client
        )

        if response.status_code == 200:
            logger.info(f"Successfully docked ship {ship_symbol}")
            return True
        else:
            logger.error(f"Failed to dock ship {ship_symbol}: {response.status_code}")
            if response.content:
                logger.error(f"Response: {response.content.decode()}")
            return False

    async def refuel_ship(self, ship_symbol: str) -> bool:
        """Refuel the ship at current waypoint

        Args:
            ship_symbol: Symbol of the ship to refuel

        Returns:
            bool: True if refueling was successful
        """
        response = await self.rate_limiter.execute_with_retry(
            refuel_ship.asyncio_detailed,
            task_name="refuel_ship",
            ship_symbol=ship_symbol,
            client=self.client,
            body=RefuelShipBody()
        )

        if response.status_code == 200:
            if response.parsed:
                cost = response.parsed.data.total_price
                logger.info(f"Successfully refueled ship {ship_symbol} (cost: {cost} credits)")
            else:
                logger.info(f"Successfully refueled ship {ship_symbol}")
            return True
        else:
            logger.error(f"Failed to refuel ship {ship_symbol}: {response.status_code}")
            if response.content:
                logger.error(f"Response: {response.content.decode()}")
            return False

    async def orbit_ship(self, ship_symbol: str) -> bool:
        """Put the ship in orbit at current waypoint

        Args:
            ship_symbol: Symbol of the ship to put in orbit

        Returns:
            bool: True if orbit maneuver was successful
        """
        response = await self.rate_limiter.execute_with_retry(
            orbit_ship.asyncio_detailed,
            task_name="orbit_ship",
            ship_symbol=ship_symbol,
            client=self.client
        )

        if response.status_code == 200:
            logger.info(f"Successfully moved ship {ship_symbol} to orbit")
            return True
        else:
            logger.error(f"Failed to move ship {ship_symbol} to orbit: {response.status_code}")
            if response.content:
                logger.error(f"Response: {response.content.decode()}")
            return False

    async def wait_for_arrival(self, ship_symbol: str) -> Optional[Ship]:
        """Wait for ship to arrive at destination

        Args:
            ship_symbol: Symbol of the ship to wait for

        Returns:
            Ship object if arrived successfully, None if error or timeout
        """
        max_attempts = 30  # 5 minutes with 10s sleep
        attempts = 0

        while attempts < max_attempts:
            try:
                # Update fleet status to get latest ship info
                response = await self.rate_limiter.execute_with_retry(
                    get_my_ships.asyncio_detailed,
                    task_name="check_ship_arrival",
                    client=self.client
                )

                if response.status_code != 200 or not response.parsed:
                    logger.error(f"Failed to get ship status: {response.status_code}")
                    await asyncio.sleep(1)
                    attempts += 1
                    continue

                ship = next(
                    (s for s in response.parsed.data
                     if s.symbol == ship_symbol),
                    None
                )

                if not ship:
                    logger.error(f"Ship {ship_symbol} not found")
                    return None

                if ship.nav.status != ShipNavStatus.IN_TRANSIT:
                    logger.info(f"Ship {ship_symbol} has arrived at {ship.nav.waypoint_symbol}")
                    return ship

                logger.info(
                    f'Ship {ship_symbol} in transit to {ship.nav.waypoint_symbol}... '
                    f'({attempts + 1}/{max_attempts})'
                )
                await asyncio.sleep(10)
                attempts += 1

            except Exception as e:
                logger.error(f"Error checking ship arrival: {e}", exc_info=True)
                await asyncio.sleep(1)
                attempts += 1

        logger.error(f'Timeout waiting for ship {ship_symbol} to arrive')
        return None
