import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from space_traders_api_client.models.system import System
from space_traders_api_client.models.waypoint import Waypoint
from space_traders_api_client.models.waypoint_type import WaypointType
from space_traders_api_client.models.meta import Meta
from space_traders_api_client.api.systems import get_systems, get_system_waypoints
from space_traders_api_client.models.get_systems_response_200 import GetSystemsResponse200
from space_traders_api_client.models.get_system_waypoints_response_200 import GetSystemWaypointsResponse200


# Make sure the game module can be imported
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.system_manager import SystemManager
from game.rate_limiter import RateLimiter # Assuming this path is correct

@pytest.fixture
def mock_client():
    return AsyncMock()

@pytest.fixture
def mock_rate_limiter():
    limiter = MagicMock(spec=RateLimiter)
    # Mock execute_with_retry to directly return the result of the api_call
    async def mock_execute(*args, **kwargs):
        api_call = args[0] # The first arg to execute_with_retry is the api_call
        # Remaining args are for the api_call itself, extract them carefully
        # Example: api_call_args = args[1:] won't work because task_name etc are also there.
        # We need to pass the keyword arguments intended for the actual API function.

        # A simplified approach for mock: assume kwargs contains what the api_call needs
        # This might need adjustment based on actual RateLimiter.execute_with_retry signature
        # and how api_call is wrapped.

        # Let's assume api_call is called with its specific arguments from kwargs within execute_with_retry
        # For this mock, we'll simulate that by calling api_call with relevant parts of kwargs.
        # This is tricky because execute_with_retry takes its own params (task_name, client)
        # and then passes others to api_call.

        # Simplification: The mocked API calls (like get_systems.asyncio_detailed)
        # will be patched directly in tests, so execute_with_retry just needs to return their awaited result.

        # The actual api_call (e.g., get_systems.ayncio_detailed) is passed as the first argument
        # The actual arguments for that call are passed as kwargs to execute_with_retry

        # Simulate the api_call being awaited
        # The patched version of `get_systems.asyncio_detailed` will be an AsyncMock
        # so when we call it, it returns another awaitable (an AsyncMock).
        # We need to await this.
        mock_api_response = await api_call(**kwargs) # This calls the *patched* API function
        return mock_api_response

    limiter.execute_with_retry = AsyncMock(side_effect=mock_execute)
    return limiter


@pytest.fixture
def system_manager(mock_client, mock_rate_limiter):
    sm = SystemManager(client=mock_client)
    sm.rate_limiter = mock_rate_limiter # Replace with mock
    return sm

def test_add_and_get_system(system_manager):
    system = System(symbol="SYS1", sector_symbol="SEC1", type_="BLUE_STAR", x=0, y=0, waypoints=[])
    system_manager.add_system(system)
    assert system_manager.get_system("SYS1") == system
    assert system_manager.get_system("UNKNOWN") is None

def test_add_waypoints(system_manager):
    waypoint1 = Waypoint(symbol="WP1", system_symbol="SYS1", type_=WaypointType.PLANET, x=10, y=20)
    waypoint2 = Waypoint(symbol="WP2", system_symbol="SYS1", type_=WaypointType.ASTEROID_FIELD, x=30, y=40)
    system_manager.add_waypoints("SYS1", [waypoint1, waypoint2])

    waypoints_in_sys = system_manager.get_waypoints_in_system("SYS1")
    assert len(waypoints_in_sys) == 2
    assert waypoint1 in waypoints_in_sys
    assert waypoint2 in waypoints_in_sys

    # Test adding same waypoint again (should not duplicate)
    system_manager.add_waypoints("SYS1", [waypoint1])
    assert len(system_manager.get_waypoints_in_system("SYS1")) == 2


