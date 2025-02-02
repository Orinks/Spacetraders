import pytest
from unittest.mock import MagicMock, patch

from game.contract_manager import ContractManager
from space_traders_api_client.models.contract import Contract
from space_traders_api_client.models.contract_deliver_good import (
    ContractDeliverGood
)
from space_traders_api_client.models.contract_terms import ContractTerms
from space_traders_api_client.models.get_contracts_response_200 import (
    GetContractsResponse200
)
from space_traders_api_client.models.get_contract_response_200 import (
    GetContractResponse200
)
from space_traders_api_client.models.accept_contract_response_200 import (
    AcceptContractResponse200
)
from space_traders_api_client.models.deliver_contract_response_200 import (
    DeliverContractResponse200
)
from space_traders_api_client.models.fulfill_contract_response_200 import (
    FulfillContractResponse200
)
from space_traders_api_client.models.meta import Meta


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def contract_manager(mock_client):
    return ContractManager(mock_client)


@pytest.fixture
def mock_contract():
    contract = MagicMock(spec=Contract)
    contract.id = "test-contract-1"
    contract.terms = MagicMock(spec=ContractTerms)
    contract.terms.deliver = [
        MagicMock(
            spec=ContractDeliverGood,
            trade_symbol="TEST_GOOD",
            units_required=10,
            destination_symbol="TEST-DEST",
            units_fulfilled=0
        )
    ]
    return contract


@pytest.mark.asyncio
async def test_update_contracts_success(
    contract_manager,
    mock_client,
    mock_contract
):
    """Test successful contract update"""
    with patch(
        'game.contract_manager.get_contracts.asyncio_detailed'
    ) as mock_get:
        response = MagicMock()
        response.status_code = 200
        response.parsed = GetContractsResponse200(
            data=[mock_contract],
            meta=Meta(total=1)
        )
        mock_get.return_value = response

        await contract_manager.update_contracts()

        mock_get.assert_called_once_with(client=mock_client)
        assert len(contract_manager.contracts) == 1
        assert contract_manager.contracts[mock_contract.id] == mock_contract


@pytest.mark.asyncio
async def test_update_contracts_failure(contract_manager, mock_client):
    """Test contract update failure"""
    with patch(
        'game.contract_manager.get_contracts.asyncio_detailed'
    ) as mock_get:
        response = MagicMock()
        response.status_code = 404
        response.parsed = None
        mock_get.return_value = response

        await contract_manager.update_contracts()

        mock_get.assert_called_once_with(client=mock_client)
        assert len(contract_manager.contracts) == 0


@pytest.mark.asyncio
async def test_update_contracts_exception(contract_manager, mock_client):
    """Test contract update with exception"""
    with patch(
        'game.contract_manager.get_contracts.asyncio_detailed'
    ) as mock_get:
        mock_get.side_effect = Exception("API Error")

        await contract_manager.update_contracts()

        mock_get.assert_called_once_with(client=mock_client)
        assert len(contract_manager.contracts) == 0


@pytest.mark.asyncio
async def test_accept_contract_success(contract_manager, mock_client):
    """Test successful contract acceptance"""
    with patch(
        'game.contract_manager.accept_contract.asyncio_detailed'
    ) as mock_accept:
        response = MagicMock()
        response.status_code = 200
        response.parsed = AcceptContractResponse200(data={
            "contract": MagicMock(),
            "agent": MagicMock()
        })
        mock_accept.return_value = response

        with patch(
            'game.contract_manager.ContractManager.update_contracts'
        ) as mock_update:
            result = await contract_manager.accept_contract("test-contract-1")

            mock_accept.assert_called_once_with(
                contract_id="test-contract-1",
                client=mock_client
            )
            mock_update.assert_called_once()
            assert result is True


@pytest.mark.asyncio
async def test_accept_contract_failure(contract_manager, mock_client):
    """Test contract acceptance failure"""
    with patch(
        'game.contract_manager.accept_contract.asyncio_detailed'
    ) as mock_accept:
        response = MagicMock()
        response.status_code = 400
        mock_accept.return_value = response

        result = await contract_manager.accept_contract("test-contract-1")

        mock_accept.assert_called_once_with(
            contract_id="test-contract-1",
            client=mock_client
        )
        assert result is False


@pytest.mark.asyncio
async def test_deliver_contract_cargo_success(contract_manager, mock_client):
    """Test successful cargo delivery"""
    with patch(
        'game.contract_manager.deliver_contract.asyncio_detailed'
    ) as mock_deliver:
        response = MagicMock()
        response.status_code = 200
        response.parsed = DeliverContractResponse200(data={
            "contract": MagicMock(),
            "cargo": MagicMock()
        })
        mock_deliver.return_value = response

        result = await contract_manager.deliver_contract_cargo(
            "test-contract-1",
            "test-ship-1",
            "TEST_GOOD",
            10
        )

        mock_deliver.assert_called_once()
        assert result is True


