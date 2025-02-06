"""Tests for SpaceTrader system scanning functionality"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from space_traders_api_client.models.system import System
from space_traders_api_client.models.system_type import SystemType
from space_traders_api_client.models.get_systems_response_200 import GetSystemsResponse200
from space_traders_api_client.models.meta import Meta
from space_traders_api_client.types import Response

from game.trader import SpaceTrader
from tests.factories import SystemFactory


@pytest.fixture
def trader():
    """Create a SpaceTrader instance for testing"""
    return SpaceTrader("test_token")


@pytest.fixture
def mock_systems():
    """Create a list of mock systems"""
    return [
        SystemFactory(
            symbol=f"TEST-SYSTEM-{i}",
            sector_symbol="TEST-SECTOR",
            type_=SystemType.NEUTRON_STAR,
            x=i * 10,
            y=i * 10
        ) for i in range(5)
    ]


@pytest.mark.asyncio
async def test_scan_systems_success(trader, mock_systems):
    """Test successful system scanning"""
    with patch(
        'space_traders_api_client.api.systems.get_systems.asyncio_detailed'
    ) as mock_get:
        # Create mock response
        response = MagicMock()
        response.status_code = 200
        response.parsed = GetSystemsResponse200(
            data=mock_systems,
            meta=Meta(total=len(mock_systems))
        )
        mock_get.return_value = response

        # Call the method
        systems = await trader.scan_systems(limit=5)

        # Verify API call
        mock_get.assert_called_once_with(
            client=trader.agent_manager.client,
            limit=5
        )

        # Verify results
        assert len(systems) == 5
        for i, system in enumerate(systems):
            assert system.symbol == f"TEST-SYSTEM-{i}"
            assert system.type_ == SystemType.NEUTRON_STAR
            assert system.x == i * 10
            assert system.y == i * 10


@pytest.mark.asyncio
async def test_scan_systems_http_error(trader):
    """Test system scanning with HTTP error"""
    with patch(
        'space_traders_api_client.api.systems.get_systems.asyncio_detailed'
    ) as mock_get:
        # Create error response
        response = MagicMock()
        response.status_code = 404
        response.parsed = None
        mock_get.return_value = response

        # Call the method
        systems = await trader.scan_systems()

        # Verify error handling
        assert len(systems) == 0


@pytest.mark.asyncio
async def test_scan_systems_connection_error(trader):
    """Test system scanning with connection error"""
    with patch(
        'space_traders_api_client.api.systems.get_systems.asyncio_detailed',
        side_effect=Exception("Connection error")
    ) as mock_get:
        # Call the method
        systems = await trader.scan_systems()

        # Verify error handling
        assert len(systems) == 0
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_scan_systems_rate_limit(trader, mock_systems):
    """Test system scanning with rate limit response"""
    with patch(
        'space_traders_api_client.api.systems.get_systems.asyncio_detailed'
    ) as mock_get:
        # Create rate limit response
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.parsed = None

        # Create success response
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.parsed = GetSystemsResponse200(
            data=mock_systems,
            meta=Meta(total=len(mock_systems))
        )

        # Set up mock to first return rate limit, then success
        mock_get.side_effect = [rate_limit_response, success_response]

        # Call the method
        systems = await trader.scan_systems()

        # Verify error handling
        assert len(systems) == 0  # Since current implementation doesn't retry


@pytest.mark.asyncio
async def test_scan_systems_pagination(trader):
    """Test system scanning with pagination"""
    with patch(
        'space_traders_api_client.api.systems.get_systems.asyncio_detailed'
    ) as mock_get:
        # Create response with pagination metadata
        response = MagicMock()
        response.status_code = 200
        response.parsed = GetSystemsResponse200(
            data=[
                SystemFactory(
                    symbol=f"TEST-SYSTEM-{i}",
                    sector_symbol="TEST-SECTOR",
                    type_=SystemType.NEUTRON_STAR,
                    x=i * 10,
                    y=i * 10
                ) for i in range(2)  # Return fewer systems than requested
            ],
            meta=Meta(total=2)  # Indicate there are only 2 total systems
        )
        mock_get.return_value = response

        # Request more systems than available
        systems = await trader.scan_systems(limit=5)

        # Verify we get all available systems
        assert len(systems) == 2
        mock_get.assert_called_once_with(
            client=trader.agent_manager.client,
            limit=5
        )


@pytest.mark.asyncio
async def test_scan_systems_empty_response(trader):
    """Test system scanning with empty response"""
    with patch(
        'space_traders_api_client.api.systems.get_systems.asyncio_detailed'
    ) as mock_get:
        # Create empty response
        response = MagicMock()
        response.status_code = 200
        response.parsed = GetSystemsResponse200(
            data=[],
            meta=Meta(total=0)
        )
        mock_get.return_value = response

        # Call the method
        systems = await trader.scan_systems()

        # Verify handling of empty response
        assert len(systems) == 0
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_scan_systems_malformed_response(trader):
    """Test system scanning with malformed response"""
    with patch(
        'space_traders_api_client.api.systems.get_systems.asyncio_detailed'
    ) as mock_get:
        # Create malformed response
        response = MagicMock()
        response.status_code = 200
        response.parsed = None  # Missing parsed data
        mock_get.return_value = response

        # Call the method
        systems = await trader.scan_systems()

        # Verify error handling
        assert len(systems) == 0
        mock_get.assert_called_once()