def test_find_waypoints_by_type(system_manager):
    wp_planet = Waypoint(symbol="PLANET1", system_symbol="SYS1", type_=WaypointType.PLANET, x=0,y=0)
    wp_asteroid = Waypoint(symbol="AST1", system_symbol="SYS1", type_=WaypointType.ASTEROID_FIELD, x=0,y=0)
    wp_moon = Waypoint(symbol="MOON1", system_symbol="SYS2", type_=WaypointType.MOON, x=0,y=0)
    system_manager.add_waypoints("SYS1", [wp_planet, wp_asteroid])
    system_manager.add_waypoints("SYS2", [wp_moon])

    asteroid_fields = system_manager.find_waypoints_by_type(WaypointType.ASTEROID_FIELD)
    assert len(asteroid_fields) == 1
    assert asteroid_fields[0] == wp_asteroid

    planets = system_manager.find_waypoints_by_type(WaypointType.PLANET)
    assert len(planets) == 1
    assert planets[0] == wp_planet

    gas_giants = system_manager.find_waypoints_by_type(WaypointType.GAS_GIANT)
    assert len(gas_giants) == 0


@pytest.mark.asyncio
@patch('space_traders_api_client.api.systems.get_systems.asyncio_detailed', new_callable=AsyncMock)
async def test_discover_systems(mock_get_systems, system_manager, mock_client):
    sys_data1 = System(symbol="SYS1", sector_symbol="S1", type_="RED_STAR", x=0,y=0, waypoints=[])
    sys_data2 = System(symbol="SYS2", sector_symbol="S1", type_="BLUE_STAR", x=0,y=0, waypoints=[])

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.parsed = GetSystemsResponse200(data=[sys_data1, sys_data2], meta=Meta(total=2, page=1, limit=10))
    mock_get_systems.return_value = mock_response

    await system_manager.discover_systems(limit=2)

    # Check that rate_limiter.execute_with_retry was called with get_systems.asyncio_detailed
    system_manager.rate_limiter.execute_with_retry.assert_called_once_with(
        get_systems.asyncio_detailed, # The actual API function
        task_name="discover_systems",
        client=mock_client,
        limit=2
    )

    assert system_manager.get_system("SYS1") is not None
    assert system_manager.get_system("SYS2") is not None
    assert system_manager.get_system("SYS1").type == "RED_STAR"

@pytest.mark.asyncio
@patch('space_traders_api_client.api.systems.get_system_waypoints.asyncio_detailed', new_callable=AsyncMock)
async def test_discover_waypoints_in_system(mock_get_waypoints, system_manager, mock_client):
    # System must exist first
    test_system = System(symbol="SYS-TEST", sector_symbol="S",type_="STAR", x=0,y=0,waypoints=[])
    system_manager.add_system(test_system)

    wp_data1 = Waypoint(symbol="WP1", system_symbol="SYS-TEST", type_=WaypointType.PLANET, x=0,y=0)
    wp_data2 = Waypoint(symbol="WP2", system_symbol="SYS-TEST", type_=WaypointType.ASTEROID_FIELD, x=0,y=0)

    mock_response_page1 = MagicMock()
    mock_response_page1.status_code = 200
    mock_response_page1.parsed = GetSystemWaypointsResponse200(
        data=[wp_data1],
        meta=Meta(total=2, page=1, limit=1) # Total 2, 1 per page
    )

    mock_response_page2 = MagicMock()
    mock_response_page2.status_code = 200
    mock_response_page2.parsed = GetSystemWaypointsResponse200(
        data=[wp_data2],
        meta=Meta(total=2, page=2, limit=1)
    )

    # Configure the mock to return page1 then page2
    mock_get_waypoints.side_effect = [mock_response_page1, mock_response_page2]

    await system_manager.discover_waypoints_in_system("SYS-TEST")

    # Check calls to rate_limiter
    assert system_manager.rate_limiter.execute_with_retry.call_count == 2
    system_manager.rate_limiter.execute_with_retry.assert_any_call(
        get_system_waypoints.asyncio_detailed,
        task_name="discover_waypoints_SYS-TEST",
        client=mock_client,
        system_symbol="SYS-TEST",
        limit=20 # Default limit in implementation
    )
    system_manager.rate_limiter.execute_with_retry.assert_any_call(
        get_system_waypoints.asyncio_detailed,
        task_name="discover_waypoints_SYS-TEST_page_2",
        client=mock_client,
        system_symbol="SYS-TEST",
        limit=20,
        page=2
    )

    waypoints = system_manager.get_waypoints_in_system("SYS-TEST")
    assert len(waypoints) == 2
    assert wp_data1 in waypoints
    assert wp_data2 in waypoints
