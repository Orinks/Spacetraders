"""Tests for contract manager"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone

from space_traders_api_client.models.ship_nav_status import ShipNavStatus
from .factories import (
    ContractFactory,
    ShipFactory,
    ContractDeliverGood,
    MetaFactory,
    ShipMountFactory,
    WaypointFactory,
    WaypointTraitFactory,
)
from space_traders_api_client.models.meta import Meta
from space_traders_api_client.models.waypoint_trait_symbol import WaypointTraitSymbol
from game.contract_manager import ContractManager


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def contract_manager(mock_client):
    return ContractManager(mock_client)


@pytest.fixture
def mock_contract():
    """Create a mock contract with delivery requirements"""
    return ContractFactory.build(
        terms__deliver=[
            ContractDeliverGood(
                trade_symbol="TEST_GOOD",
                destination_symbol="TEST-DEST",
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


@pytest.mark.asyncio
async def test_update_contracts_success(contract_manager, mock_client, mock_contract):
    """Test successful contract update"""
    with patch('game.contract_manager.get_contracts.asyncio_detailed', new_callable=AsyncMock) as mock_get:
        response = MagicMock()
        response.status_code = 200
        response.parsed.data = [mock_contract]
        response.parsed.meta = MetaFactory.build(total=1)
        mock_get.return_value = response

        await contract_manager.update_contracts()

        # Check called once since it was successful
        assert mock_get.call_count == 1
        mock_get.assert_called_with(client=mock_client)
        assert len(contract_manager.contracts) == 1
        assert contract_manager.contracts[mock_contract.id] == mock_contract


@pytest.mark.asyncio
async def test_update_contracts_failure(contract_manager, mock_client):
    """Test contract update failure"""
    with patch('game.contract_manager.get_contracts.asyncio_detailed', new_callable=AsyncMock) as mock_get:
        response = MagicMock()
        response.status_code = 404
        response.parsed = None
        mock_get.return_value = response

        await contract_manager.update_contracts()

        # Check that it attempted the retry mechanism (3 tries)
        assert mock_get.call_count == 3
        mock_get.assert_called_with(client=mock_client)
        assert len(contract_manager.contracts) == 0


@pytest.mark.asyncio
async def test_update_contracts_exception(contract_manager, mock_client):
    """Test contract update with exception"""
    with patch('game.contract_manager.get_contracts.asyncio_detailed', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("API Error")

        await contract_manager.update_contracts()

        # Check that it attempted the retry mechanism (3 tries)
        assert mock_get.call_count == 3
        mock_get.assert_called_with(client=mock_client)
        assert len(contract_manager.contracts) == 0


@pytest.mark.asyncio
async def test_accept_contract_success(contract_manager, mock_client):
    """Test successful contract acceptance"""
    with patch('game.contract_manager.accept_contract.asyncio_detailed', new_callable=AsyncMock) as mock_accept:
        response = MagicMock()
        response.status_code = 200
        response.parsed.data = {
            "contract": MagicMock(),
            "agent": MagicMock()
        }
        mock_accept.return_value = response

        with patch('game.contract_manager.ContractManager.update_contracts', new_callable=AsyncMock) as mock_update:
            result = await contract_manager.accept_contract("test-contract-1")

            assert mock_accept.call_count == 1
            mock_accept.assert_called_with(
                contract_id="test-contract-1",
                client=mock_client
            )
            mock_update.assert_called_once()
            assert result is True


@pytest.mark.asyncio
async def test_accept_contract_failure(contract_manager, mock_client):
    """Test contract acceptance failure"""
    with patch('game.contract_manager.accept_contract.asyncio_detailed', new_callable=AsyncMock) as mock_accept:
        response = MagicMock()
        response.status_code = 400
        mock_accept.return_value = response

        result = await contract_manager.accept_contract("test-contract-1")

        assert mock_accept.call_count == 1
        mock_accept.assert_called_with(
            contract_id="test-contract-1",
            client=mock_client
        )
        assert result is False


@pytest.mark.asyncio
async def test_deliver_contract_cargo_success(contract_manager, mock_client):
    """Test successful cargo delivery"""
    with patch('game.contract_manager.dock_ship.asyncio_detailed', new_callable=AsyncMock) as mock_dock:
        dock_response = MagicMock()
        dock_response.status_code = 200
        mock_dock.return_value = dock_response

        with patch('game.contract_manager.deliver_contract.asyncio_detailed', new_callable=AsyncMock) as mock_deliver:
            response = MagicMock()
            response.status_code = 200
            response.parsed.data = {
                "contract": MagicMock(),
                "cargo": MagicMock()
            }
            mock_deliver.return_value = response

            result = await contract_manager.deliver_contract_cargo(
                "test-contract-1",
                "test-ship-1",
                "TEST_GOOD",
                10
            )

            assert mock_dock.call_count == 1
            mock_dock.assert_called_with(
                ship_symbol="test-ship-1",
                client=mock_client
            )
            mock_deliver.assert_called_once()
            assert result is True


@pytest.mark.asyncio
async def test_deliver_contract_cargo_failure(contract_manager, mock_client):
    """Test cargo delivery failure"""
    with patch('game.contract_manager.dock_ship.asyncio_detailed', new_callable=AsyncMock) as mock_dock:
        dock_response = MagicMock()
        dock_response.status_code = 200
        mock_dock.return_value = dock_response

        with patch('game.contract_manager.deliver_contract.asyncio_detailed', new_callable=AsyncMock) as mock_deliver:
            deliver_response = MagicMock()
            deliver_response.status_code = 400
            if hasattr(deliver_response, 'content'):
                deliver_response.content.decode.return_value = "Error"
            mock_deliver.return_value = deliver_response

            result = await contract_manager.deliver_contract_cargo(
                "test-contract-1",
                "test-ship-1",
                "TEST_GOOD",
                10
            )

            # Check that docking was attempted 3 times due to delivery failure
            assert mock_dock.call_count == 3
            mock_dock.assert_called_with(
                ship_symbol="test-ship-1",
                client=mock_client
            )
            assert mock_deliver.call_count == 3
            assert result is False


@pytest.mark.asyncio
async def test_fulfill_contract_success(contract_manager, mock_client):
    """Test successful contract fulfillment"""
    with patch('game.contract_manager.fulfill_contract.asyncio_detailed', new_callable=AsyncMock) as mock_fulfill:
        response = MagicMock()
        response.status_code = 200
        response.parsed.data = {
            "contract": MagicMock(),
            "agent": MagicMock()
        }
        mock_fulfill.return_value = response

        with patch('game.contract_manager.ContractManager.update_contracts', new_callable=AsyncMock) as mock_update:
            result = await contract_manager.fulfill_contract("test-contract-1")

            assert mock_fulfill.call_count == 1
            mock_fulfill.assert_called_with(
                contract_id="test-contract-1",
                client=mock_client
            )
            mock_update.assert_called_once()
            assert result is True


@pytest.mark.asyncio
async def test_fulfill_contract_failure(contract_manager, mock_client):
    """Test contract fulfillment failure"""
    with patch('game.contract_manager.fulfill_contract.asyncio_detailed', new_callable=AsyncMock) as mock_fulfill:
        response = MagicMock()
        response.status_code = 400
        mock_fulfill.return_value = response

        result = await contract_manager.fulfill_contract("test-contract-1")

        assert mock_fulfill.call_count == 1
        mock_fulfill.assert_called_with(
            contract_id="test-contract-1",
            client=mock_client
        )
        assert result is False


@pytest.mark.asyncio
async def test_process_contract_fulfilled(
    contract_manager,
    mock_client,
    mock_contract,
    mock_ships,
    mock_survey_manager
):
    """Test processing a fulfilled contract"""
    with patch('game.contract_manager.get_contract.asyncio_detailed', new_callable=AsyncMock) as mock_get:
        get_response = MagicMock()
        get_response.status_code = 200
        get_response.parsed.data = MagicMock(fulfilled=True)
        mock_get.return_value = get_response

        with patch('game.contract_manager.ContractManager.fulfill_contract', new_callable=AsyncMock) as mock_fulfill:
            await contract_manager.process_contract(
                mock_contract,
                mock_ships,
                mock_survey_manager
            )

            assert mock_get.call_count == 1
            mock_get.assert_called_with(
                contract_id=mock_contract.id,
                client=mock_client
            )
            mock_fulfill.assert_called_once_with(mock_contract.id)


@pytest.mark.asyncio
async def test_process_contract_not_fulfilled(
    contract_manager,
    mock_client,
    mock_contract,
    mock_ships,
    mock_survey_manager
):
    """Test processing a non-fulfilled contract"""
    with patch('game.contract_manager.get_contract.asyncio_detailed', new_callable=AsyncMock) as mock_get:
        get_response = MagicMock()
        get_response.status_code = 200
        get_response.parsed.data = MagicMock(
            fulfilled=False,
            terms=mock_contract.terms
        )
        mock_get.return_value = get_response

        with patch('game.contract_manager.ContractManager.fulfill_contract', new_callable=AsyncMock) as mock_fulfill:
            await contract_manager.process_contract(
                mock_contract,
                mock_ships,
                mock_survey_manager
            )

            assert mock_get.call_count == 1
            mock_get.assert_called_with(
                contract_id=mock_contract.id,
                client=mock_client
            )
            mock_fulfill.assert_not_called()


@pytest.mark.asyncio
async def test_process_contract_purchase_mining_ship(
    contract_manager,
    mock_client,
    mock_contract,
    mock_ships,
    mock_survey_manager
):
    """Test processing a contract that requires purchasing a mining ship"""
    # Create a ship without mining capabilities
    non_mining_ship = ShipFactory.build(
        nav__status=ShipNavStatus.DOCKED,
        nav__waypoint_symbol="TEST-WAYPOINT",
        nav__system_symbol="TEST-SYSTEM",
        cargo__capacity=100,
        cargo__units=0,
        mounts=[]  # No mining mounts
    )
    ships = {non_mining_ship.symbol: non_mining_ship}

    with patch('game.contract_manager.get_contract.asyncio_detailed', new_callable=AsyncMock) as mock_get:
        get_response = MagicMock()
        get_response.status_code = 200
        get_response.parsed.data = MagicMock(
            fulfilled=False,
            terms=mock_contract.terms
        )
        mock_get.return_value = get_response

        with patch.object(
            contract_manager.shipyard_manager,
            'get_ship_mounts',
            new_callable=AsyncMock
        ) as mock_mounts:
            mock_mounts.return_value = []  # No mining mounts

            with patch.object(
                contract_manager.shipyard_manager,
                'purchase_mining_ship',
                new_callable=AsyncMock
            ) as mock_purchase:
                mock_response = MagicMock()
                mock_response.parsed = MagicMock()
                mock_response.parsed.data = MagicMock()
                mock_response.parsed.data.ship = ShipFactory.build(
                    symbol="NEW-MINING-SHIP"
                )
                mock_purchase.return_value = mock_response

                await contract_manager.process_contract(
                    mock_contract,
                    ships,
                    mock_survey_manager
                )

                mock_purchase.assert_called_once_with(
                    system_symbol=non_mining_ship.nav.system_symbol
                )


@pytest.mark.asyncio
async def test_process_contract_invalid_format(
    contract_manager,
    mock_ships,
    mock_survey_manager
):
    """Test processing a contract with invalid format"""
    invalid_contract = ContractFactory.build()
    invalid_contract.terms = None  # Invalid format

    await contract_manager.process_contract(
        invalid_contract,
        mock_ships,
        mock_survey_manager
    )