"""Factories for creating test fixtures using factory_boy."""
from typing import List, Optional
import factory
from factory import (
    Sequence,
    LazyAttribute,
    SubFactory,
    List as FactoryList,
    LazyFunction,
)
from datetime import datetime, timezone
from space_traders_api_client.types import UNSET
from space_traders_api_client.models import (
    Ship,
    ShipCargo,
    ShipCargoItem,
    ShipCrew,
    ShipCrewRotation,
    ShipRegistration,
    ShipRole,
    FactionSymbol,
    ShipFrame,
    ShipFrameSymbol,
    ShipReactor,
    ShipReactorSymbol,
    ShipEngine,
    ShipEngineSymbol,
    ShipNav,
    ShipNavRoute,
    ShipNavStatus,
    ShipNavFlightMode,
    ShipRequirements,
    Waypoint,
    WaypointType,
    Agent,
    Contract,
    ContractTerms,
    ContractPayment,
    ContractDeliverGood,
    ContractType,
    System,
    SystemType,
    SystemFaction,
    SystemWaypoint,
    ShipFuelConsumed,
    Faction,
    Cooldown,
    ShipFuel,
    FactionTrait,
    FactionTraitSymbol,
    WaypointOrbital,
    WaypointTrait,
    WaypointTraitSymbol,
    ShipModule,
    ShipModuleSymbol,
    ShipMount,
    ShipMountSymbol,
    ShipNavRouteWaypoint,
    Meta,
)


class MetaFactory(factory.Factory):
    """Factory for pagination metadata"""
    class Meta:
        model = Meta

    total = 0
    page = 1
    limit = 10


class WaypointRouteFactory(factory.Factory):
    """Factory for waypoint route information"""
    class Meta:
        model = ShipNavRouteWaypoint

    symbol = factory.Sequence(lambda n: f"TEST-WAYPOINT-{n}")
    type_ = WaypointType.PLANET
    system_symbol = factory.Sequence(lambda n: f"TEST-SYSTEM-{n}")
    x = factory.Sequence(lambda n: n * 10)
    y = factory.Sequence(lambda n: n * 10)


class AgentFactory(factory.Factory):
    """Factory for agent data"""
    class Meta:
        model = Agent

    account_id = factory.Sequence(lambda n: f"test_account_{n}")
    symbol = factory.Sequence(lambda n: f"TEST_AGENT_{n}")
    headquarters = factory.Sequence(lambda n: f"TEST-HQ-{n}")
    credits_ = 100000
    starting_faction = FactionSymbol.COSMIC
    ship_count = 2


class FactionTraitFactory(factory.Factory):
    """Factory for faction traits"""
    class Meta:
        model = FactionTrait

    symbol = FactionTraitSymbol.BUREAUCRATIC
    name = "Bureaucratic"
    description = "A trait description"


class FactionFactory(factory.Factory):
    """Factory for faction data"""
    class Meta:
        model = Faction

    symbol = FactionSymbol.COSMIC
    name = "Cosmic Corporation"
    description = "A test faction"
    headquarters = factory.Sequence(lambda n: f"TEST-HQ-{n}")
    traits = factory.List([factory.SubFactory(FactionTraitFactory)])
    is_recruiting = True


class ContractFactory(factory.Factory):
    """Factory for contract data"""
    class Meta:
        model = Contract

    id = factory.Sequence(lambda n: f"test-contract-{n}")
    faction_symbol = FactionSymbol.COSMIC
    type_ = ContractType.PROCUREMENT
    terms = factory.LazyAttribute(lambda _: ContractTerms(
        deadline=datetime.now(timezone.utc),
        payment=ContractPayment(on_accepted=10000, on_fulfilled=50000),
        deliver=[
            ContractDeliverGood(
                trade_symbol="IRON_ORE",
                destination_symbol="TEST-DEST",
                units_required=100,
                units_fulfilled=0
            )
        ]
    ))
    accepted = False
    fulfilled = False
    expiration = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    deadline_to_accept = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class WaypointTraitFactory(factory.Factory):
    """Factory for waypoint traits"""
    class Meta:
        model = WaypointTrait

    symbol = WaypointTraitSymbol.MARKETPLACE
    name = "Marketplace"
    description = "A bustling marketplace"


class WaypointFactory(factory.Factory):
    """Factory for waypoint data"""
    class Meta:
        model = Waypoint

    symbol = factory.Sequence(lambda n: f"TEST-WAYPOINT-{n}")
    type_ = WaypointType.PLANET
    system_symbol = factory.Sequence(lambda n: f"TEST-SYSTEM-{n}")
    x = factory.Sequence(lambda n: n * 10)
    y = factory.Sequence(lambda n: n * 10)
    orbitals = factory.List([])
    traits = factory.List([factory.SubFactory(WaypointTraitFactory)])
    is_under_construction = False
    chart = UNSET


class SystemWaypointFactory(factory.Factory):
    """Factory for system waypoint data"""
    class Meta:
        model = SystemWaypoint

    symbol = factory.Sequence(lambda n: f"TEST-WAYPOINT-{n}")
    type_ = WaypointType.PLANET
    x = factory.Sequence(lambda n: n * 10)
    y = factory.Sequence(lambda n: n * 10)
    orbitals = factory.List([])  # Required list of orbital objects


class SystemFactionFactory(factory.Factory):
    """Factory for system faction data"""
    class Meta:
        model = SystemFaction

    symbol = FactionSymbol.COSMIC


