"""
Tests for the SpaceTrader game automation
"""
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from space_traders_api_client.models.agent import Agent
from space_traders_api_client.models.ship import Ship
from space_traders_api_client.models.ship_nav import ShipNav
from space_traders_api_client.models.ship_fuel import ShipFuel
from space_traders_api_client.models.ship_cargo import ShipCargo
from space_traders_api_client.models.system import System
from space_traders_api_client.models.system_type import SystemType
from space_traders_api_client.models.waypoint_type import WaypointType
from space_traders_api_client.models.waypoint_trait import WaypointTrait
from space_traders_api_client.models.ship_type import ShipType
from space_traders_api_client.models.contract import Contract
from space_traders_api_client.models.contract_terms import ContractTerms
from space_traders_api_client.models.meta import Meta
from space_traders_api_client.models.ship_nav_status import ShipNavStatus
from space_traders_api_client.models.get_my_agent_response_200 import (
    GetMyAgentResponse200,
)
from space_traders_api_client.models.get_my_ships_response_200 import (
    GetMyShipsResponse200,
)
from space_traders_api_client.models.get_system_response_200 import (
    GetSystemResponse200,
)
from space_traders_api_client.models.get_system_waypoints_response_200 import (
    GetSystemWaypointsResponse200,
)
from space_traders_api_client.models.waypoint import Waypoint
from space_traders_api_client.types import Response as STResponse

from game.trader import SpaceTrader
from tests.factories import (
    AgentFactory,
    ShipFactory,
    SystemFactory,
    WaypointFactory,
    ContractFactory,
    ShipNavFactory,
    ShipRegistrationFactory,
)


@pytest.fixture
def mock_agent() -> Agent:
    """Create a mock agent for testing"""
    # Fixed symbol instead of using sequence
    return AgentFactory(symbol="TEST_AGENT")


@pytest.fixture
def mock_ship() -> Ship:
    """Create a mock ship for testing"""
    return ShipFactory(
        symbol="TEST_SHIP_1",
        registration={
            "name": "Test Ship", "role": "EXPLORER", 
            "factionSymbol": "TEST_FACTION"
        },
        frame={"symbol": "FRAME_EXPLORER", "name": "Explorer Frame"},
        mounts=[{
            "symbol": "MOUNT_LASER_I",
            "name": "Laser I",
            "description": "A basic laser for defense",
            "strength": 10
        }],
        nav=ShipNav(
            system_symbol="test-system-XXX",
            waypoint_symbol="test-system-XXX",
            route=None,
            status=ShipNavStatus.DOCKED,
            flight_mode="CRUISE"
        ),
        fuel=ShipFuel(
            current=100,
            capacity=100
        ),
        cargo=ShipCargo(
            capacity=100,
            units=0,
            inventory=[]
        )
    )


@pytest.fixture
def mock_system() -> System:
    """Create a mock system for testing"""
    return SystemFactory(
        symbol="test-system-XXX",
        type_=SystemType.NEUTRON_STAR
    )


@pytest.fixture
def trader():
    """Create a SpaceTrader instance for testing"""
    return SpaceTrader("test_token")


@pytest.fixture
def mock_waypoint() -> Waypoint:
    """Create a mock waypoint for testing"""
    return WaypointFactory(
        type_=WaypointType.ENGINEERED_ASTEROID,
        traits=[
            WaypointTrait(
                symbol="MINERAL_DEPOSITS",
                name="Mineral Deposits",
                description="Rich in mineral deposits"
            )
        ]
    )


@pytest.fixture
def mock_shipyard_waypoint() -> Waypoint:
    """Create a mock shipyard waypoint for testing"""
    return WaypointFactory(
        type_=WaypointType.ORBITAL_STATION,
        traits=[
            WaypointTrait(
                symbol="SHIPYARD",
                name="Shipyard",
                description="A shipyard for constructing and repairing ships"
            )
        ]
    )


@pytest.fixture
def mock_mining_ship() -> Ship:
    """Create a mock mining ship for testing"""
    return ShipFactory(
        symbol="MINING_SHIP_1",
        registration={
            "name": "Mining Ship", "role": "EXCAVATOR",
            "factionSymbol": "TEST_FACTION"
        },
        frame={"symbol": "FRAME_MINER", "name": "Mining Frame"},
        mounts=[{
            "symbol": "MOUNT_MINING_LASER_I",
            "name": "Mining Laser I",
            "description": "A basic mining laser for extracting resources",
            "strength": 10
        }]
    )


@pytest.fixture
def mock_contract() -> Contract:
    """Create a mock contract for testing"""
    return ContractFactory()


