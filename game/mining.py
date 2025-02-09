"""
Mining operations and survey management system
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from space_traders_api_client.models.survey import Survey
from space_traders_api_client.models.extraction import Extraction
from space_traders_api_client.api.fleet import create_survey, extract_resources
from space_traders_api_client.models.extract_resources_body import ExtractResourcesBody

from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Tracks the result of an extraction operation"""
    survey_signature: str
    extraction: Extraction
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MiningTarget:
    """Represents a prioritized mining target"""
    waypoint: str
    resource_type: str
    priority: int
    survey: Optional[Survey] = None


class SurveyManager:
    """Manages survey operations and tracking"""

    def __init__(self, client):
        """Initialize the survey manager

        Args:
            client: The authenticated SpaceTraders client
        """
        self.client = client
        self.active_surveys: Dict[str, Survey] = {}  # signature -> Survey
        self.extraction_history: List[ExtractionResult] = []
        self.rate_limiter = RateLimiter()

    def add_survey(self, survey: Survey) -> None:
        """Add a new survey to tracking

        Args:
            survey: The survey to track
        """
        # Convert expiration to a naive datetime for comparison
        expiration = survey.expiration.replace(tzinfo=None)
        if datetime.now() < expiration:
            self.active_surveys[survey.signature] = survey
            logger.info(
                f"Added survey {survey.signature} at {survey.symbol} "
                f"(expires: {survey.expiration})"
            )

    def get_active_surveys(self) -> List[Survey]:
        """Get all currently active surveys

        Returns:
            List of active surveys
        """
        self.cleanup_expired_surveys()
        return list(self.active_surveys.values())

    def get_survey_by_signature(self, signature: str) -> Optional[Survey]:
        """Get a specific survey by signature

        Args:
            signature: The survey signature to look up

        Returns:
            The survey if found and active, None otherwise
        """
        self.cleanup_expired_surveys()
        return self.active_surveys.get(signature)

    def get_surveys_for_waypoint(self, waypoint: str) -> List[Survey]:
        """Get all active surveys for a specific waypoint

        Args:
            waypoint: The waypoint symbol to filter by

        Returns:
            List of active surveys at the waypoint
        """
        self.cleanup_expired_surveys()
        return [
            survey for survey in self.active_surveys.values()
            if survey.symbol == waypoint
        ]

    def get_best_survey(self, resource_type: str) -> Optional[Survey]:
        """Get the best active survey for a specific resource

        Args:
            resource_type: The type of resource to look for

        Returns:
            The best matching survey, or None if no matches
        """
        self.cleanup_expired_surveys()

        matching_surveys = []
        for survey in self.active_surveys.values():
            # Count matching deposits
            matching_deposits = sum(
                1 for deposit in survey.deposits
                if deposit.symbol == resource_type
            )
            if matching_deposits > 0:
                matching_surveys.append((matching_deposits, survey))

        if not matching_surveys:
            return None

        # Return survey with most matching deposits
        best_survey = max(matching_surveys, key=lambda x: x[0])[1]
        logger.info(
            f"Found best survey for {resource_type} at {best_survey.symbol} "
            f"(signature: {best_survey.signature})"
        )
        return best_survey

    def track_extraction_result(
        self,
        survey: Survey,
        extraction: Extraction
    ) -> None:
        """Record the result of an extraction operation

        Args:
            survey: The survey used for extraction
            extraction: The extraction result
        """
        result = ExtractionResult(
            survey_signature=survey.signature,
            extraction=extraction
        )
        self.extraction_history.append(result)
        logger.info(
            f"Recorded extraction result: {extraction.yield_.units} units of "
            f"{extraction.yield_.symbol} using survey {survey.signature}"
        )

    def cleanup_expired_surveys(self) -> None:
        """Remove expired surveys from tracking"""
        now = datetime.now()
        expired = [
            sig for sig, survey in self.active_surveys.items()
            if now >= survey.expiration.replace(tzinfo=None)
        ]
        for sig in expired:
            logger.info(f"Removing expired survey {sig}")
            del self.active_surveys[sig]

    def get_extraction_stats(
        self,
        resource_type: Optional[str] = None
    ) -> Dict[str, float]:
        """Get statistics about extraction operations

        Args:
            resource_type: Optional resource type to filter by

        Returns:
            Dictionary of statistics including:
            - average_yield: Average units per extraction
            - success_rate: Percentage of successful extractions
        """
        if not self.extraction_history:
            return {
                "average_yield": 0.0,
                "success_rate": 0.0
            }

        relevant_extractions = self.extraction_history
        if resource_type:
            relevant_extractions = [
                result for result in self.extraction_history
                if result.extraction.yield_.symbol == resource_type
            ]

        if not relevant_extractions:
            return {
                "average_yield": 0.0,
                "success_rate": 0.0
            }

        total_yield = sum(
            result.extraction.yield_.units
            for result in relevant_extractions
        )
        success_count = len([
            result for result in relevant_extractions
            if result.extraction.yield_.units > 0
        ])

        stats = {
            "average_yield": total_yield / len(relevant_extractions),
            "success_rate": success_count / len(relevant_extractions)
        }

        logger.info(
            f"Extraction stats for {resource_type if resource_type else 'all resources'}: "
            f"avg yield = {stats['average_yield']:.1f}, "
            f"success rate = {stats['success_rate']*100:.1f}%"
        )
        return stats

    async def create_survey(self, ship_symbol: str) -> Optional[Survey]:
        """Create a new survey using the specified ship

        Args:
            ship_symbol: Symbol of the ship to use for survey

        Returns:
            The created survey if successful, None otherwise
        """
        response = await self.rate_limiter.execute_with_retry(
            create_survey.asyncio_detailed,
            task_name="create_survey",
            ship_symbol=ship_symbol,
            client=self.client
        )

        if response.status_code == 201 and response.parsed:
            # Add all surveys from the response
            surveys = response.parsed.data.surveys
            for survey in surveys:
                self.add_survey(survey)
            # Return the first survey if available
            if response.parsed.data.surveys:
                survey = response.parsed.data.surveys[0]
                logger.info(
                    f"Created new survey at {survey.symbol} "
                    f"(signature: {survey.signature})"
                )
                return survey
            return None
        else:
            logger.error(f"Failed to create survey: {response.status_code}")
            if response.content:
                logger.error(f"Response: {response.content.decode()}")
            return None

    async def extract_resources_with_survey(
        self,
        ship_symbol: str,
        survey: Survey
    ) -> Optional[Extraction]:
        """Perform resource extraction using a survey

        Args:
            ship_symbol: Symbol of the ship to use for extraction
            survey: Survey to use for extraction

        Returns:
            The extraction result if successful, None otherwise
        """
        response = await self.rate_limiter.execute_with_retry(
            extract_resources.asyncio_detailed,
            task_name="extract_resources",
            ship_symbol=ship_symbol,
            client=self.client,
            json_body={"survey": survey.to_dict()}
        )

        if response.status_code == 201 and response.parsed:
            extraction = response.parsed.data.extraction
            self.track_extraction_result(survey, extraction)
            logger.info(
                f"Successfully extracted {extraction.yield_.units} units of "
                f"{extraction.yield_.symbol} using survey {survey.signature}"
            )
            return extraction
        else:
            logger.error(f"Failed to extract resources: {response.status_code}")
            if response.content:
                logger.error(f"Response: {response.content.decode()}")
            return None
