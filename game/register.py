from typing import Optional, Union as TypingUnion
from space_traders_api_client.models.faction_symbol import FactionSymbol
from space_traders_api_client.models.register_body import RegisterBody
from space_traders_api_client.client import Client
from space_traders_api_client.api.default import register
from space_traders_api_client.types import UNSET, Unset
import json
import os
import random
import string


def generate_agent_symbol(prefix: str = "JOSHU") -> str:
    """Generate a random agent symbol with the given prefix."""
    # Generate 4 random uppercase letters
    suffix = ''.join(random.choices(string.ascii_uppercase, k=4))
    return f"{prefix}-{suffix}"


DEFAULT_API_URL = "https://api.spacetraders.io/v2"


class RegistrationManager:
    def __init__(self, api_url: str = DEFAULT_API_URL):
        self.api_url = api_url
        self.client = Client(base_url=api_url)
        # Use absolute path for token file in project root
        self.token_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "token.json"
        )

    def load_existing_token(self) -> Optional[str]:
        """Load existing token from file if it exists."""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    return data.get('token')
            except Exception:
                return None
        return None

    def save_token(self, token: str):
        """Save token to file for future use."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
        with open(self.token_file, 'w') as f:
            json.dump({'token': token}, f)

    def register_agent(
        self,
        symbol: str,
        faction: FactionSymbol = FactionSymbol.COSMIC,
        email: Optional[str] = None
    ) -> bool:
        """
        Register a new agent with SpaceTraders API.

        Args:
            symbol: Desired agent symbol (callsign)
            faction: Faction to join (default: COSMIC)
            email: Optional email for reserved callsigns

        Returns:
            bool: True if registration was successful, False if token already
            exists
        """
        # Check for existing token first
        existing_token = self.load_existing_token()
        if existing_token:
            return False

        # Create registration body with proper email handling
        email_param: TypingUnion[Unset, str] = (
            UNSET if email is None else email
        )
        register_body = RegisterBody(
            symbol=symbol,
            faction=faction,
            email=email_param
        )

        # Register new agent
        response = register.sync_detailed(
            client=self.client,
            body=register_body
        )

        try:
            error_content = response.content.decode('utf-8')
        except UnicodeDecodeError:
            error_content = str(response.content)

        if response.status_code != 201:
            raise Exception(f"Failed to register agent: {error_content}")

        # Parse response and extract token
        if not response.parsed:
            raise Exception("Invalid response format: no parsed data")

        data = response.parsed.data
        if not data:
            raise Exception("Invalid response format: no data field")

        token = data.token
        if not token:
            raise Exception("Invalid response format: no token field")

        # Save token for future use
        self.save_token(token)

        return True

    def generate_agent_symbol(self) -> str:
        """
        Generate a valid agent symbol for SpaceTraders API.
        Creates a random space-themed prefix followed by random characters.
        Must be 3-14 characters, using only A-Z, 0-9, and _ (underscore).

        Returns:
            A valid agent symbol string
        """
        # Space-themed prefix options
        prefix_options = [
            "NOVA", "STAR", "VOID", "NEBULA", "SOLAR", "LUNAR", "COSMIC",
            "ASTRO", "ORBIT", "COMET", "METEOR", "SPACE", "GALAXY", "QUASAR"
        ]

        # Pick a random prefix
        prefix = random.choice(prefix_options)

        # Calculate remaining length for random chars
        remaining_length = 14 - len(prefix) - 1

        # Generate random string of valid characters
        valid_chars = string.ascii_uppercase + string.digits
        random_part = ''.join(
            random.choices(valid_chars, k=min(4, remaining_length))
        )

        # Combine with underscore
        return f"{prefix}_{random_part}"