@pytest.mark.asyncio
async def test_initialization(trader, mock_agent, mock_ship, mock_system):
    """Test trader initialization process"""
    # Mock API responses
    agent_response = STResponse(
        status_code=200,
        content=b"",
        headers={},
        parsed=GetMyAgentResponse200(data=mock_agent)
    )
    
    ships_response = STResponse(
        status_code=200,
        content=b"",
        headers={},
        parsed=GetMyShipsResponse200(data=[mock_ship], meta=Meta(total=1))
    )
    
    system_response = STResponse(
        status_code=200,
        content=b"",
        headers={},
        parsed=GetSystemResponse200(data=mock_system)
    )
    
    # Patch API calls
    with patch(
        "game.trader.get_my_agent.asyncio_detailed",
        AsyncMock(return_value=agent_response)
    ), patch(
        "game.trader.get_my_ships.asyncio_detailed",
        AsyncMock(return_value=ships_response)
    ), patch(
        "game.trader.get_system.asyncio_detailed",
        AsyncMock(return_value=system_response)
    ):
        
        await trader.initialize()
        
        assert trader.agent == mock_agent
        assert trader.ships[mock_ship.symbol] == mock_ship
        assert trader.current_system == mock_system


@pytest.mark.asyncio
async def test_agent_status(trader, mock_agent):
    """Test agent status retrieval"""
    response = STResponse(
        status_code=200,
        content=b"",
        headers={},
        parsed=GetMyAgentResponse200(data=mock_agent)
    )
    
    with patch(
        "game.trader.get_my_agent.asyncio_detailed",
        AsyncMock(return_value=response)
    ):
        agent = await trader.get_agent_status()
        assert agent == mock_agent
        assert agent.symbol == "TEST_AGENT"
        assert agent.credits_ == 100000


@pytest.mark.asyncio
async def test_find_engineered_asteroids(trader, mock_waypoint):
    """Test finding engineered asteroids"""
    response = STResponse(
        status_code=200,
        content=b'{}',  # Mocking an empty JSON response
        headers={"Content-Type": "application/json"},
        parsed=GetSystemWaypointsResponse200(
            data=[mock_waypoint],
            meta=Meta(total=1)
        )
    )
    
    with patch(
        "game.trader.get_system_waypoints.sync_detailed",
        AsyncMock(return_value=response)
    ):
        asteroids = await trader.find_engineered_asteroids("TEST-SYSTEM")
        assert len(asteroids) == 1
        assert asteroids[0].type_ == WaypointType.ENGINEERED_ASTEROID


@pytest.mark.asyncio
async def test_navigation_operations(trader, mock_mining_ship):
    """Test ship navigation operations"""
    # Test navigation
    with patch(
        "game.trader.navigate_ship.sync_detailed",
        AsyncMock(return_value=STResponse(
            status_code=200,
            content=b'{"data": {"nav": {"status": "IN_TRANSIT"}}}',
            headers={"content-type": "application/json"},
            parsed={
                "data": {
                    "nav": {"status": "IN_TRANSIT"}
                }
            }
        ))
    ):
        success = await trader.navigate_to_waypoint(
            mock_mining_ship.symbol,
            "TEST-WAYPOINT"
        )
        assert success is True
        
    # Test docking
    with patch(
        "game.trader.dock_ship.sync_detailed",
        AsyncMock(return_value=STResponse(
            status_code=200,
            content=b'{"data": {"nav": {"status": "DOCKED"}}}',
            headers={"content-type": "application/json"},
            parsed={
                "data": {
                    "nav": {"status": "DOCKED"}
                }
            }
        ))
    ):
        success = await trader.dock_ship(mock_mining_ship.symbol)
        assert success is True
        
    # Test orbiting
    with patch(
        "game.trader.orbit_ship.sync_detailed",
        AsyncMock(return_value=STResponse(
            status_code=200,
            content=b'{"data": {"nav": {"status": "IN_ORBIT"}}}',
            headers={"content-type": "application/json"},
            parsed={
                "data": {
                    "nav": {"status": "IN_ORBIT"}
                }
            }
        ))
    ):
        success = await trader.orbit_ship(mock_mining_ship.symbol)
        assert success is True


@pytest.mark.asyncio
async def test_mining_operations(trader, mock_mining_ship):
    """Test mining operations"""
    # Mock successful extraction
    extraction_response = STResponse(
        status_code=200,
        content=b'{"data":{"extraction":{"shipSymbol":"MINING_SHIP_1","yield":{"symbol":"IRON_ORE","units":10}},"cooldown":{"shipSymbol":"MINING_SHIP_1","totalSeconds":60,"remainingSeconds":60}}}',
        headers={"content-type": "application/json"},
        parsed={
            "data": {
                "extraction": {
                    "shipSymbol": mock_mining_ship.symbol,
                    "yield": {
                        "symbol": "IRON_ORE",
                        "units": 10
                    }
                },
                "cooldown": {
                    "shipSymbol": mock_mining_ship.symbol,
                    "totalSeconds": 60,
                    "remainingSeconds": 60
                }
            }
        }
    )
    
    with patch(
        "game.trader.extract_resources.sync_detailed",
        AsyncMock(return_value=extraction_response)
    ):
        result = await trader.extract_resources(mock_mining_ship.symbol)
        assert result is not None
        assert result["extraction"]["yield"]["symbol"] == "IRON_ORE"


