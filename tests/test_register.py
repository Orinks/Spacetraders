"""Tests for registration functionality"""
import json
import asyncio
from unittest.mock import patch, mock_open
import pytest
from space_traders_api_client.models.faction_symbol import FactionSymbol
from space_traders_api_client.types import Response
from space_traders_api_client.models.register_response_201 import (
    RegisterResponse201
)
from space_traders_api_client.models.register_response_201_data import (
    RegisterResponse201Data
)
from space_traders_api_client.models.contract import Contract
from game.register import RegistrationManager
from http import HTTPStatus
from tests.factories import (
    AgentFactory,
    ShipFactory,
    FactionFactory,
    ContractFactory,
)


@pytest.fixture
async def token_file_path(tmp_path):
    """Fixture providing a temporary path for the token file."""
    return tmp_path / "token.json"


@pytest.fixture
async def registration_manager(token_file_path):
    """Fixture providing a RegistrationManager instance."""
    manager = RegistrationManager()
    manager.token_file = str(token_file_path)
    yield manager
    # Cleanup if needed
    if hasattr(manager, 'rate_limiter'):
        await manager.rate_limiter.cleanup()


@pytest.fixture
async def mock_success_response():
    """Create mock response data for successful registration."""
    token = "eyJhbGciOiJS...c1ajwC9XVoG3A"

    # Create test data using factories
    agent = AgentFactory(symbol="TEST_AGENT")
    contract = ContractFactory()
    faction = FactionFactory()
    ship = ShipFactory()

    # Convert contract datetime fields to ISO format
    contract_dict = contract.to_dict()
    contract_dict["expiration"] = contract.expiration.isoformat()
    contract_dict["deadlineToAccept"] = (
        contract.deadline_to_accept.isoformat()
    )

    # Convert camelCase keys to snake_case
    def camel_to_snake(name):
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        if name == "type":
            return name.replace("type", "type_")
        return name

    # Convert keys with special handling for type -> type_
    contract_kwargs = {}
    for key, value in contract_dict.items():
        snake_key = camel_to_snake(key)
        if snake_key == "type":
            contract_kwargs["type_"] = value
        else:
            contract_kwargs[snake_key] = value

    response_data = RegisterResponse201Data(
        token=token,
        agent=agent,
        contract=Contract(**contract_kwargs),
        faction=faction,
        ship=ship
    )

    response = RegisterResponse201(data=response_data)
    return Response(
        status_code=HTTPStatus.CREATED,
        content=json.dumps({
            "data": {
                "token": token,
                "agent": agent.to_dict(),
                "contract": contract_dict,
                "faction": faction.to_dict(),
                "ship": ship.to_dict()
            }
        }).encode(),
        headers={},
        parsed=response
    )


def safe_path_exists(values):
    """Helper to create a safe mock for os.path.exists.

    Args:
        values: List of boolean values to return in sequence

    Returns:
        Function that returns values in sequence, with last value as default
    """
    def _exists(*args, **kwargs):
        nonlocal iterator
        try:
            return next(iterator)
        except StopIteration:
            return values[-1]  # Return last value as default
    iterator = iter(values)
    return _exists


@pytest.mark.asyncio
async def test_load_existing_token_no_file(registration_manager):
    """Test loading token when file doesn't exist."""
    with patch('os.path.exists', return_value=False):
        token = registration_manager.load_existing_token()
        assert token is None


@pytest.mark.asyncio
async def test_load_existing_token_with_file(registration_manager):
    """Test loading token from existing file."""
    mock_token = {'token': 'test-token-123'}
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data=json.dumps(mock_token))):
        token = registration_manager.load_existing_token()
        assert token == 'test-token-123'


@pytest.mark.asyncio
async def test_save_token_writes_token_to_file(
    registration_manager,
    token_file_path
):
    """Test that save_token correctly writes the token to a file."""
    test_token = "test-token-123"
    expected_content = {"token": test_token}

    registration_manager.save_token(test_token)

    assert token_file_path.exists()
    saved_content = json.loads(token_file_path.read_text())
    assert saved_content == expected_content


