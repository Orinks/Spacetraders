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

from game.mining import ExtractionResult, MiningTarget, SurveyManager


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
    # Create a proper mock extraction with all required attributes
    extraction = Extraction(
        ship_symbol="TEST-SHIP",
        yield_=ExtractionYield(
            symbol="IRON_ORE",
            units=10
        )
    )
    # Ensure ship_symbol is set
    setattr(extraction, 'ship_symbol', "TEST-SHIP")
    return extraction


@pytest.fixture
def survey_manager():
    """Create a SurveyManager instance"""
    return SurveyManager(client=None)


def test_extraction_result_creation(mock_survey, mock_extraction):
    """Test ExtractionResult initialization"""
    result = ExtractionResult(
        survey_signature=mock_survey.signature,
        extraction=mock_extraction
    )

    assert result.survey_signature == mock_survey.signature
    assert result.extraction == mock_extraction
    assert isinstance(result.timestamp, datetime)


def test_mining_target_creation(mock_survey):
    """Test MiningTarget initialization"""
    target = MiningTarget(
        waypoint="TEST-WAYPOINT",
        resource_type="IRON_ORE",
        priority=1,
        survey=mock_survey
    )

    assert target.waypoint == "TEST-WAYPOINT"
    assert target.resource_type == "IRON_ORE"
    assert target.priority == 1
    assert target.survey == mock_survey


def test_survey_manager_add_survey(survey_manager, mock_survey):
    """Test adding surveys to manager"""
    survey_manager.add_survey(mock_survey)
    assert mock_survey.signature in survey_manager.active_surveys
    assert len(survey_manager.active_surveys) == 1


def test_survey_manager_expired_survey(
    survey_manager,
    mock_survey,
    mock_expired_survey
):
    """Test handling of expired surveys"""
    survey_manager.add_survey(mock_survey)
    survey_manager.add_survey(mock_expired_survey)

    active_surveys = survey_manager.get_active_surveys()
    assert len(active_surveys) == 1
    assert mock_expired_survey.signature not in survey_manager.active_surveys


def test_survey_manager_get_surveys_for_waypoint(survey_manager, mock_survey):
    """Test filtering surveys by waypoint"""
    survey_manager.add_survey(mock_survey)

    waypoint_surveys = survey_manager.get_surveys_for_waypoint(
        "TEST-WAYPOINT"
    )
    assert len(waypoint_surveys) == 1
    assert waypoint_surveys[0] == mock_survey

    other_surveys = survey_manager.get_surveys_for_waypoint("OTHER-WAYPOINT")
    assert len(other_surveys) == 0


def test_survey_manager_get_best_survey(survey_manager, mock_survey):
    """Test finding best survey for resource"""
    survey_manager.add_survey(mock_survey)

    best_survey = survey_manager.get_best_survey("IRON_ORE")
    assert best_survey == mock_survey

    no_survey = survey_manager.get_best_survey("GOLD_ORE")
    assert no_survey is None


def test_survey_manager_track_extraction(
    survey_manager,
    mock_survey,
    mock_extraction
):
    """Test tracking extraction results"""
    survey_manager.track_extraction_result(mock_survey, mock_extraction)

    assert len(survey_manager.extraction_history) == 1
    result = survey_manager.extraction_history[0]
    assert result.survey_signature == mock_survey.signature
    assert result.extraction == mock_extraction


def test_survey_manager_extraction_stats(
    survey_manager,
    mock_survey,
    mock_extraction
):
    """Test extraction statistics calculation"""
    # Add some extraction history
    survey_manager.track_extraction_result(mock_survey, mock_extraction)

    # Test overall stats
    stats = survey_manager.get_extraction_stats()
    assert stats["average_yield"] == 10.0  # noqa: B001
    assert stats["success_rate"] == 1.0  # noqa: B001

    # Test filtered stats
    iron_stats = survey_manager.get_extraction_stats("IRON_ORE")
    assert iron_stats["average_yield"] == 10.0  # noqa: B001
    assert iron_stats["success_rate"] == 1.0  # noqa: B001

    # Test non-existent resource
    gold_stats = survey_manager.get_extraction_stats("GOLD_ORE")
    assert gold_stats["average_yield"] == 0.0  # noqa: B001
    assert gold_stats["success_rate"] == 0.0  # noqa: B001


@pytest.mark.asyncio
async def test_survey_manager_create_survey(survey_manager, mock_survey):
    """Test survey creation API interaction"""
    response = Response(
        status_code=201,
        content=b"",
        headers={},
        parsed=type(
            "ParsedResponse",
            (),
            {"data": type("Data", (), {"surveys": [mock_survey]})}
        )
    )

    with patch(
        "game.mining.create_survey.asyncio_detailed",
        AsyncMock(return_value=response)
    ):
        survey = await survey_manager.create_survey("TEST-SHIP")
        assert survey == mock_survey
        assert mock_survey.signature in survey_manager.active_surveys


@pytest.mark.asyncio
async def test_survey_manager_extract_resources(
    survey_manager,
    mock_survey,
    mock_extraction
):
    """Test resource extraction API interaction"""
    with patch(
        "game.mining.extract_resources.asyncio_detailed"
    ) as mock_extract:
        # Set up the mock response
        mock_data = type('Data', (), {'extraction': mock_extraction})
        mock_parsed = type('ParsedResponse', (), {'data': mock_data})
        mock_response = Response(
            status_code=201,
            content=b"",
            headers={},
            parsed=mock_parsed
        )
        mock_extract.return_value = mock_response
        # Call the method
        result = await survey_manager.extract_resources_with_survey(
            "TEST-SHIP",
            mock_survey
        )

        # Verify the API call was made correctly
        mock_extract.assert_called_once_with(
            ship_symbol="TEST-SHIP",
            client=None,
            json_body={"survey": mock_survey.to_dict()}
        )

        # Verify the result
        assert result is not None
        assert result.ship_symbol == mock_extraction.ship_symbol
        assert result.yield_.symbol == mock_extraction.yield_.symbol
        assert result.yield_.units == mock_extraction.yield_.units
        assert len(survey_manager.extraction_history) == 1
