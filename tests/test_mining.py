"""Tests for mining operations and survey management"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from space_traders_api_client.models.survey import Survey
from space_traders_api_client.models.extraction import Extraction
from space_traders_api_client.models.extraction_yield import ExtractionYield
from space_traders_api_client.models.survey_deposit import SurveyDeposit
from space_traders_api_client.models.survey_size import SurveySize
from space_traders_api_client.types import Response
from space_traders_api_client.models.waypoint import Waypoint # Added
from space_traders_api_client.models.waypoint_type import WaypointType # Added
from space_traders_api_client.models.ship import Ship # Added
from space_traders_api_client.models.ship_nav import ShipNav # Added
from space_traders_api_client.models.ship_cargo import ShipCargo # Added
from space_traders_api_client.models.ship_fuel import ShipFuel # Added


# Make sure the game module can be imported
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from game.mining import ExtractionResult, MiningTarget, MiningManager # Renamed SurveyManager
from game.system_manager import SystemManager # Added for MiningManager dependency
from game.rate_limiter import RateLimiter # Added, though likely mocked


@pytest.fixture
def mock_client(): # Added
    return AsyncMock()

@pytest.fixture
def mock_system_manager(): # Added
    sm = MagicMock(spec=SystemManager)
    sm.find_waypoints_by_type = MagicMock(return_value=[]) # Default empty list
    return sm

@pytest.fixture
def mock_survey():
    """Create a mock survey"""
    survey = Survey(
        signature="test-survey-1",
        symbol="TEST-WAYPOINT",
        deposits=[
            SurveyDeposit(symbol="IRON_ORE"),
            SurveyDeposit(symbol="COPPER_ORE")
        ],
        expiration=datetime.now() + timedelta(hours=1),
        size=SurveySize.MODERATE
    )
    # Ensure survey has to_dict method
    if not hasattr(survey, 'to_dict'):
        setattr(survey, 'to_dict', lambda: {
            'signature': survey.signature,
            'symbol': survey.symbol,
            'deposits': [{'symbol': d.symbol} for d in survey.deposits],
            'expiration': survey.expiration.isoformat(),
            'size': survey.size
        })
    return survey


@pytest.fixture
def mock_expired_survey():
    """Create a mock expired survey"""
    return Survey(
        signature="test-survey-2",
        symbol="TEST-WAYPOINT",
        deposits=[SurveyDeposit(symbol="IRON_ORE")],
        expiration=datetime.now() - timedelta(hours=1),
        size="SMALL"
    )


@pytest.fixture
def mock_extraction():
    """Create a mock extraction result"""
    return Extraction(
        ship_symbol="TEST-SHIP", # ship_symbol is part of Extraction model itself
        yield_=ExtractionYield(
            symbol="IRON_ORE",
            units=10
        )
    )

@pytest.fixture
def mock_ship(): # Added
    return Ship(
        symbol="TEST-SHIP",
        nav=ShipNav(
            system_symbol="SYS1",
            waypoint_symbol="SYS1-WP1",
            # other ShipNav fields if needed by tests
        ),
        cargo=ShipCargo(capacity=100, units=0, inventory=[]),
        fuel=ShipFuel(current=100, capacity=100)
        # other Ship fields if needed
    )


@pytest.fixture
def mining_manager(mock_client, mock_system_manager): # Updated fixture
    """Create a MiningManager instance"""
    manager = MiningManager(client=mock_client, system_manager=mock_system_manager)
    # Mock rate_limiter if its methods are called directly by MiningManager
    manager.rate_limiter = MagicMock(spec=RateLimiter)
    async def mock_execute(*args, **kwargs):
        api_call = args[0]
        # This simplified mock assumes the actual API call function (like create_survey.asyncio_detailed)
        # is what's passed and needs to be awaited with its specific kwargs.
        return await api_call(**kwargs)
    manager.rate_limiter.execute_with_retry = AsyncMock(side_effect=mock_execute)
    return manager


def test_extraction_result_creation(mock_survey, mock_extraction): # Renamed survey_manager to mining_manager
    """Test ExtractionResult initialization"""
    result = ExtractionResult(
        survey_signature=mock_survey.signature, # survey_signature can be "None" if no survey used
        extraction=mock_extraction
    )
    
    assert result.survey_signature == mock_survey.signature
    assert result.extraction == mock_extraction
    assert isinstance(result.timestamp, datetime)


def test_mining_target_creation(mock_survey): # Updated for MiningTarget changes
    """Test MiningTarget initialization"""
    waypoint_obj = Waypoint(symbol="TEST-WAYPOINT", system_symbol="SYS1", type_=WaypointType.ASTEROID_FIELD, x=0, y=0)
    target = MiningTarget(
        waypoint_symbol="TEST-WAYPOINT", # Changed from 'waypoint'
        resource_type="IRON_ORE",
        priority=1,
        survey=mock_survey,
        waypoint_obj=waypoint_obj
    )
    
    assert target.waypoint_symbol == "TEST-WAYPOINT"
    assert target.resource_type == "IRON_ORE"
    assert target.priority == 1
    assert target.survey == mock_survey
    assert target.waypoint_obj == waypoint_obj


# Class name updated to TestMiningManager
class TestMiningManager:

    def test_mining_manager_add_survey(self, mining_manager, mock_survey): # Renamed survey_manager to mining_manager
        """Test adding surveys to manager"""
        mining_manager.add_survey(mock_survey)
        assert mock_survey.signature in mining_manager.active_surveys
        assert len(mining_manager.active_surveys) == 1


    def test_mining_manager_expired_survey( # Renamed survey_manager to mining_manager
        self,
        mining_manager,
        mock_survey,
        mock_expired_survey
    ):
        """Test handling of expired surveys"""
        mining_manager.add_survey(mock_survey)
        mining_manager.add_survey(mock_expired_survey)

        active_surveys = mining_manager.get_active_surveys()
        assert len(active_surveys) == 1
        assert mock_expired_survey.signature not in mining_manager.active_surveys


    def test_mining_manager_get_surveys_for_waypoint(self, mining_manager, mock_survey): # Renamed survey_manager to mining_manager
        """Test filtering surveys by waypoint"""
        mining_manager.add_survey(mock_survey)

        waypoint_surveys = mining_manager.get_surveys_for_waypoint( # Method name unchanged
            "TEST-WAYPOINT"
        )
        assert len(waypoint_surveys) == 1
        assert waypoint_surveys[0] == mock_survey

        other_surveys = mining_manager.get_surveys_for_waypoint("OTHER-WAYPOINT")
        assert len(other_surveys) == 0


    def test_mining_manager_get_best_survey_for_resource_at_waypoint(self, mining_manager, mock_survey): # Updated method name
        """Test finding best survey for resource at a waypoint"""
        mining_manager.add_survey(mock_survey)

        # Test with the correct waypoint symbol from mock_survey
        best_survey = mining_manager.get_best_survey_for_resource_at_waypoint("IRON_ORE", mock_survey.symbol)
        assert best_survey == mock_survey

        no_survey_wrong_resource = mining_manager.get_best_survey_for_resource_at_waypoint("GOLD_ORE", mock_survey.symbol)
        assert no_survey_wrong_resource is None

        no_survey_wrong_waypoint = mining_manager.get_best_survey_for_resource_at_waypoint("IRON_ORE", "OTHER-WAYPOINT")
        assert no_survey_wrong_waypoint is None


    def test_mining_manager_track_extraction( # Renamed survey_manager to mining_manager
        self,
        mining_manager,
        mock_survey,
        mock_extraction
    ):
        """Test tracking extraction results"""
        mining_manager.track_extraction_result(mock_survey, mock_extraction, "TEST-WAYPOINT") # Added waypoint_symbol

        assert len(mining_manager.extraction_history) == 1
        result = mining_manager.extraction_history[0]
        assert result.survey_signature == mock_survey.signature
        assert result.extraction == mock_extraction

    def test_mining_manager_track_extraction_no_survey(self, mining_manager, mock_extraction):
        """Test tracking extraction results without a survey"""
        mining_manager.track_extraction_result(None, mock_extraction, "TEST-WAYPOINT-NO-SURVEY")

        assert len(mining_manager.extraction_history) == 1
        result = mining_manager.extraction_history[0]
        assert result.survey_signature == "None"
        assert result.extraction == mock_extraction


    def test_mining_manager_extraction_stats( # Renamed survey_manager to mining_manager
        self,
        mining_manager, # Renamed survey_manager to mining_manager
        mock_survey,
        mock_extraction
    ):
        """Test extraction statistics calculation"""
        mining_manager.track_extraction_result(mock_survey, mock_extraction, "TEST-WAYPOINT") # Added waypoint_symbol

        stats = mining_manager.get_extraction_stats()
        assert stats["average_yield"] == 10.0
        assert stats["success_rate"] == 1.0

        iron_stats = mining_manager.get_extraction_stats("IRON_ORE")
        assert iron_stats["average_yield"] == 10.0
        assert iron_stats["success_rate"] == 1.0

        gold_stats = mining_manager.get_extraction_stats("GOLD_ORE")
        assert gold_stats["average_yield"] == 0.0
        assert gold_stats["success_rate"] == 0.0

    def test_find_mining_targets(self, mining_manager, mock_system_manager): # New test
        """Test finding mining targets."""
        wp1 = Waypoint(symbol="AST-FIELD-1", system_symbol="SYS1", type_=WaypointType.ASTEROID_FIELD, x=10, y=20, traits=[])
        wp2 = Waypoint(symbol="AST-FIELD-2", system_symbol="SYS2", type_=WaypointType.ASTEROID_FIELD, x=30, y=40, traits=[])
        wp_planet = Waypoint(symbol="PLANET", system_symbol="SYS1", type_=WaypointType.PLANET, x=50,y=60, traits=[])

        mock_system_manager.find_waypoints_by_type.return_value = [wp1, wp2, wp_planet] # Will be filtered by type in SUT

        desired_resources = ["IRON_ORE", "ALUMINUM_ORE"]
        priority_map = {"IRON_ORE": 5, "ALUMINUM_ORE": 3}

        # Test without ship location
        targets = mining_manager.find_mining_targets(desired_resources, priority_map)
        # find_waypoints_by_type in SystemManager is mocked, but the one in MiningManager calls it.
        # The SUT's find_waypoints_by_type will filter for ASTEROID_FIELD
        # So, wp_planet should be filtered out by the call in mining_manager to system_manager.find_waypoints_by_type(WaypointType.ASTEROID_FIELD)
        # then it iterates desired_resources. So 2 targets * 2 resources = 4 potential targets
        # Based on the SUT, it only calls find_waypoints_by_type(WaypointType.ASTEROID_FIELD)
        mock_system_manager.find_waypoints_by_type.assert_called_once_with(WaypointType.ASTEROID_FIELD)

        # Reset mock for next call if needed, or ensure it's fine with multiple calls
        mock_system_manager.find_waypoints_by_type.return_value = [wp1, wp2] # Simulate the filtering already happened for ASTEROID_FIELD

        targets = mining_manager.find_mining_targets(desired_resources, priority_map)

        assert len(targets) == 4 # wp1 for IRON, wp1 for ALUMINUM, wp2 for IRON, wp2 for ALUMINUM
        assert targets[0].resource_type == "IRON_ORE" # Highest priority
        assert targets[0].priority == 5
        assert targets[1].resource_type == "IRON_ORE" # wp2 for IRON_ORE (same priority as wp1 for IRON_ORE)
        assert targets[1].priority == 5
        # Order between wp1 and wp2 for IRON_ORE might not be guaranteed if priorities are equal without system bonus.
        # Let's check if both exist for IRON_ORE
        iron_targets = [t for t in targets if t.resource_type == "IRON_ORE"]
        assert len(iron_targets) == 2
        assert any(t.waypoint_symbol == "AST-FIELD-1" for t in iron_targets)
        assert any(t.waypoint_symbol == "AST-FIELD-2" for t in iron_targets)


        # Test with ship location
        mock_system_manager.find_waypoints_by_type.return_value = [wp1, wp2] # Reset for this call
        targets_in_sys1 = mining_manager.find_mining_targets(desired_resources, priority_map, ship_location_system="SYS1")
        assert len(targets_in_sys1) == 4
        # AST-FIELD-1 for IRON_ORE should be highest due to system bonus
        assert targets_in_sys1[0].waypoint_symbol == "AST-FIELD-1"
        assert targets_in_sys1[0].resource_type == "IRON_ORE"
        assert targets_in_sys1[0].priority == 5 + 100 # 5 (resource) + 100 (system bonus)

        # AST-FIELD-1 for ALUMINUM_ORE should be next
        assert targets_in_sys1[1].waypoint_symbol == "AST-FIELD-1"
        assert targets_in_sys1[1].resource_type == "ALUMINUM_ORE"
        assert targets_in_sys1[1].priority == 3 + 100

        # Then AST-FIELD-2 for IRON_ORE
        assert targets_in_sys1[2].waypoint_symbol == "AST-FIELD-2"
        assert targets_in_sys1[2].resource_type == "IRON_ORE"
        assert targets_in_sys1[2].priority == 5 # No system bonus

    @pytest.mark.asyncio
    async def test_mining_manager_create_survey(self, mining_manager, mock_survey, mock_client): # Renamed
        """Test survey creation API interaction"""
        # Mock the API call via rate_limiter
        mock_api_response = Response(
            status_code=201,
            content=b"",
            headers={},
            parsed=type(
                "ParsedResponse",
                (),
                {"data": type("Data", (), {"surveys": [mock_survey], "cooldown": {}})} # Added cooldown for typical response
            )
        )
        # Instead of patching 'game.mining.create_survey.asyncio_detailed',
        # we ensure execute_with_retry calls the (mocked) create_survey.asyncio_detailed
        
        # We need to patch the actual API function that execute_with_retry will call
        with patch('space_traders_api_client.api.fleet.create_survey.asyncio_detailed', AsyncMock(return_value=mock_api_response)) as mock_api_call:
            survey = await mining_manager.create_survey("TEST-SHIP", "TEST-WAYPOINT") # Added waypoint symbol

            mining_manager.rate_limiter.execute_with_retry.assert_called_once_with(
                mock_api_call, # Check it's called with the patched API function
                task_name="create_survey_TEST-SHIP",
                ship_symbol="TEST-SHIP",
                client=mock_client
            )
            assert survey == mock_survey
            assert mock_survey.signature in mining_manager.active_surveys


    @pytest.mark.asyncio
    async def test_mining_manager_extract_resources_at_waypoint_with_survey( # Renamed
        self,
        mining_manager, # Renamed
        mock_ship, # Added mock_ship
        mock_survey,
        mock_extraction,
        mock_client # Added mock_client
    ):
        """Test resource extraction API interaction with a survey."""
        mock_ship.nav.waypoint_symbol = mock_survey.symbol # Ensure ship is at survey location
        
        # Mock the API call response
        mock_api_data = type('Data', (), {
            'extraction': mock_extraction,
            'cooldown': {}, # Typical response includes cooldown
            'cargo': mock_ship.cargo # API returns updated cargo
        })
        mock_api_parsed = type('ParsedResponse', (), {'data': mock_api_data})
        mock_api_response = Response(status_code=201, content=b"", headers={}, parsed=mock_api_parsed)

        with patch('space_traders_api_client.api.fleet.extract_resources.asyncio_detailed', AsyncMock(return_value=mock_api_response)) as mock_api_call:
            result = await mining_manager.extract_resources_at_waypoint( # Renamed method
                ship=mock_ship, # Pass ship object
                survey=mock_survey
            )

            mining_manager.rate_limiter.execute_with_retry.assert_called_once_with(
                mock_api_call,
                task_name=f"extract_resources_{mock_ship.symbol}",
                ship_symbol=mock_ship.symbol,
                client=mock_client,
                json_body={"survey": mock_survey.to_dict()}
            )

            assert result is not None
            assert result.ship_symbol == mock_extraction.ship_symbol # ship_symbol comes from Extraction model
            assert result.yield_.symbol == mock_extraction.yield_.symbol
            assert result.yield_.units == mock_extraction.yield_.units
            assert len(mining_manager.extraction_history) == 1
            # Check if ship's cargo was updated (assuming the mock_ship passed is updated by reference)
            assert mock_ship.cargo == mock_api_data.cargo


    @pytest.mark.asyncio
    async def test_mining_manager_extract_resources_at_waypoint_no_survey( # New test for no survey
        self,
        mining_manager,
        mock_ship,
        mock_extraction,
        mock_client
    ):
        """Test resource extraction API interaction without a survey."""
        mock_api_data = type('Data', (), {
            'extraction': mock_extraction,
            'cooldown': {},
            'cargo': mock_ship.cargo
        })
        mock_api_parsed = type('ParsedResponse', (), {'data': mock_api_data})
        mock_api_response = Response(status_code=201, content=b"", headers={}, parsed=mock_api_parsed)

        with patch('space_traders_api_client.api.fleet.extract_resources.asyncio_detailed', AsyncMock(return_value=mock_api_response)) as mock_api_call:
            result = await mining_manager.extract_resources_at_waypoint(
                ship=mock_ship,
                survey=None # Explicitly no survey
            )

            mining_manager.rate_limiter.execute_with_retry.assert_called_once_with(
                mock_api_call,
                task_name=f"extract_resources_{mock_ship.symbol}",
                ship_symbol=mock_ship.symbol,
                client=mock_client,
                json_body=None # Expect None or empty dict if no survey
            )

            assert result is not None
            assert len(mining_manager.extraction_history) == 1
            assert mining_manager.extraction_history[0].survey_signature == "None"