"""Tests for shipyard manager"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock, ANY
from datetime import datetime, timezone

from space_traders_api_client.models.ship_mount import ShipMount
from space_traders_api_client.models.ship_mount_symbol import ShipMountSymbol
from space_traders_api_client.models.purchase_ship_body import PurchaseShipBody
from space_traders_api_client.models.ship_type import ShipType

from .factories import (
    WaypointFactory,
    WaypointTraitFactory,
    MetaFactory,
)
from game.shipyard import ShipyardManager


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def shipyard_manager(mock_client):
    return ShipyardManager(mock_client)


@pytest.fixture
def mock_waypoint():
    """Create a waypoint with a shipyard"""
    return WaypointFactory.build(
        traits=[WaypointTraitFactory.build(symbol="SHIPYARD")]
    )


def test_has_mining_mount(shipyard_manager):
    """Test detection of mining mounts"""
    # Test with mining laser
    mounts = [
        ShipMount(
            symbol=ShipMountSymbol.MOUNT_MINING_LASER_I,
            name="Mining Laser I",
            description="A basic mining laser",
            requirements=MagicMock(power=1, crew=0),
            strength=None,
            deposits=None
        )
    ]
    assert shipyard_manager.has_mining_mount(mounts) is True

    # Test with non-mining mount
    mounts = [
        ShipMount(
            symbol="MOUNT_TURRET",
            name="Turret",
            description="A basic turret",
            requirements=MagicMock(power=1, crew=0),
            strength=None,
            deposits=None
        )
    ]
    assert shipyard_manager.has_mining_mount(mounts) is False

    # Test with empty list
    assert shipyard_manager.has_mining_mount([]) is False


@pytest.mark.asyncio
async def test_find_shipyards_in_system(shipyard_manager, mock_waypoint):
    """Test finding shipyards in a system"""
    with patch(
        'game.shipyard.get_system_waypoints.asyncio_detailed',
        new_callable=AsyncMock
    ) as mock_get:
        # Setup mock response for first page
        response = MagicMock()
        response.status_code = 200
        response.parsed.data = [mock_waypoint]
        response.parsed.meta = MetaFactory.build(total=1)
        mock_get.return_value = response

        shipyards = await shipyard_manager.find_shipyards_in_system("TEST-SYSTEM")
        assert len(shipyards) == 1
        assert shipyards[0] == mock_waypoint.symbol

        mock_get.assert_called_once_with(
            system_symbol="TEST-SYSTEM",
            client=shipyard_manager.client,
            page=1,
            limit=20
        )


@pytest.mark.asyncio
async def test_find_shipyards_multiple_pages(shipyard_manager, mock_waypoint):
    """Test finding shipyards across multiple pages"""
    with patch(
        'game.shipyard.get_system_waypoints.asyncio_detailed',
        new_callable=AsyncMock
    ) as mock_get:
        # Setup mock responses for two pages
        response1 = MagicMock()
        response1.status_code = 200
        response1.parsed.data = [mock_waypoint]
        response1.parsed.meta = MetaFactory.build(total=40)  # 2 pages (20 per page)

        # Create a second waypoint for page 2
        mock_waypoint2 = WaypointFactory.build(
            symbol="TEST-WAYPOINT-2",
            traits=[WaypointTraitFactory.build(symbol="SHIPYARD")]
        )
        response2 = MagicMock()
        response2.status_code = 200
        response2.parsed.data = [mock_waypoint2]
        response2.parsed.meta = MetaFactory.build(total=40)

        mock_get.side_effect = [response1, response2]

        shipyards = await shipyard_manager.find_shipyards_in_system("TEST-SYSTEM")
        assert len(shipyards) == 2  # Should find both shipyards
        assert mock_waypoint.symbol in shipyards
        assert mock_waypoint2.symbol in shipyards


@pytest.mark.asyncio
async def test_find_available_mining_ship(shipyard_manager, mock_waypoint):
    """Test finding an available mining ship"""
    with patch.object(
        shipyard_manager,
        'find_shipyards_in_system',
        new_callable=AsyncMock
    ) as mock_find:
        mock_find.return_value = [mock_waypoint.symbol]

        with patch.object(
            shipyard_manager,
            'get_shipyard_info',
            new_callable=AsyncMock
        ) as mock_info:
            mock_info.return_value = {
                'ships': [
                    {
                        'type': 'SHIP_MINING_DRONE',
                        'purchasePrice': 90000
                    }
                ]
            }

            result = await shipyard_manager.find_available_mining_ship("TEST-SYSTEM")

            assert result is not None
            waypoint, ship = result
            assert waypoint == mock_waypoint.symbol
            assert ship['type'] == 'SHIP_MINING_DRONE'
            assert ship['purchasePrice'] == 90000


@pytest.mark.asyncio
async def test_purchase_mining_ship(shipyard_manager):
    """Test purchasing a mining ship"""
    # Mock finding available ship
    with patch.object(
        shipyard_manager,
        'find_available_mining_ship',
        new_callable=AsyncMock
    ) as mock_find:
        mock_find.return_value = (
            "SHIPYARD-1",
            {
                'type': 'SHIP_MINING_DRONE',
                'purchasePrice': 90000
            }
        )

        # Mock purchase API call
        with patch(
            'game.shipyard.purchase_ship.asyncio_detailed',
            new_callable=AsyncMock
        ) as mock_purchase:
            # Create mock response
            mock_ship = MagicMock()
            mock_ship.symbol = "NEW-MINING-SHIP"

            mock_data = MagicMock()
            mock_data.ship = mock_ship

            mock_parsed = MagicMock()
            mock_parsed.data = mock_data

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.parsed = mock_parsed

            mock_purchase.return_value = mock_response

            result = await shipyard_manager.purchase_mining_ship("TEST-SYSTEM")

            assert result is not None
            assert result.parsed.data.ship.symbol == "NEW-MINING-SHIP"

            expected_body = PurchaseShipBody(
                ship_type=ShipType.SHIP_MINING_DRONE,
                waypoint_symbol="SHIPYARD-1"
            )
            mock_purchase.assert_called_once_with(
                client=shipyard_manager.client,
                body=expected_body
            )


@pytest.mark.asyncio
async def test_purchase_mining_ship_no_ships_available(shipyard_manager):
    """Test purchasing when no mining ships are available"""
    with patch.object(
        shipyard_manager,
        'find_mining_ship_in_nearby_systems',
        new_callable=AsyncMock
    ) as mock_find:
        mock_find.return_value = None

        result = await shipyard_manager.purchase_mining_ship("TEST-SYSTEM")

        assert result is None
        mock_find.assert_called_once_with("TEST-SYSTEM", min_fuel_capacity=None)


@pytest.mark.asyncio
async def test_purchase_mining_ship_failure(shipyard_manager):
    """Test purchase failure"""
    with patch.object(
        shipyard_manager,
        'find_available_mining_ship',
        new_callable=AsyncMock
    ) as mock_find:
        mock_find.return_value = (
            "SHIPYARD-1",
            {
                'type': 'SHIP_MINING_DRONE',
                'purchasePrice': 90000
            }
        )

        with patch(
            'game.shipyard.purchase_ship.asyncio_detailed',
            new_callable=AsyncMock
        ) as mock_purchase:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.content = b"Not enough credits"
            mock_purchase.return_value = mock_response

            result = await shipyard_manager.purchase_mining_ship("TEST-SYSTEM")

            assert result is None
            mock_purchase.assert_called_once()
