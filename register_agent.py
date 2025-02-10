import argparse
from game.register import RegistrationManager
from space_traders_api_client.models.faction_symbol import FactionSymbol


def main():
    parser = argparse.ArgumentParser(description='Register a new SpaceTraders agent')
    parser.add_argument(
        '--symbol',
        type=str,
        required=True,
        help='Your desired agent symbol/callsign'
    )
    parser.add_argument(
        '--faction',
        type=str,
        default="COSMIC",
        help='Faction to join (default: COSMIC)'
    )
    parser.add_argument(
        '--email',
        type=str,
        help='Email for reserved callsigns (optional)'
    )

    args = parser.parse_args()

    try:
        manager = RegistrationManager()
        success = manager.register_agent(
            symbol=args.symbol,
            faction=FactionSymbol(args.faction.upper()),
            email=args.email
        )
        if success:
            print(f"Successfully registered agent {args.symbol}!")
            print("Use the token in token.json for future API calls")
        else:
            print("Agent already registered!")

    except Exception as e:
        print(f"Registration failed: {str(e)}")


if __name__ == "__main__":
    main()