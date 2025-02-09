"""
Tests for the SpaceTrader game automation
"""
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from space_traders_api_client.models.agent import Agent
from space_traders_api_client.models.ship import Ship
from space_traders_api_client.models.ship_nav import ShipNav
from space_traders_api_client.models.ship_nav_flight_mode import (
    ShipNavFlightMode
)
from space_traders_api_client.models.ship_nav_route import ShipNavRoute
from space_traders_api_client.models.ship_nav_route_waypoint import (
    ShipNavRouteWaypoint
)
from space_traders_api_client.models.ship_fuel import ShipFuel
from space_traders_api_client.models.ship_cargo import ShipCargo
from space_traders_api_client.models.system import System
from space_traders_api_client.models.system_type import SystemType
from space_traders_api_client.models.waypoint_type import WaypointType
from space_traders_api_client.models.ship_nav_status import ShipNavStatus

from game.trader import SpaceTrader
from tests.factories import (
    AgentFactory,
    ShipFactory,
    SystemFactory,
)


@pytest.fixture
def mock_agent() -> Agent:
    """Create a mock agent for testing"""
    return AgentFactory(symbol="TEST_AGENT")


@pytest.fixture
def mock_ship() -> Ship:
    """Create a mock ship for testing"""
    now = datetime.now(timezone.utc)
    waypoint = ShipNavRouteWaypoint(
        symbol="TEST-WAYPOINT",
        type_=WaypointType.PLANET,
        system_symbol="TEST-SYSTEM",
        x=1,
        y=1
    )

    origin_waypoint = ShipNavRouteWaypoint(
        symbol="TEST-ORIGIN",
        type_=WaypointType.PLANET,
        system_symbol="TEST-SYSTEM",
        x=0,
        y=0
    )

    nav_route = ShipNavRoute(
        destination=waypoint,
        origin=origin_waypoint,
        departure_time=now,
        arrival=now
    )

    return ShipFactory(
        symbol="TEST_SHIP_1",
        registration={
            "name": "Test Ship",
            "role": "EXPLORER",
            "factionSymbol": "TEST_FACTION"
        },
        frame={"symbol": "FRAME_EXPLORER", "name": "Explorer Frame"},
        mounts=[{
            "symbol": "MOUNT_LASER_I",
            "name": "Laser I",
            "description": "A basic laser for defense",
            "strength": 10
        }],
        nav=ShipNav(
            system_symbol="test-system-XXX",
            waypoint_symbol="test-system-XXX",
            route=nav_route,
            status=ShipNavStatus.DOCKED,
            flight_mode=ShipNavFlightMode.CRUISE
        ),
        fuel=ShipFuel(
            current=100,
            capacity=100
        ),
        cargo=ShipCargo(
            capacity=100,
            units=0,
            inventory=[]
        )
    )


@pytest.fixture
def mock_system() -> System:
    """Create a mock system for testing"""
    return SystemFactory(
        symbol="test-system-XXX",
        type_=SystemType.NEUTRON_STAR
    )


@pytest.fixture
def trader():
    """Create a SpaceTrader instance for testing"""
    return SpaceTrader("test_token")


@pytest.mark.asyncio
async def test_initialization(trader, mock_agent, mock_ship, mock_system):
    """Test trader initialization process"""
    with patch.object(
        trader.agent_manager,
        'initialize',
        AsyncMock()
    ) as mock_init, patch.object(
        trader.fleet_manager,
        'update_fleet',
        AsyncMock()
    ) as mock_fleet, patch.object(
        trader.contract_manager,
        'update_contracts',
        AsyncMock()
    ) as mock_contracts:
        await trader.initialize()

        # Verify all initialization methods were called
        mock_init.assert_called_once()
        mock_fleet.assert_called_once()
        mock_contracts.assert_called_once()


