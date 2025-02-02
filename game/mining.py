"""
Mining operations and survey management system
"""
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from space_traders_api_client.models.survey import Survey
from space_traders_api_client.models.extraction import Extraction
from space_traders_api_client.api.fleet import create_survey, extract_resources


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
        
    def add_survey(self, survey: Survey) -> None:
        """Add a new survey to tracking
        
        Args:
            survey: The survey to track
        """
        if datetime.now() < survey.expiration:
            self.active_surveys[survey.signature] = survey
            
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
        return max(matching_surveys, key=lambda x: x[0])[1]
        
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
        
    def cleanup_expired_surveys(self) -> None:
        """Remove expired surveys from tracking"""
        now = datetime.now()
        expired = [
            sig for sig, survey in self.active_surveys.items()
            if now >= survey.expiration
        ]
        for sig in expired:
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
        
        return {
            "average_yield": total_yield / len(relevant_extractions),
            "success_rate": success_count / len(relevant_extractions)
        }

    async def create_survey(self, ship_symbol: str) -> Optional[Survey]:
        """Create a new survey using the specified ship
        
        Args:
            ship_symbol: Symbol of the ship to use for survey
            
        Returns:
            The created survey if successful, None otherwise
        """
        try:
            response = await create_survey.asyncio_detailed(
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
                    return response.parsed.data.surveys[0]
                return None
            return None
        except Exception as e:
            print(f"Error creating survey: {e}")
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
        try:
            response = await extract_resources.asyncio_detailed(
                ship_symbol=ship_symbol,
                client=self.client,
                json_body={"survey": survey.to_dict()}
            )
            
            if response.status_code == 201 and response.parsed:
                extraction = response.parsed.data.extraction
                self.track_extraction_result(survey, extraction)
                return extraction
            return None
        except Exception as e:
            print(f"Error extracting resources: {e}")
            return None