import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

# Imports for SystemManager and WaypointType
from space_traders_api_client.models.survey import Survey
from space_traders_api_client.models.extraction import Extraction
from space_traders_api_client.api.fleet import create_survey, extract_resources
# Removed: from space_traders_api_client.models.extract_resources_body import ExtractResourcesBody # Not used directly in this file after changes
from space_traders_api_client.models.waypoint_type import WaypointType # Added
from space_traders_api_client.models.ship import Ship # Added
from space_traders_api_client.models.waypoint import Waypoint # Added

from .rate_limiter import RateLimiter
from .system_manager import SystemManager # Added

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Tracks the result of an extraction operation"""
    survey_signature: str
    extraction: Extraction
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MiningTarget:
    """Represents a prioritized mining target, now dynamically found."""
    waypoint_symbol: str # Changed from 'waypoint' to 'waypoint_symbol' for clarity
    resource_type: str # The specific resource to mine (e.g., 'IRON_ORE')
    priority: int
    # Survey is optional because we might not have one when initially identifying the target
    survey: Optional[Survey] = None
    # Waypoint object itself can be stored if needed, but symbol is key
    waypoint_obj: Optional[Waypoint] = None


class MiningManager: # Renamed from SurveyManager to MiningManager for broader scope
    """Manages mining operations, including finding sites and survey management."""
    
    def __init__(self, client, system_manager: SystemManager): # Added system_manager
        """Initialize the mining manager
        
        Args:
            client: The authenticated SpaceTraders client
            system_manager: The manager for system and waypoint data
        """
        self.client = client
        self.system_manager = system_manager # Store SystemManager instance
        self.active_surveys: Dict[str, Survey] = {}  # signature -> Survey
        self.extraction_history: List[ExtractionResult] = []
        self.rate_limiter = RateLimiter()
        
    def add_survey(self, survey: Survey) -> None:
        """Add a new survey to tracking"""
        expiration = survey.expiration.replace(tzinfo=None)
        if datetime.now() < expiration:
            self.active_surveys[survey.signature] = survey
            logger.info(
                f"Added survey {survey.signature} at {survey.symbol} "
                f"(expires: {survey.expiration})"
            )
            
    def get_active_surveys(self) -> List[Survey]:
        """Get all currently active surveys"""
        self.cleanup_expired_surveys()
        return list(self.active_surveys.values())
        
    def get_survey_by_signature(self, signature: str) -> Optional[Survey]:
        """Get a specific survey by signature"""
        self.cleanup_expired_surveys()
        return self.active_surveys.get(signature)
        
    def get_surveys_for_waypoint(self, waypoint_symbol: str) -> List[Survey]: # Changed waypoint to waypoint_symbol
        """Get all active surveys for a specific waypoint"""
        self.cleanup_expired_surveys()
        return [
            survey for survey in self.active_surveys.values()
            if survey.symbol == waypoint_symbol
        ]
        
    def get_best_survey_for_resource_at_waypoint(self, resource_type: str, waypoint_symbol: str) -> Optional[Survey]:
        """Get the best active survey for a specific resource at a given waypoint."""
        self.cleanup_expired_surveys()
        
        matching_surveys = []
        for survey in self.get_surveys_for_waypoint(waypoint_symbol):
            matching_deposits = sum(
                1 for deposit in survey.deposits
                if deposit.symbol == resource_type
            )
            if matching_deposits > 0:
                # Consider survey size or other factors for "best"
                # For now, prioritizing surveys with more deposits of the target resource
                priority = matching_deposits
                # Could also factor in survey expiration or deposit size if available
                # Example: survey.size could be 'SMALL', 'MODERATE', 'LARGE'
                # size_priority = {'SMALL': 1, 'MODERATE': 2, 'LARGE': 3}.get(survey.size, 0)
                # priority = (matching_deposits, size_priority)
                matching_surveys.append((priority, survey))
                
        if not matching_surveys:
            return None
            
        best_survey = max(matching_surveys, key=lambda x: x[0])[1] # Max by priority (matching_deposits)
        logger.info(
            f"Found best survey for {resource_type} at {best_survey.symbol} "
            f"(signature: {best_survey.signature})"
        )
        return best_survey

    def find_mining_targets(self, desired_resources: List[str], priority_map: Dict[str, int], ship_location_system: Optional[str] = None) -> List[MiningTarget]:
        """
        Finds potential mining targets (asteroid fields or other relevant waypoints)
        based on desired resources.
        Args:
            desired_resources: A list of resource symbols (e.g., ['IRON_ORE', 'ALUMINUM_ORE']).
            priority_map: A dictionary mapping resource symbols to priority (higher is better).
            ship_location_system: Optional. The current system of the ship to prioritize nearby targets.
        Returns:
            A list of MiningTarget objects, sorted by priority.
        """
        potential_targets: List[MiningTarget] = []

        # Find asteroid fields first, as they are common mining spots
        asteroid_fields = self.system_manager.find_waypoints_by_type(WaypointType.ASTEROID_FIELD)
        # Could also search for other types like ASTEROID, ENGINEERED_ASTEROID if relevant

        logger.info(f"Found {len(asteroid_fields)} asteroid field waypoints for potential mining.")

        for waypoint in asteroid_fields:
            # In a more advanced scenario, check waypoint traits for specific resources
            # For now, we assume asteroid fields *might* have the desired resources
            # and rely on surveys later to confirm.
            for resource_type in desired_resources:
                # Check if this waypoint is known to have the resource (e.g. from previous surveys or market data)
                # This is a placeholder for more intelligent resource discovery at a waypoint
                # For now, any asteroid field is a potential target for any desired ore.

                # Prioritize targets in the ship's current system
                system_priority_bonus = 0
                if ship_location_system and waypoint.system_symbol == ship_location_system:
                    system_priority_bonus = 100 # Arbitrary bonus for being in the same system

                target = MiningTarget(
                    waypoint_symbol=waypoint.symbol,
                    resource_type=resource_type,
                    priority=priority_map.get(resource_type, 1) + system_priority_bonus,
                    waypoint_obj=waypoint
                )
                potential_targets.append(target)
                logger.debug(f"Identified potential mining target: {target.waypoint_symbol} for {target.resource_type} (Priority: {target.priority})")

        # Sort targets by priority (higher first)
        potential_targets.sort(key=lambda t: t.priority, reverse=True)
        
        if not potential_targets:
            logger.warning(f"No mining targets found for desired resources: {desired_resources}")
        else:
            logger.info(f"Found {len(potential_targets)} potential mining targets. Top target: {potential_targets[0].waypoint_symbol} for {potential_targets[0].resource_type}")

        return potential_targets

    def track_extraction_result(
        self,
        survey: Optional[Survey], # Survey can be None if not using a survey
        extraction: Extraction,
        waypoint_symbol: str # Added waypoint_symbol for context
    ) -> None:
        """Record the result of an extraction operation"""
        survey_sig = survey.signature if survey else "None"
        result = ExtractionResult(
            survey_signature=survey_sig,
            extraction=extraction
        )
        self.extraction_history.append(result)
        logger.info(
            f"Recorded extraction at {waypoint_symbol}: {extraction.yield_.units} units of "
            f"{extraction.yield_.symbol} (Survey: {survey_sig})"
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
            
    # get_extraction_stats remains largely the same, ensure it handles cases where survey might be None if used.

    async def create_survey(self, ship_symbol: str, current_waypoint_symbol: str) -> Optional[Survey]: # Added current_waypoint_symbol for logging
        """Create a new survey using the specified ship at its current location."""
        # Ensure ship is at a surveyable location (e.g., asteroid field)
        # This check might be better placed in the calling logic (e.g., in SpaceTrader)
        # waypoint = self.system_manager.get_waypoint(current_waypoint_symbol) # Assumes get_waypoint exists
        # if not waypoint or waypoint.type not in [WaypointType.ASTEROID_FIELD, WaypointType.ASTEROID]:
        #     logger.warning(f"Ship {ship_symbol} at {current_waypoint_symbol} is not a surveyable location.")
        #     return None

        logger.info(f"Attempting to create survey with ship {ship_symbol} at {current_waypoint_symbol}.")
        response = await self.rate_limiter.execute_with_retry(
            create_survey.asyncio_detailed,
            task_name=f"create_survey_{ship_symbol}",
            ship_symbol=ship_symbol,
            client=self.client
        )
        
        if response.status_code == 201 and response.parsed:
            surveys = response.parsed.data.surveys
            if surveys:
                for survey_item in surveys: # The API returns a list of surveys
                    self.add_survey(survey_item) # Add all created surveys
                first_survey = surveys[0]
                logger.info(
                    f"Ship {ship_symbol} created new survey at {first_survey.symbol} "
                    f"(Signature: {first_survey.signature}, Expires: {first_survey.expiration}). "
                    f"{len(surveys)} surveys created in total."
                )
                return first_survey # Return the first one as representative
            else:
                logger.warning(f"Survey creation call succeeded for {ship_symbol} but no surveys returned.")
                return None
        elif response.status_code == 400 and response.content: # Specific error for cooldown or existing survey
             error_data = response.parsed
             if error_data and hasattr(error_data, 'error') and hasattr(error_data.error, 'data'):
                 cooldown_data = error_data.error.data.get('cooldown')
                 if cooldown_data:
                     logger.warning(f"Cannot create survey with {ship_symbol}: Cooldown active. Remaining: {cooldown_data.get('remainingSeconds')}s")
                     # Store cooldown info if needed by ship logic
                     return None # Or raise a specific CooldownException
                 # Handle other 400 errors if necessary
                 logger.error(f"Failed to create survey with {ship_symbol} (400): {error_data.error.message}")
             else:
                logger.error(f"Failed to create survey with {ship_symbol}: {response.status_code}. Response: {response.content.decode()}")
        else:
            logger.error(f"Failed to create survey with {ship_symbol}: {response.status_code}")
            if response.content:
                logger.error(f"Response: {response.content.decode()}")
            return None

    async def extract_resources_at_waypoint( # Renamed from extract_resources_with_survey
        self,
        ship: Ship, # Pass the whole ship object
        survey: Optional[Survey] = None # Survey is now optional
    ) -> Optional[Extraction]:
        """
        Perform resource extraction at the ship's current waypoint.
        Uses a survey if provided and valid.
        """
        current_waypoint_symbol = ship.nav.waypoint_symbol
        logger.info(f"Ship {ship.symbol} attempting extraction at {current_waypoint_symbol}...")

        json_body = {}
        if survey:
            # Validate survey: check expiration and if it's for the current waypoint
            if datetime.now() >= survey.expiration.replace(tzinfo=None):
                logger.warning(f"Survey {survey.signature} for {ship.symbol} has expired. Removing.")
                if survey.signature in self.active_surveys:
                    del self.active_surveys[survey.signature]
                survey = None # Do not use expired survey
            elif survey.symbol != current_waypoint_symbol:
                logger.warning(f"Survey {survey.signature} is for waypoint {survey.symbol}, but ship {ship.symbol} is at {current_waypoint_symbol}. Cannot use this survey here.")
                survey = None # Do not use survey for wrong location
            else:
                logger.info(f"Using survey {survey.signature} for extraction by {ship.symbol}.")
                json_body = {"survey": survey.to_dict()}

        if not survey:
            logger.info(f"No valid survey provided or found for {ship.symbol} at {current_waypoint_symbol}. Performing regular extraction.")

        response = await self.rate_limiter.execute_with_retry(
            extract_resources.asyncio_detailed,
            task_name=f"extract_resources_{ship.symbol}",
            ship_symbol=ship.symbol,
            client=self.client,
            json_body=json_body if json_body else None # Pass None if no survey
        )
        
        if response.status_code == 201 and response.parsed:
            extraction = response.parsed.data.extraction
            self.track_extraction_result(survey, extraction, current_waypoint_symbol) # Pass survey (can be None)
            logger.info(
                f"Ship {ship.symbol} successfully extracted {extraction.yield_.units} units of "
                f"{extraction.yield_.symbol} at {current_waypoint_symbol}."
            )
            # Update ship cargo after extraction
            # The API response includes the updated cargo, so we can update our local ship model
            ship.cargo = response.parsed.data.cargo
            logger.info(f"Ship {ship.symbol} cargo updated: {ship.cargo.units}/{ship.cargo.capacity}")
            return extraction
        elif response.status_code == 400 and response.content: # Specific error for cooldown
             error_data = response.parsed
             if error_data and hasattr(error_data, 'error') and hasattr(error_data.error, 'data'):
                 cooldown_data = error_data.error.data.get('cooldown')
                 extraction_data = error_data.error.data.get('extraction') # Existing extraction in progress
                 cargo_data = error_data.error.data.get('cargo') # Cargo full

                 if cooldown_data:
                     logger.warning(f"Cannot extract with {ship.symbol}: Cooldown active. Remaining: {cooldown_data.get('remainingSeconds')}s. Ship cargo: {cooldown_data.get('cargoUnits')}/{cooldown_data.get('cargoCapacity')}")
                     # Update ship with cooldown data from response
                     # ship.cooldown = Cooldown(**cooldown_data) # Assuming Cooldown model is available
                     return None # Or raise CooldownException
                 elif extraction_data: #This case means an extraction is already in progress and hasn't yielded.
                      logger.warning(f"Extraction already in progress for ship {ship.symbol}. Yield: {extraction_data.get('yield').get('symbol')} ({extraction_data.get('yield').get('units')}). Cooldown: {error_data.error.data.get('cooldown').get('remainingSeconds')}s")
                      # This is not an error, but an ongoing state. The ship should wait.
                      # The response includes a cooldown object for the current extraction.
                      return None # Or a specific status indicating "waiting for current extraction"
                 elif cargo_data:
                     logger.warning(f"Cannot extract with {ship.symbol}: Cargo is full ({cargo_data.get('units')}/{cargo_data.get('capacity')}).")
                     ship.cargo = cargo_data # Update local cargo status
                     return None # Or raise CargoFullException


                 logger.error(f"Failed to extract resources with {ship.symbol} (400): {error_data.error.message}")
             else:
                logger.error(f"Failed to extract resources with {ship.symbol}: {response.status_code}. Response: {response.content.decode()}")

        else:
            logger.error(f"Failed to extract resources with {ship.symbol} at {current_waypoint_symbol}: {response.status_code}")
            if response.content:
                logger.error(f"Response: {response.content.decode()}")
            return None

    # get_extraction_stats can remain as is, or be enhanced to show stats per waypoint / resource type.
    def get_extraction_stats(
        self,
        resource_type: Optional[str] = None,
        waypoint_symbol: Optional[str] = None # Optional filter
    ) -> Dict[str, float]:
        """Get statistics about extraction operations"""
        if not self.extraction_history:
            return {"average_yield": 0.0, "success_rate": 0.0}

        relevant_extractions = self.extraction_history
        if resource_type:
            relevant_extractions = [
                result for result in relevant_extractions
                if result.extraction.yield_.symbol == resource_type
            ]
        # Add waypoint filter if needed, assuming ExtractionResult stores waypoint or can be inferred

        if not relevant_extractions:
            return {"average_yield": 0.0, "success_rate": 0.0}

        total_yield = sum(
            result.extraction.yield_.units
            for result in relevant_extractions
        )
        success_count = len([
            result for result in relevant_extractions
            if result.extraction.yield_.units > 0
        ])

        stats = {
            "average_yield": total_yield / len(relevant_extractions) if relevant_extractions else 0.0,
            "success_rate": success_count / len(relevant_extractions) if relevant_extractions else 0.0
        }

        filter_desc = f"for {resource_type}" if resource_type else "all resources"
        if waypoint_symbol: filter_desc += f" at {waypoint_symbol}"

        logger.info(
            f"Extraction stats {filter_desc}: "
            f"avg yield = {stats['average_yield']:.1f}, "
            f"success rate = {stats['success_rate']*100:.1f}% "
            f"({success_count}/{len(relevant_extractions)} extractions)"
        )
        return stats