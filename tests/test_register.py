import pytest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
from space_traders_api_client.models.faction_symbol import FactionSymbol
from space_traders_api_client.types import Response
from space_traders_api_client.models.register_response_201 import RegisterResponse201
from space_traders_api_client.models.register_response_201_data import RegisterResponse201Data
from space_traders_api_client.models.agent import Agent
from space_traders_api_client.models.contract import Contract
from space_traders_api_client.models.faction import Faction
from space_traders_api_client.models.ship import Ship
from space_traders_api_client.models.cooldown import Cooldown
from game.register import RegistrationManager
from http import HTTPStatus
from tests.factories import (
    AgentFactory,
    ShipFactory,
    FactionFactory,
    ContractFactory,
)

@pytest.fixture
def registration_manager():
    return RegistrationManager()

@pytest.fixture
def mock_success_response():
    # Create mock response data
    token = "eyJhbGciOiJS...c1ajwC9XVoG3A"
    
    agent = AgentFactory(symbol="TEST_AGENT")  # Override sequence to match test expectations
    contract = ContractFactory()
    faction = FactionFactory()
    ship = ShipFactory()

    # Convert contract datetime fields to ISO format for API response
    contract_dict = contract.to_dict()
    contract_dict["expiration"] = contract.expiration.isoformat()
    contract_dict["deadlineToAccept"] = contract.deadline_to_accept.isoformat()

    # Convert camelCase keys to snake_case
    def camel_to_snake(name):
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        # Special case for 'type' -> 'type_'
        return name.replace("type", "type_") if name == "type" else name
    
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
        contract=Contract(**contract_kwargs),  # Use transformed kwargs
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
                "contract": contract_dict,  # Use the dict with serialized dates
                "faction": faction.to_dict(),
                "ship": ship.to_dict()
            }
        }).encode(),
        headers={},
        parsed=response
    )

@pytest.fixture
def token_file_path(tmp_path):
    """Fixture providing a temporary path for the token file"""
    return tmp_path / "token.json"

@pytest.fixture
def registration_manager(token_file_path):
    """Fixture providing a RegistrationManager instance with a temporary token file path"""
    manager = RegistrationManager()
    manager.token_file = str(token_file_path)
    return manager

def safe_path_exists(values):
    """Helper to create a safe mock for os.path.exists that won't exhaust"""
    def _exists(*args, **kwargs):
        try:
            return next(iterator)
        except StopIteration:
            return values[-1]  # Return last value as default
    iterator = iter(values)
    return _exists

def test_load_existing_token_no_file(registration_manager):
    """Test loading token when file doesn't exist"""
    with patch('os.path.exists', return_value=False):
        token = registration_manager.load_existing_token()
        assert token is None

def test_load_existing_token_with_file(registration_manager):
    """Test loading token from existing file"""
    mock_token = {'token': 'test-token-123'}
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_token))):
            token = registration_manager.load_existing_token()
            assert token == 'test-token-123'

def test_save_token_writes_token_to_file(registration_manager, token_file_path):
    """
    Test that save_token correctly writes the token to a file.
    
    Given: A registration manager and a token
    When: The token is saved
    Then: The token should be written to the file in the correct JSON format
    """
    # Arrange
    test_token = "test-token-123"
    expected_content = {"token": test_token}
    
    # Act
    registration_manager.save_token(test_token)
    
    # Assert
    assert token_file_path.exists(), "Token file should be created"
    saved_content = json.loads(token_file_path.read_text())
    assert saved_content == expected_content, "Token should be saved in correct JSON format"

def test_save_token_creates_directory_if_missing(registration_manager, tmp_path):
    """
    Test that save_token creates the directory structure if it doesn't exist.
    
    Given: A registration manager with a token file path in a non-existent directory
    When: A token is saved
    Then: The directory should be created and the token should be saved
    """
    # Arrange
    nested_path = tmp_path / "nested" / "path" / "token.json"
    registration_manager.token_file = str(nested_path)
    test_token = "test-token-123"
    
    # Act
    registration_manager.save_token(test_token)
    
    # Assert
    assert nested_path.exists(), "Token file should be created in nested directory"
    saved_content = json.loads(nested_path.read_text())
    assert saved_content["token"] == test_token, "Token should be saved correctly"