@pytest.mark.asyncio
async def test_purchase_mining_ship(trader, mock_shipyard_waypoint):
    """Test purchasing a mining ship"""
    # Mock finding shipyard
    shipyard_response = STResponse(
        status_code=200,
        content=(
            b'{"data":[{"symbol":"TEST-SYSTEM-SHIPYARD"}],'
            b'"meta":{"total":1}}'
        ),
        headers={"content-type": "application/json"},
        
        parsed=GetSystemWaypointsResponse200(
            data=[mock_shipyard_waypoint],
            meta=Meta(total=1)
        )
    )
    
    # Mock available ships
    ships_response = STResponse(
        status_code=200,
        content=(
            b'{"data":{"ships":[{"type":"SHIP_MINING_DRONE",'
            b'"name":"Mining Drone",'
            b'"description":"A basic mining drone",'
            b'"purchasePrice":50000}]}}'
        ),
        headers={"content-type": "application/json"},
        parsed={
            "data": {
                "ships": [
                    {
                        "type": ShipType.SHIP_MINING_DRONE,
                        "name": "Mining Drone",
                        "description": "A basic mining drone",
                        "purchasePrice": 50000
                    }
                ]
            }
        }
    )
    
    # Mock purchase response
    purchase_response = STResponse(
        status_code=201,
        content=(
            b'{"data":{"ship":{"symbol":"TEST_MINER_2",'
            b'"registration":{'
            b'"name":"Mining Drone",'
            b'"role":"EXCAVATOR",'
            b'"factionSymbol":"TEST_FACTION"}}}}'
        ),
        headers={"content-type": "application/json"},
        parsed={
            "data": {
                "ship": ShipFactory(
                    symbol="TEST_MINER_2",
                    registration=ShipRegistrationFactory(
                        name="Mining Drone",
                        role="EXCAVATOR",
                        faction_symbol="TEST_FACTION"
                    ),
                    frame={
                        "symbol": "FRAME_MINER", "name": "Mining Frame"
                    },
                    mounts=[{
                        "symbol": "MOUNT_MINING_LASER_I",
                        "name": "Mining Laser I",
                        "description": (
                            "A basic mining laser for extracting resources"
                        ),
                        "strength": 10
                    }],
                    nav=ShipNavFactory(
                        system_symbol="test-system-XXX",
                        waypoint_symbol="test-system-XXX",
                        route=None,
                        status=ShipNavStatus.DOCKED,
                        flight_mode="CRUISE"
                    ),
                    fuel=ShipFuel(
                        current=100,
                        capacity=100
                    ),
                    cargo=ShipCargo(
                        capacity=100,
                        units=0,
                        inventory=[]
                    )
                )
            }
        }
    )
    
    with patch(
        "game.trader.get_system_waypoints.asyncio_detailed",
        AsyncMock(return_value=shipyard_response)
    ), patch(
        "game.trader.get_shipyard.asyncio_detailed",
        AsyncMock(return_value=ships_response)
    ), patch(
        "game.trader.purchase_ship.asyncio_detailed",
        AsyncMock(return_value=purchase_response)
    ):
        
        ship = await trader.purchase_mining_ship("test-system-XXX")
        assert ship is not None
        assert ship.symbol == "TEST_MINER_2"
        assert ship.registration.role == "EXCAVATOR"


@pytest.mark.asyncio
async def test_process_contract_error_handling(trader, mock_contract):
    """Test contract processing error handling"""
    # Test with invalid contract (no delivery requirements)
    invalid_contract = Contract(
        id="test-contract-2",
        faction_symbol="TEST_FACTION",
        type_="PROCUREMENT",
        terms=ContractTerms(
            deadline=datetime.now(),
            payment={"onAccepted": 1000, "onFulfilled": 10000},
            deliver=[]
        ),
        accepted=True,
        fulfilled=False,
        expiration=datetime.now(),
        deadline_to_accept=datetime.now()
    )
    
    # Should handle missing terms gracefully
    await trader._process_contract(invalid_contract)
    
    # Test with valid contract but failed delivery
    with patch(
        "space_traders_api_client.api.contracts.deliver_contract",
        AsyncMock(return_value=False)
    ):
        await trader._process_contract(mock_contract)
        
    # Test with missing ship data
    trader.ships = {}
    await trader._process_contract(mock_contract)
