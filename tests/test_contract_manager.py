"""Tests for contract manager"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone

from space_traders_api_client.models.ship_nav_status import ShipNavStatus
from space_traders_api_client.models.ship_nav_flight_mode import ShipNavFlightMode
from space_traders_api_client.models.waypoint_trait_symbol import WaypointTraitSymbol
from space_traders_api_client.models.waypoint_type import WaypointType
from .factories import (
    ContractFactory,
    ShipFactory,
    ContractDeliverGood,
    MetaFactory,
    ShipMountFactory,
    WaypointFactory,
    WaypointTraitFactory,
    SystemFactory,
    ShipNavFactory
)
from space_traders_api_client.models.meta import Meta
from game.contract_manager import ContractManager


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
async def contract_manager(mock_client):
    manager = ContractManager(mock_client)
    try:
        yield manager
    finally:
        if hasattr(manager, 'rate_limiter'):
            await manager.rate_limiter.cleanup()


@pytest.fixture
def mock_contract():
    """Create a mock contract with delivery requirements"""
    return ContractFactory.build(
        terms__deliver=[
            ContractDeliverGood(
                trade_symbol="TEST_GOOD",
                destination_symbol="TEST-SYSTEM-DEST",
                units_required=10,
                units_fulfilled=0
            )
        ]
    )


@pytest.fixture
def mock_mining_ship():
    """Create a mock ship with mining capabilities"""
    ship = ShipFactory.build(
        nav__status=ShipNavStatus.DOCKED,
        nav__waypoint_symbol="TEST-WAYPOINT",
        nav__system_symbol="TEST-SYSTEM",
        cargo__capacity=100,
        cargo__units=0,
        mounts=[ShipMountFactory.build(symbol="MOUNT_MINING_LASER")]
    )
    return ship


@pytest.fixture
def mock_ships(mock_mining_ship):
    """Create a dictionary of mock ships"""
    return {mock_mining_ship.symbol: mock_mining_ship}


@pytest.fixture
def mock_survey_manager():
    return MagicMock()


# New test fixtures for navigation features
@pytest.fixture
def mock_waypoint():
    return WaypointFactory.build(
        symbol="TEST-SYSTEM-DEST",
        type_=WaypointType.ORBITAL_STATION,
        traits=[
            WaypointTraitFactory.build(
                symbol=WaypointTraitSymbol.MARKETPLACE
            )
        ]
    )


@pytest.fixture
def mock_system():
    return SystemFactory.build(
        symbol="TEST-SYSTEM",
        waypoints=[mock_waypoint]
    )


# New tests for navigation features
@pytest.mark.asyncio
async def test_navigate_to_waypoint_success(
    contract_manager,
    mock_client,
    mock_mining_ship
):
    """Test successful navigation to waypoint"""
    target_waypoint = "TEST-SYSTEM-DEST"
    
    # Mock orbit_ship response
    with patch('game.contract_manager.orbit_ship.asyncio_detailed', new_callable=AsyncMock) as mock_orbit:
        orbit_response = MagicMock()
        orbit_response.status_code = 200
        mock_orbit.return_value = orbit_response

        # Mock navigate_ship response
        with patch('game.contract_manager.navigate_ship.asyncio_detailed', new_callable=AsyncMock) as mock_navigate:
            nav_response = MagicMock()
            nav_response.status_code = 200
            nav_response.parsed.data = ShipNavFactory.build(
                status=ShipNavStatus.IN_TRANSIT,
                flight_mode=ShipNavFlightMode.CRUISE
            )
            mock_navigate.return_value = nav_response

            # Call the navigation method
            result = await contract_manager.navigate_to_waypoint(
                mock_mining_ship,
                target_waypoint
            )

            assert result is True
            mock_orbit.assert_called_once()
            mock_navigate.assert_called_once()


@pytest.mark.asyncio
async def test_navigate_to_waypoint_already_at_destination(
    contract_manager,
    mock_client,
    mock_mining_ship
):
    """Test navigation when ship is already at destination"""
    target_waypoint = mock_mining_ship.nav.waypoint_symbol
    
    result = await contract_manager.navigate_to_waypoint(
        mock_mining_ship,
        target_waypoint
    )
    
    assert result is True


@pytest.mark.asyncio
async def test_navigate_to_waypoint_failure(
    contract_manager,
    mock_client,
    mock_mining_ship
):
    """Test navigation failure handling"""
    target_waypoint = "TEST-SYSTEM-DEST"
    
    with patch('game.contract_manager.orbit_ship.asyncio_detailed', new_callable=AsyncMock) as mock_orbit:
        orbit_response = MagicMock()
        orbit_response.status_code = 200
        mock_orbit.return_value = orbit_response

        with patch('game.contract_manager.navigate_ship.asyncio_detailed', new_callable=AsyncMock) as mock_navigate:
            nav_response = MagicMock()
            nav_response.status_code = 400
            mock_navigate.return_value = nav_response

            result = await contract_manager.navigate_to_waypoint(
                mock_mining_ship,
                target_waypoint
            )

            assert result is False
            mock_orbit.assert_called_once()
            mock_navigate.assert_called_once()


@pytest.mark.asyncio
async def test_ensure_ship_docked_success(
    contract_manager,
    mock_client,
    mock_mining_ship
):
    """Test successful docking operation"""
    # Set ship to in orbit
    mock_mining_ship.nav.status = ShipNavStatus.IN_ORBIT
    
    with patch('game.contract_manager.dock_ship.asyncio_detailed', new_callable=AsyncMock) as mock_dock:
        dock_response = MagicMock()
        dock_response.status_code = 200
        mock_dock.return_value = dock_response

        result = await contract_manager.ensure_ship_docked(mock_mining_ship)

        assert result is True
        mock_dock.assert_called_once()


@pytest.mark.asyncio
async def test_ensure_ship_docked_already_docked(
    contract_manager,
    mock_client,
    mock_mining_ship
):
    """Test when ship is already docked"""
    # Ship is already docked in fixture
    result = await contract_manager.ensure_ship_docked(mock_mining_ship)
    
    assert result is True


@pytest.mark.asyncio
async def test_refuel_ship_success(
    contract_manager,
    mock_client,
    mock_mining_ship
):
    """Test successful ship refueling"""
    with patch('game.contract_manager.refuel_ship.asyncio_detailed', new_callable=AsyncMock) as mock_refuel:
        refuel_response = MagicMock()
        refuel_response.status_code = 200
        mock_refuel.return_value = refuel_response

        result = await contract_manager.refuel_ship(mock_mining_ship)

        assert result is True
        mock_refuel.assert_called_once()


@pytest.mark.asyncio
async def test_refuel_ship_failure(
    contract_manager,
    mock_client,
    mock_mining_ship
):
    """Test ship refueling failure"""
    with patch('game.contract_manager.refuel_ship.asyncio_detailed', new_callable=AsyncMock) as mock_refuel:
        refuel_response = MagicMock()
        refuel_response.status_code = 400
        mock_refuel.return_value = refuel_response

        result = await contract_manager.refuel_ship(mock_mining_ship)

        assert result is False
        mock_refuel.assert_called_once()


@pytest.mark.asyncio
async def test_get_route_to_waypoint_success(
    contract_manager,
    mock_client,
    mock_mining_ship,
    mock_waypoint
):
    """Test successful route planning"""
    with patch('game.contract_manager.get_system_waypoints.asyncio_detailed', new_callable=AsyncMock) as mock_waypoints:
        waypoints_response = MagicMock()
        waypoints_response.status_code = 200
        waypoints_response.parsed.data = [mock_waypoint]
        mock_waypoints.return_value = waypoints_response

        route = await contract_manager.get_route_to_waypoint(
            mock_mining_ship.nav.system_symbol,
            "TEST-SYSTEM-DEST"
        )

        assert route is not None
        assert route.symbol == "TEST-SYSTEM-DEST"
        mock_waypoints.assert_called_once()


@pytest.mark.asyncio
async def test_get_route_to_waypoint_not_found(
    contract_manager,
    mock_client,
    mock_mining_ship
):
    """Test route planning when waypoint not found"""
    with patch('game.contract_manager.get_system_waypoints.asyncio_detailed', new_callable=AsyncMock) as mock_waypoints:
        waypoints_response = MagicMock()
        waypoints_response.status_code = 200
        waypoints_response.parsed.data = []  # No waypoints found
        mock_waypoints.return_value = waypoints_response

        route = await contract_manager.get_route_to_waypoint(
            mock_mining_ship.nav.system_symbol,
            "NONEXISTENT-WAYPOINT"
        )

        assert route is None
        mock_waypoints.assert_called_once()


@pytest.mark.asyncio
async def test_complete_delivery_success(
    contract_manager,
    mock_client,
    mock_contract,
    mock_mining_ship
):
    """Test successful contract delivery completion"""
    # Setup mocks for the entire delivery process
    with patch.object(contract_manager, 'navigate_to_waypoint', new_callable=AsyncMock) as mock_navigate:
        mock_navigate.return_value = True
        
        with patch.object(contract_manager, 'ensure_ship_docked', new_callable=AsyncMock) as mock_dock:
            mock_dock.return_value = True
            
            with patch.object(contract_manager, 'deliver_contract_cargo', new_callable=AsyncMock) as mock_deliver:
                mock_deliver.return_value = True

                result = await contract_manager.complete_delivery(
                    contract=mock_contract,
                    ship=mock_mining_ship,
                    delivery=mock_contract.terms.deliver[0]
                )

                assert result is True
                mock_navigate.assert_called_once()
                mock_dock.assert_called_once()
                mock_deliver.assert_called_once()


@pytest.mark.asyncio
async def test_complete_delivery_navigation_failure(
    contract_manager,
    mock_client,
    mock_contract,
    mock_mining_ship
):
    """Test delivery completion with navigation failure"""
    with patch.object(contract_manager, 'navigate_to_waypoint', new_callable=AsyncMock) as mock_navigate:
        mock_navigate.return_value = False

        result = await contract_manager.complete_delivery(
            contract=mock_contract,
            ship=mock_mining_ship,
            delivery=mock_contract.terms.deliver[0]
        )

        assert result is False
        mock_navigate.assert_called_once()