import logging
from typing import Dict, List, Optional

from space_traders_api_client import AuthenticatedClient
from space_traders_api_client.api.systems import get_systems, get_system_waypoints
from space_traders_api_client.models.system import System
from space_traders_api_client.models.waypoint import Waypoint
from space_traders_api_client.models.waypoint_type import WaypointType

from .rate_limiter import RateLimiter # Assuming RateLimiter is in the same directory

logger = logging.getLogger(__name__)

class SystemManager:
    """Manages information about systems and their waypoints."""

    def __init__(self, client: AuthenticatedClient):
        self.client = client
        self.systems: Dict[str, System] = {}
        self.waypoints: Dict[str, List[Waypoint]] = {}  # System symbol -> List of Waypoints
        self.rate_limiter = RateLimiter()

    def add_system(self, system: System):
        """Adds a system to the manager."""
        if system.symbol not in self.systems:
            self.systems[system.symbol] = system
            logger.info(f"Added system: {system.symbol}")
        else:
            logger.debug(f"System {system.symbol} already exists.")

    def get_system(self, system_symbol: str) -> Optional[System]:
        """Retrieves a system by its symbol."""
        return self.systems.get(system_symbol)

    def add_waypoints(self, system_symbol: str, waypoints: List[Waypoint]):
        """Adds a list of waypoints for a given system."""
        if system_symbol not in self.waypoints:
            self.waypoints[system_symbol] = []

        current_waypoints_in_system = {wp.symbol: wp for wp in self.waypoints[system_symbol]}
        new_waypoints_added = 0
        for waypoint in waypoints:
            if waypoint.symbol not in current_waypoints_in_system:
                self.waypoints[system_symbol].append(waypoint)
                current_waypoints_in_system[waypoint.symbol] = waypoint
                new_waypoints_added +=1
            else:
                logger.debug(f"Waypoint {waypoint.symbol} in system {system_symbol} already exists.")
        if new_waypoints_added > 0:
            logger.info(f"Added {new_waypoints_added} new waypoints to system {system_symbol}. Total waypoints for system: {len(self.waypoints[system_symbol])}")
        else:
            logger.info(f"No new waypoints added to system {system_symbol}. All provided waypoints already exist.")

    def get_waypoints_in_system(self, system_symbol: str) -> List[Waypoint]:
        """Retrieves all waypoints in a given system."""
        return self.waypoints.get(system_symbol, [])

    def find_waypoints_by_type(self, waypoint_type: WaypointType) -> List[Waypoint]:
        """Finds all waypoints of a specific type across all known systems."""
        found_waypoints: List[Waypoint] = []
        for system_waypoints in self.waypoints.values():
            for waypoint in system_waypoints:
                if waypoint.type == waypoint_type:
                    found_waypoints.append(waypoint)
        logger.info(f"Found {len(found_waypoints)} waypoints of type {waypoint_type}")
        return found_waypoints

    def get_all_systems(self) -> List[System]:
        """Retrieves all known systems."""
        return list(self.systems.values())

    def get_total_waypoints_count(self) -> int:
        """Returns the total number of waypoints stored."""
        return sum(len(wps) for wps in self.waypoints.values())

    async def discover_systems(self, limit: int = 20):
        """Scans for systems and adds them to the manager."""
        try:
            response = await self.rate_limiter.execute_with_retry(
                get_systems.asyncio_detailed,
                task_name="discover_systems",
                client=self.client,
                limit=limit
            )

            if response.status_code == 200 and response.parsed:
                for system_data in response.parsed.data:
                    self.add_system(system_data)
                logger.info(f"Successfully discovered and added {len(response.parsed.data)} systems.")
            else:
                logger.error(f"Failed to discover systems: {response.status_code}")
        except Exception as e:
            logger.error(f"Error during system discovery: {e}", exc_info=True)

    async def discover_waypoints_in_system(self, system_symbol: str):
        """Scans for waypoints in a given system and adds them to the manager."""
        if not self.get_system(system_symbol):
            logger.warning(f"System {system_symbol} not known. Cannot discover waypoints.")
            # Optionally, try to discover the system first
            # await self.discover_systems()
            # if not self.get_system(system_symbol):
            #     logger.error(f"Failed to discover system {system_symbol} before waypoint scan.")
            #     return
            return

        try:
            response = await self.rate_limiter.execute_with_retry(
                get_system_waypoints.asyncio_detailed,
                task_name=f"discover_waypoints_{system_symbol}",
                client=self.client,
                system_symbol=system_symbol,
                limit=20 # Max waypoints per page
            )

            if response.status_code == 200 and response.parsed:
                waypoints_data = response.parsed.data
                self.add_waypoints(system_symbol, waypoints_data)
                logger.info(f"Successfully discovered and added {len(waypoints_data)} waypoints for system {system_symbol}.")

                # Handle pagination if meta is present and indicates more pages
                if hasattr(response.parsed, 'meta') and response.parsed.meta.total > len(waypoints_data):
                    total_pages = (response.parsed.meta.total + 19) // 20 # Calculate total pages
                    for page in range(2, total_pages + 1):
                        logger.info(f"Fetching page {page}/{total_pages} for system {system_symbol} waypoints...")
                        paginated_response = await self.rate_limiter.execute_with_retry(
                            get_system_waypoints.asyncio_detailed,
                            task_name=f"discover_waypoints_{system_symbol}_page_{page}",
                            client=self.client,
                            system_symbol=system_symbol,
                            limit=20,
                            page=page
                        )
                        if paginated_response.status_code == 200 and paginated_response.parsed:
                            self.add_waypoints(system_symbol, paginated_response.parsed.data)
                            logger.info(f"Added {len(paginated_response.parsed.data)} waypoints from page {page} for system {system_symbol}.")
                        else:
                            logger.error(f"Failed to fetch page {page} for system {system_symbol} waypoints: {paginated_response.status_code}")
            else:
                logger.error(f"Failed to discover waypoints for system {system_symbol}: {response.status_code}")
        except Exception as e:
            logger.error(f"Error during waypoint discovery for system {system_symbol}: {e}", exc_info=True)
