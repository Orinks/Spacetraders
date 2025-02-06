"""Tests for shipyard operations"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from space_traders_api_client.models.ship_mount import ShipMount
from space_traders_api_client.models.ship_modification_transaction import ShipModificationTransaction
from space_traders_api_client.models.waypoint_trait import WaypointTrait
from space_traders_api_client.models.waypoint_trait_symbol import WaypointTraitSymbol
from space_traders_api_client.models.meta import Meta

from game.shipyard import ShipyardManager
from tests.factories import (
    WaypointFactory,
    WaypointTraitFactory,
    ShipMountFactory,
    MetaFactory
)


@pytest.fixture
def mock_client():
    client = MagicMock()
    return client


@pytest.fixture
def shipyard_manager(mock_client):
    return ShipyardManager(mock_client)


@pytest.fixture
def mock_waypoint():
    waypoint = WaypointFactory.build()
    # Ensure it has the shipyard trait
    shipyard_trait = WaypointTraitFactory.build(symbol=WaypointTraitSymbol.SHIPYARD)
    waypoint.traits = [shipyard_trait]
    return waypoint


def test_has_mining_mount(shipyard_manager):
    """Test detection of mining mounts"""
    # Test with mining laser
    mounts = [ShipMountFactory.build(symbol="MOUNT_MINING_LASER")]
    assert shipyard_manager.has_mining_mount(mounts) is True

    # Test with mining laser II
    mounts = [ShipMountFactory.build(symbol="MOUNT_MINING_LASER_II")]
    assert shipyard_manager.has_mining_mount(mounts) is True

    # Test with non-mining mount
    mounts = [ShipMountFactory.build(symbol="MOUNT_TURRET")]
    assert shipyard_manager.has_mining_mount(mounts) is False

    # Test with empty mounts
    assert shipyard_manager.has_mining_mount([]) is False


@pytest.mark.asyncio
async def test_find_shipyards_in_system(shipyard_manager, mock_waypoint):
    """Test finding shipyards in a system"""
    with patch(
        'game.shipyard.get_system_waypoints.asyncio_detailed'
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
            page=1
        )


@pytest.mark.asyncio
async def test_find_shipyards_multiple_pages(shipyard_manager, mock_waypoint):
    """Test finding shipyards across multiple pages"""
    with patch(
        'game.shipyard.get_system_waypoints.asyncio_detailed'
    ) as mock_get:
        # Setup mock responses for two pages
        response1 = MagicMock()
        response1.status_code = 200
        response1.parsed.data = [mock_waypoint]
        response1.parsed.meta = MetaFactory.build(total=40)  # 2 pages (20 per page)

        response2 = MagicMock()
        response2.status_code = 200
        response2.parsed.data = [mock_waypoint]
        response2.parsed.meta = MetaFactory.build(total=40)

        mock_get.side_effect = [response1, response2]

        shipyards = await shipyard_manager.find_shipyards_in_system("TEST-SYSTEM")
        assert len(shipyards) == 2
        assert mock_get.call_count == 2


@pytest.mark.asyncio
async def test_find_available_mining_ship(shipyard_manager):
    """Test finding available mining ships"""
    # Mock finding shipyards
    with patch.object(
        shipyard_manager,
        'find_shipyards_in_system'
    ) as mock_find:
        mock_find.return_value = ["SHIPYARD-1", "SHIPYARD-2"]

        # Mock getting shipyard info
        with patch.object(
            shipyard_manager,
            'get_shipyard_info'
        ) as mock_info:
            # First shipyard has expensive ship
            mock_info.side_effect = [
                {
                    'ships': [{
                        'type': 'SHIP_MINING_DRONE',
                        'purchasePrice': 100000
                    }]
                },
                # Second shipyard has cheaper ship
                {
                    'ships': [{
                        'type': 'SHIP_MINING_DRONE',
                        'purchasePrice': 90000
                    }]
                }
            ]

            result = await shipyard_manager.find_available_mining_ship("TEST-SYSTEM")
            assert result is not None
            waypoint, ship = result
            assert waypoint == "SHIPYARD-2"
            assert ship['purchasePrice'] == 90000


@pytest.mark.asyncio
async def test_purchase_mining_ship(shipyard_manager):
    """Test purchasing a mining ship"""
    # Mock finding available ship
    with patch.object(
        shipyard_manager,
        'find_available_mining_ship'
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
            'game.shipyard.purchase_ship.asyncio_detailed'
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

            mock_purchase.assert_called_once_with(
                client=shipyard_manager.client,
                json_body={"shipType": "SHIP_MINING_DRONE"},
                waypoint_symbol="SHIPYARD-1"
            )


@pytest.mark.asyncio
async def test_purchase_mining_ship_no_ships_available(shipyard_manager):
    """Test attempting to purchase when no ships are available"""
    with patch.object(
        shipyard_manager,
        'find_available_mining_ship'
    ) as mock_find:
        mock_find.return_value = None

        result = await shipyard_manager.purchase_mining_ship("TEST-SYSTEM")
        assert result is None


@pytest.mark.asyncio
async def test_purchase_mining_ship_failure(shipyard_manager):
    """Test handling purchase failure"""
    with patch.object(
        shipyard_manager,
        'find_available_mining_ship'
    ) as mock_find:
        mock_find.return_value = (
            "SHIPYARD-1",
            {
                'type': 'SHIP_MINING_DRONE',
                'purchasePrice': 90000
            }
        )

        with patch(
            'game.shipyard.purchase_ship.asyncio_detailed'
        ) as mock_purchase:
            response = MagicMock()
            response.status_code = 400
            response.content = b"Not enough credits"
            mock_purchase.return_value = response

            result = await shipyard_manager.purchase_mining_ship("TEST-SYSTEM")
            assert result is None