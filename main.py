#!/usr/bin/env python3
"""
SpaceTraders Game Client Entry Point
"""
import os
import json
import asyncio
from game.trader import SpaceTrader
from game.register import RegistrationManager, generate_agent_symbol
from space_traders_api_client.models.faction_symbol import FactionSymbol

async def main():
    """Main entry point for the SpaceTraders game client"""
    registration_manager = RegistrationManager()

    # Try to load existing token
    token = registration_manager.load_existing_token()

    if not token:
        print("No token found in token.json. Registering new agent...")
        try:
            # Generate a random valid agent symbol
            agent_symbol = generate_agent_symbol()
            print(f"Registering new agent with symbol: {agent_symbol}")

            # Register new agent
            success = registration_manager.register_agent(
                symbol=agent_symbol,
                faction=FactionSymbol("COSMIC")  # Starting faction
            )
            if success:
                token = registration_manager.load_existing_token()
                print("Successfully registered new agent!")
            else:
                print("Agent already registered!")
        except Exception as e:
            print(f"Failed to register new agent: {e}")
            return

    # Initialize trader
    trader = SpaceTrader(token)

    try:
        # Initialize game state
        print("Initializing game state...")
        await trader.initialize()

        if trader.agent:
            print("\nAgent Status:")
            print(f"Symbol: {trader.agent.symbol}")
            print(f"Credits: {trader.agent.credits_}")
            print(f"Headquarters: {trader.agent.headquarters}")
            print(f"Starting Faction: {trader.agent.starting_faction}")
            print(f"Ship Count: {trader.agent.ship_count}")

        if trader.ships:
            print("\nShips:")
            for symbol, ship in trader.ships.items():
                print(f"- {symbol} at {ship.nav.waypoint_symbol}")

        # Scan nearby systems
        print("\nScanning nearby systems...")
        systems = await trader.scan_systems(limit=5)
        print(f"Found {len(systems)} nearby systems:")
        for system in systems:
            print(f"- {system.symbol}: {system.type_}")

        # Start fleet management
        print("\nStarting fleet management...")
        await trader.manage_fleet()

    except Exception as e:
        print(f"Error during game operations: {e}")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