class SystemFactory(factory.Factory):
    """Factory for system data"""
    class Meta:
        model = System

    symbol = factory.Sequence(lambda n: f"TEST-SYSTEM-{n}")
    sector_symbol = factory.Sequence(lambda n: f"TEST-SECTOR-{n}")
    type_ = SystemType.NEUTRON_STAR
    x = factory.Sequence(lambda n: n * 100)
    y = factory.Sequence(lambda n: n * 100)
    waypoints = factory.List([factory.SubFactory(SystemWaypointFactory)])
    factions = factory.List([factory.SubFactory(SystemFactionFactory)])


class ShipFrameFactory(factory.Factory):
    """Factory for ship frame data"""
    class Meta:
        model = ShipFrame

    symbol = ShipFrameSymbol.FRAME_MINER
    name = "Mining Frame"
    description = "A basic frame for mining operations"
    module_slots = 3
    mounting_points = 3
    fuel_capacity = 1000
    requirements = factory.LazyAttribute(
        lambda _: ShipRequirements(power=1, crew=1)
    )
    condition = 100
    integrity = 1.0


class ShipReactorFactory(factory.Factory):
    """Factory for ship reactor data"""
    class Meta:
        model = ShipReactor

    symbol = ShipReactorSymbol.REACTOR_SOLAR_I
    name = "Solar Reactor I"
    description = "A basic solar reactor"
    power_output = 10
    requirements = factory.LazyAttribute(
        lambda _: ShipRequirements(power=0, crew=0)
    )
    condition = 100
    integrity = 1.0


class ShipEngineFactory(factory.Factory):
    """Factory for ship engine data"""
    class Meta:
        model = ShipEngine

    symbol = ShipEngineSymbol.ENGINE_IMPULSE_DRIVE_I
    name = "Impulse Drive I"
    description = "A basic impulse drive"
    speed = 2
    requirements = factory.LazyAttribute(
        lambda _: ShipRequirements(power=1, crew=0)
    )
    condition = 100
    integrity = 1.0


class ShipModuleFactory(factory.Factory):
    """Factory for ship module data"""
    class Meta:
        model = ShipModule

    symbol = ShipModuleSymbol.MODULE_CARGO_HOLD_I
    name = "Cargo Hold I"
    description = "A basic cargo hold"
    requirements = factory.LazyAttribute(
        lambda _: ShipRequirements(power=1, crew=0)
    )


class ShipMountFactory(factory.Factory):
    """Factory for ship mount data"""
    class Meta:
        model = ShipMount

    symbol = ShipMountSymbol.MOUNT_MINING_LASER_I
    name = "Mining Laser I"
    description = "A basic mining laser"
    requirements = factory.LazyAttribute(
        lambda _: ShipRequirements(power=1, crew=0)
    )


class ShipNavFactory(factory.Factory):
    """Factory for ship navigation data"""
    class Meta:
        model = ShipNav

    system_symbol = factory.Sequence(lambda n: f"TEST-SYSTEM-{n}")
    waypoint_symbol = factory.Sequence(lambda n: f"TEST-WAYPOINT-{n}")
    route = factory.LazyAttribute(lambda _: ShipNavRoute(
        destination=WaypointRouteFactory(),
        origin=WaypointRouteFactory(),
        departure_time=datetime.now(timezone.utc),
        arrival=datetime.now(timezone.utc)
    ))
    status = ShipNavStatus.DOCKED
    flight_mode = ShipNavFlightMode.CRUISE


class ShipRegistrationFactory(factory.Factory):
    """Factory for ship registration data"""
    class Meta:
        model = ShipRegistration

    name = factory.Sequence(lambda n: f"Test Ship {n}")
    role = ShipRole.COMMAND
    faction_symbol = FactionSymbol.COSMIC


class ShipCargoItemFactory(factory.Factory):
    """Factory for ship cargo item data"""
    class Meta:
        model = ShipCargoItem

    symbol = "IRON_ORE"
    units = 10
    name = "Iron Ore"
    description = "Unrefined iron ore"


class ShipFactory(factory.Factory):
    """Factory for ship data"""
    class Meta:
        model = Ship

    symbol = factory.Sequence(lambda n: f"TEST-SHIP-{n}")
    registration = factory.SubFactory(ShipRegistrationFactory)
    nav = factory.SubFactory(ShipNavFactory)
    crew = factory.LazyAttribute(lambda _: ShipCrew(
        current=1,
        required=1,
        capacity=2,
        rotation=ShipCrewRotation.STRICT,
        wages=100,
        morale=100
    ))
    frame = factory.SubFactory(ShipFrameFactory)
    reactor = factory.SubFactory(ShipReactorFactory)
    engine = factory.SubFactory(ShipEngineFactory)
    modules = factory.List([factory.SubFactory(ShipModuleFactory)])
    mounts = factory.List([factory.SubFactory(ShipMountFactory)])
    cargo = factory.LazyAttribute(lambda _: ShipCargo(
        capacity=100,
        units=0,
        inventory=[]
    ))
    fuel = factory.LazyAttribute(lambda _: ShipFuel(
        current=1000,
        capacity=1000,
        consumed=ShipFuelConsumed(
            amount=0,
            timestamp=datetime.now(timezone.utc)
        )
    ))
    cooldown = factory.LazyAttribute(lambda obj: Cooldown(
        ship_symbol=obj.symbol,
        total_seconds=0,
        remaining_seconds=0,
        expiration=UNSET
    ))