def test_save_token_overwrites_existing_file(registration_manager, token_file_path):
    """
    Test that save_token overwrites an existing token file.
    
    Given: A registration manager and an existing token file
    When: A new token is saved
    Then: The file should be overwritten with the new token
    """
    # Arrange
    initial_token = {"token": "old-token"}
    token_file_path.write_text(json.dumps(initial_token))
    new_token = "new-token-123"
    
    # Act
    registration_manager.save_token(new_token)
    
    # Assert
    saved_content = json.loads(token_file_path.read_text())
    assert saved_content["token"] == new_token, "New token should overwrite old token"

def test_register_agent_success(registration_manager, mock_success_response):
    """Test successful registration of a new agent"""
    with patch('space_traders_api_client.api.default.register.sync_detailed',
               return_value=mock_success_response), \
         patch('os.path.exists', side_effect=safe_path_exists([False, True])), \
         patch('builtins.open', mock_open(read_data='{"token": "eyJhbGciOiJS...c1ajwC9XVoG3A"}')):
        success = registration_manager.register_agent(
            symbol="TEST_AGENT",
            faction=FactionSymbol("COSMIC")
        )
        assert success is True
        # Verify token was saved
        token = registration_manager.load_existing_token()
        assert token == "eyJhbGciOiJS...c1ajwC9XVoG3A"

def test_register_agent_existing_token(registration_manager):
    """Test registration when token already exists"""
    # Mock existing token
    with patch('builtins.open', mock_open(read_data='{"token": "test-token"}')), \
         patch('os.path.exists', return_value=True):
        success = registration_manager.register_agent(
            symbol="TEST_AGENT",
            faction=FactionSymbol("COSMIC")
        )
        assert success is False

def test_register_agent_failure(registration_manager):
    """Test registration failure"""
    error_response = Response(
        status_code=HTTPStatus.BAD_REQUEST,
        content=b'{"error":{"message":"Registration failed"}}',
        headers={},
        parsed=None
    )
    
    with patch('space_traders_api_client.api.default.register.sync_detailed',
               return_value=error_response):
        with pytest.raises(Exception) as exc_info:
            registration_manager.register_agent(
                symbol="TEST_AGENT",
                faction=FactionSymbol("COSMIC")
            )
        assert "Registration failed" in str(exc_info.value)

def test_register_agent_direct(mock_success_response):
    """Test registering an agent directly with RegistrationManager"""
    with patch('space_traders_api_client.api.default.register.sync_detailed',
               return_value=mock_success_response), \
         patch('os.path.exists', side_effect=safe_path_exists([False, True])), \
         patch('builtins.open', mock_open(read_data='{"token": "eyJhbGciOiJS...c1ajwC9XVoG3A"}')):
        manager = RegistrationManager()
        success = manager.register_agent(
            symbol="TEST_AGENT",
            faction=FactionSymbol("COSMIC")
        )
        assert success is True
        # Verify token was saved
        token = manager.load_existing_token()
        assert token == "eyJhbGciOiJS...c1ajwC9XVoG3A"

def test_register_with_email(registration_manager, mock_success_response):
    """Test registration with email parameter"""
    with patch('space_traders_api_client.api.default.register.sync_detailed',
               return_value=mock_success_response), \
         patch('os.path.exists', side_effect=safe_path_exists([False, True])), \
         patch('builtins.open', mock_open(read_data='{"token": "eyJhbGciOiJS...c1ajwC9XVoG3A"}')):
        success = registration_manager.register_agent(
            symbol="TEST_AGENT",
            faction=FactionSymbol("COSMIC"),
            email="test@example.com"
        )
        assert success is True
        # Verify token was saved
        token = registration_manager.load_existing_token()
        assert token == "eyJhbGciOiJS...c1ajwC9XVoG3A"