@pytest.mark.asyncio
async def test_deliver_contract_cargo_failure(contract_manager, mock_client):
    """Test cargo delivery failure"""
    with patch(
        'game.contract_manager.deliver_contract.asyncio_detailed'
    ) as mock_deliver:
        response = MagicMock()
        response.status_code = 400
        mock_deliver.return_value = response

        result = await contract_manager.deliver_contract_cargo(
            "test-contract-1",
            "test-ship-1",
            "TEST_GOOD",
            10
        )

        mock_deliver.assert_called_once()
        assert result is False


@pytest.mark.asyncio
async def test_fulfill_contract_success(contract_manager, mock_client):
    """Test successful contract fulfillment"""
    with patch(
        'game.contract_manager.fulfill_contract.asyncio_detailed'
    ) as mock_fulfill:
        response = MagicMock()
        response.status_code = 200
        response.parsed = FulfillContractResponse200(data={
            "contract": MagicMock(),
            "agent": MagicMock()
        })
        mock_fulfill.return_value = response

        with patch(
            'game.contract_manager.ContractManager.update_contracts'
        ) as mock_update:
            result = await contract_manager.fulfill_contract("test-contract-1")

            mock_fulfill.assert_called_once_with(
                contract_id="test-contract-1",
                client=mock_client
            )
            mock_update.assert_called_once()
            assert result is True


@pytest.mark.asyncio
async def test_fulfill_contract_failure(contract_manager, mock_client):
    """Test contract fulfillment failure"""
    with patch(
        'game.contract_manager.fulfill_contract.asyncio_detailed'
    ) as mock_fulfill:
        response = MagicMock()
        response.status_code = 400
        mock_fulfill.return_value = response

        result = await contract_manager.fulfill_contract("test-contract-1")

        mock_fulfill.assert_called_once_with(
            contract_id="test-contract-1",
            client=mock_client
        )
        assert result is False


@pytest.mark.asyncio
async def test_process_contract_fulfilled(
    contract_manager,
    mock_client,
    mock_contract
):
    """Test processing a fulfilled contract"""
    with patch(
        'game.contract_manager.get_contract.asyncio'
    ) as mock_get:
        contract_response = GetContractResponse200(
            data=MagicMock(fulfilled=True)
        )
        mock_get.return_value = contract_response

        with patch(
            'game.contract_manager.ContractManager.fulfill_contract'
        ) as mock_fulfill:
            await contract_manager.process_contract(mock_contract)

            mock_get.assert_called_once_with(
                contract_id=mock_contract.id,
                client=mock_client
            )
            mock_fulfill.assert_called_once_with(mock_contract.id)


@pytest.mark.asyncio
async def test_process_contract_not_fulfilled(
    contract_manager,
    mock_client,
    mock_contract
):
    """Test processing a non-fulfilled contract"""
    with patch(
        'game.contract_manager.get_contract.asyncio'
    ) as mock_get:
        contract_response = GetContractResponse200(
            data=MagicMock(fulfilled=False)
        )
        mock_get.return_value = contract_response

        with patch(
            'game.contract_manager.ContractManager.fulfill_contract'
        ) as mock_fulfill:
            await contract_manager.process_contract(mock_contract)

            mock_get.assert_called_once_with(
                contract_id=mock_contract.id,
                client=mock_client
            )
            mock_fulfill.assert_not_called()


@pytest.mark.asyncio
async def test_process_contract_invalid_format(contract_manager):
    """Test processing a contract with invalid format"""
    invalid_contract = MagicMock(spec=Contract)
    invalid_contract.id = "test-contract-1"
    # No terms attribute

    await contract_manager.process_contract(invalid_contract)
    # Should not raise any exceptions


@pytest.mark.asyncio
async def test_process_contract_no_delivery_terms(contract_manager):
    """Test processing a contract with no delivery terms"""
    contract = MagicMock(spec=Contract)
    contract.id = "test-contract-1"
    contract.terms = MagicMock(spec=ContractTerms)
    # No deliver attribute

    await contract_manager.process_contract(contract)
    # Should not raise any exceptions


@pytest.mark.asyncio
async def test_process_contract_invalid_delivery(contract_manager):
    """Test processing a contract with invalid delivery format"""
    contract = MagicMock(spec=Contract)
    contract.id = "test-contract-1"
    contract.terms = MagicMock(spec=ContractTerms)
    contract.terms.deliver = [
        MagicMock(
            spec=ContractDeliverGood
            # Missing required attributes
        )
    ]

    await contract_manager.process_contract(contract)
    # Should not raise any exceptions


@pytest.mark.asyncio
async def test_process_contract_api_error(
    contract_manager,
    mock_client,
    mock_contract
):
    """Test processing a contract with API error"""
    with patch(
        'game.contract_manager.get_contract.asyncio'
    ) as mock_get:
        mock_get.side_effect = Exception("API Error")

        await contract_manager.process_contract(mock_contract)
        # Should not raise any exceptions