@pytest.mark.asyncio
async def test_save_token_creates_directory_if_missing(
    registration_manager,
    tmp_path
):
    """Test that save_token creates the directory structure."""
    nested_path = tmp_path / "nested" / "path" / "token.json"
    registration_manager.token_file = str(nested_path)
    test_token = "test-token-123"

    registration_manager.save_token(test_token)

    assert nested_path.exists()
    saved_content = json.loads(nested_path.read_text())
    assert saved_content["token"] == test_token


@pytest.mark.asyncio
async def test_save_token_overwrites_existing_file(
    registration_manager,
    token_file_path
):
    """Test that save_token overwrites an existing token file."""
    initial_token = {"token": "old-token"}
    token_file_path.write_text(json.dumps(initial_token))
    new_token = "new-token-123"

    registration_manager.save_token(new_token)

    saved_content = json.loads(token_file_path.read_text())
    assert saved_content["token"] == new_token


@pytest.mark.asyncio
async def test_register_agent_success(registration_manager, mock_success_response):
    """Test successful registration of a new agent."""
    with patch(
        'space_traders_api_client.api.default.register.sync_detailed',
        return_value=mock_success_response
    ), patch(
        'os.path.exists',
        side_effect=safe_path_exists([False, True])
    ), patch(
        'builtins.open',
        mock_open(read_data='{"token": "eyJhbGciOiJS...c1ajwC9XVoG3A"}')
    ):
        success = registration_manager.register_agent(
            symbol="TEST_AGENT",
            faction=FactionSymbol("COSMIC")
        )
        assert success is True
        token = registration_manager.load_existing_token()
        assert token == "eyJhbGciOiJS...c1ajwC9XVoG3A"


@pytest.mark.asyncio
async def test_register_agent_existing_token(registration_manager):
    """Test registration when token already exists."""
    with patch(
        'builtins.open',
        mock_open(read_data='{"token": "test-token"}')
    ), patch('os.path.exists', return_value=True):
        success = registration_manager.register_agent(
            symbol="TEST_AGENT",
            faction=FactionSymbol("COSMIC")
        )
        assert success is False


@pytest.mark.asyncio
async def test_register_agent_failure(registration_manager):
    """Test registration failure."""
    error_response = Response(
        status_code=HTTPStatus.BAD_REQUEST,
        content=b'{"error":{"message":"Registration failed"}}',
        headers={},
        parsed=None
    )

    with patch(
        'space_traders_api_client.api.default.register.sync_detailed',
        return_value=error_response
    ):
        with pytest.raises(Exception) as exc_info:
            registration_manager.register_agent(
                symbol="TEST_AGENT",
                faction=FactionSymbol("COSMIC")
            )
        assert "Registration failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_register_agent_direct(mock_success_response):
    """Test registering an agent directly with RegistrationManager."""
    with patch(
        'space_traders_api_client.api.default.register.sync_detailed',
        return_value=mock_success_response
    ), patch(
        'os.path.exists',
        side_effect=safe_path_exists([False, True])
    ), patch(
        'builtins.open',
        mock_open(read_data='{"token": "eyJhbGciOiJS...c1ajwC9XVoG3A"}')
    ):
        manager = RegistrationManager()
        try:
            success = manager.register_agent(
                symbol="TEST_AGENT",
                faction=FactionSymbol("COSMIC")
            )
            assert success is True
            token = manager.load_existing_token()
            assert token == "eyJhbGciOiJS...c1ajwC9XVoG3A"
        finally:
            if hasattr(manager, 'rate_limiter'):
                await manager.rate_limiter.cleanup()


@pytest.mark.asyncio
async def test_register_with_email(registration_manager, mock_success_response):
    """Test registration with email parameter."""
    with patch(
        'space_traders_api_client.api.default.register.sync_detailed',
        return_value=mock_success_response
    ), patch(
        'os.path.exists',
        side_effect=safe_path_exists([False, True])
    ), patch(
        'builtins.open',
        mock_open(read_data='{"token": "eyJhbGciOiJS...c1ajwC9XVoG3A"}')
    ):
        success = registration_manager.register_agent(
            symbol="TEST_AGENT",
            faction=FactionSymbol("COSMIC"),
            email="test@example.com"
        )
        assert success is True
        token = registration_manager.load_existing_token()
        assert token == "eyJhbGciOiJS...c1ajwC9XVoG3A"