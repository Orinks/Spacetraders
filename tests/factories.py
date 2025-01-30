"""Factories for creating test fixtures using factory_boy."""
import factory
from factory import Sequence, LazyAttribute, SubFactory, List, LazyFunction
from datetime import datetime, timezone
from space_traders_api_client.types import UNSET
from space_traders_api_client.models import (
    Ship,
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
    Agent,
    Contract,
    ContractTerms,
    ContractPayment,
    ContractDeliverGood,
    ContractType,
    System,
    SystemType,
    WaypointType,
    ShipFuelConsumed,
    Faction,
    Cooldown,
    ShipFuel,
    ShipCargo,
)


class AgentFactory(factory.Factory):
    class Meta:
        model = Agent

    account_id = "test_account"
    symbol = Sequence(lambda n: f"TEST_AGENT_{n}")
    headquarters = "test-system-XXX"
    credits_ = 100000
    starting_faction = "TEST_FACTION"
    ship_count = 2


class FactionFactory(factory.Factory):
    class Meta:
        model = Faction

    symbol = FactionSymbol("COSMIC")
    name = "Cosmic Corporation"
    description = "A test faction"
    headquarters = "test-system-XXX"
    traits = []
    is_recruiting = True


class ContractFactory(factory.Factory):
    class Meta:
        model = Contract

    id = Sequence(lambda n: f"test-contract-{n}")
    faction_symbol = "TEST_FACTION"
    type_ = ContractType.PROCUREMENT
    terms = LazyAttribute(lambda _: ContractTerms(
        deadline=datetime.now(timezone.utc),
        payment=ContractPayment(on_accepted=10000, on_fulfilled=50000),
        deliver=[ContractDeliverGood(
            trade_symbol="IRON_ORE",
            destination_symbol="test-system-XXX",
            units_required=100,
            units_fulfilled=0
        )]
    ))
    accepted = False
    fulfilled = False
    expiration = LazyFunction(lambda: datetime.now(timezone.utc))
    deadline_to_accept = LazyFunction(lambda: datetime.now(timezone.utc))


class WaypointFactory(factory.Factory):
    class Meta:
        model = Waypoint

    symbol = Sequence(lambda n: f"test-waypoint-{n}")
    type_ = WaypointType.PLANET  
    system_symbol = "test-system-XXX"
    x = Sequence(lambda n: n * 10)
    y = Sequence(lambda n: n * 10)
    orbitals = []
    traits = []
    is_under_construction = False
    chart = UNSET


class SystemFactory(factory.Factory):
    class Meta:
        model = System

    symbol = "test-system-XXX"
    sector_symbol = "test-sector"
    type_ = SystemType.NEUTRON_STAR  
    x = 0
    y = 0
    waypoints = List([
        SubFactory(WaypointFactory) for _ in range(3)
    ])
    factions = []


class ShipFrameFactory(factory.Factory):
    class Meta:
        model = ShipFrame

    symbol = ShipFrameSymbol.FRAME_MINER
    name = "Mining Frame"
    description = "A basic frame for mining operations"
    module_slots = 3
    mounting_points = 3
    fuel_capacity = 1000
    requirements = LazyAttribute(lambda _: ShipRequirements(power=1, crew=1))
    condition = 100
    integrity = 1.0


class ShipReactorFactory(factory.Factory):
    class Meta:
        model = ShipReactor

    symbol = ShipReactorSymbol.REACTOR_SOLAR_I
    name = "Solar Reactor I"
    description = "A basic solar reactor"
    power_output = 10
    requirements = LazyAttribute(lambda _: ShipRequirements(power=0, crew=0))
    condition = 100
    integrity = 1.0


class ShipEngineFactory(factory.Factory):
    class Meta:
        model = ShipEngine

    symbol = ShipEngineSymbol.ENGINE_IMPULSE_DRIVE_I
    name = "Impulse Drive I"
    description = "A basic impulse drive"
    speed = 2
    requirements = LazyAttribute(lambda _: ShipRequirements(power=1, crew=0))
    condition = 100
    integrity = 1.0


class ShipNavFactory(factory.Factory):
    class Meta:
        model = ShipNav

    system_symbol = "TEST-SYSTEM"
    waypoint_symbol = "TEST-SYSTEM-WAYPOINT"
    route = LazyAttribute(lambda _: ShipNavRoute(
        destination=WaypointFactory(),
        origin=WaypointFactory(),
        departure_time=datetime.now(timezone.utc),
        arrival=datetime.now(timezone.utc)
    ))
    status = ShipNavStatus.DOCKED
    flight_mode = ShipNavFlightMode.CRUISE


class ShipRegistrationFactory(factory.Factory):
    class Meta:
        model = ShipRegistration

    name = "Test Ship"
    role = ShipRole.EXCAVATOR
    faction_symbol = "TEST_FACTION"


class ShipFactory(factory.Factory):
    class Meta:
        model = Ship

    symbol = Sequence(lambda n: f"TEST_SHIP_{n}")
    registration = LazyAttribute(lambda _: ShipRegistration(
        name="Test Ship",
        role=ShipRole.COMMAND,
        faction_symbol="TEST_FACTION"
    ))
    nav = SubFactory(ShipNavFactory)
    crew = LazyAttribute(lambda _: ShipCrew(
        current=1,
        required=1,
        capacity=2,
        rotation=ShipCrewRotation.STRICT,
        wages=100,
        morale=100
    ))
    frame = SubFactory(ShipFrameFactory)
    reactor = SubFactory(ShipReactorFactory)
    engine = SubFactory(ShipEngineFactory)
    modules = []
    mounts = []
    cargo = LazyAttribute(lambda _: ShipCargo(
        capacity=100,
        units=0,
        inventory=[]
    ))
    fuel = LazyAttribute(lambda _: ShipFuel(
        current=1000,
        capacity=1000,
        consumed=ShipFuelConsumed(
            amount=0,
            timestamp=datetime.now(timezone.utc)
        )
    ))
    cooldown = LazyAttribute(lambda obj: Cooldown(
        ship_symbol=obj.symbol,
        total_seconds=0,
        remaining_seconds=0,
        expiration=UNSET
    ))