@pytest.mark.asyncio
async def test_manage_fleet_error_handling(trader):
    """Test fleet management error handling"""
    with patch.object(
        trader.fleet_manager,
        'update_fleet',
        side_effect=Exception("API Error")
    ):
        await trader.manage_fleet()
        # Should handle error gracefully without raising


@pytest.mark.asyncio
async def test_process_ship_missing_nav(trader):
    """Test processing ship with missing nav data"""
    ship = ShipFactory(symbol="TEST_SHIP_1")
    # Remove nav attribute
    delattr(ship, 'nav')
    await trader._process_ship(ship)
    # Should handle missing nav gracefully


@pytest.mark.asyncio
async def test_process_ship_in_transit(trader, mock_ship):
    """Test processing ship in transit"""
    mock_ship.nav.status = ShipNavStatus.IN_TRANSIT
    await trader._process_ship(mock_ship)
    # Should skip processing for in-transit ship


@pytest.mark.asyncio
async def test_handle_market_actions_missing_cargo(trader, mock_ship):
    """Test handling market actions with missing cargo data"""
    delattr(mock_ship, 'cargo')
    await trader._handle_market_actions(mock_ship)
    # Should handle missing cargo gracefully


@pytest.mark.asyncio
async def test_handle_market_actions_update_failure(trader, mock_ship):
    """Test market actions with failed market update"""
    with patch.object(
        trader.trade_manager,
        'update_market_data',
        side_effect=Exception("Market update failed")
    ):
        await trader._handle_market_actions(mock_ship)
        # Should handle market update failure gracefully


@pytest.mark.asyncio
async def test_execute_trade_route_navigation_failure(
    trader,
    mock_ship,
    mock_system
):
    """Test trade route execution with navigation failure"""
    from game.market_analyzer import TradeOpportunity

    route = TradeOpportunity(
        trade_symbol="IRON_ORE",
        source_market="SOURCE",
        target_market="TARGET",
        purchase_price=50,
        sell_price=100,
        trade_volume=10,
        source_supply="HIGH",
        target_demand="HIGH",
        distance=5
    )

    with patch.object(
        trader.fleet_manager,
        'navigate_to_waypoint',
        return_value=False  # noqa: B001
    ):
        result = await trader._execute_trade_route(mock_ship, route)
        assert result is False  # noqa: B001


@pytest.mark.asyncio
async def test_trade_loop_termination(trader):
    """Test trade loop termination on error"""
    loop_task = None
    try:
        with patch.object(
            trader.agent_manager,
            'get_agent_status',
            side_effect=Exception("API Error")
        ), patch('asyncio.sleep', AsyncMock()):
            # Create task for the trade loop
            loop_task = asyncio.create_task(trader.trade_loop())
            # Wait briefly to let the loop run
            await asyncio.sleep(0.1)
            # Verify the loop is still running
            assert not loop_task.done()
    finally:
        # Ensure we clean up the task
        if loop_task and not loop_task.done():
            loop_task.cancel()
            try:
                await loop_task
            except asyncio.CancelledError:
                pass  # Expected when we cancel the task


@pytest.mark.asyncio
async def test_market_insights_empty(trader, mock_ship):
    """Test handling empty market insights"""
    with patch.object(
        trader.market_analyzer,
        'get_market_insights',
        return_value={"recommendations": []}
    ), patch.object(
        trader.trade_manager,
        'update_market_data',
        AsyncMock()
    ):
        await trader._handle_market_actions(mock_ship)
        # Should handle empty insights gracefully


@pytest.mark.asyncio
async def test_trade_route_full_cargo(trader, mock_ship):
    """Test trade route finding with full cargo"""
    mock_ship.cargo.units = mock_ship.cargo.capacity
    with patch.object(
        trader.trade_manager,
        'update_market_data',
        AsyncMock()
    ), patch.object(
        trader.market_analyzer,
        'get_market_insights',
        return_value={"recommendations": []}
    ):
        await trader._handle_market_actions(mock_ship)
        # Should skip trade route finding for full cargo
