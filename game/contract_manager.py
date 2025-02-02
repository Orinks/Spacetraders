"""
Contract management for SpaceTraders
"""
from typing import Dict

from space_traders_api_client import AuthenticatedClient
from space_traders_api_client.api.contracts import (
    accept_contract,
    deliver_contract,
    fulfill_contract,
    get_contract,
    get_contracts,
)
from space_traders_api_client.models.contract import Contract
from space_traders_api_client.models.deliver_contract_body import (
    DeliverContractBody,
)


class ContractManager:
    """Manages contract operations and fulfillment"""
    
    def __init__(self, client: AuthenticatedClient):
        """Initialize ContractManager
        
        Args:
            client: Authenticated API client
        """
        self.client = client
        self.contracts: Dict[str, Contract] = {}
        
    async def update_contracts(self) -> None:
        """Update the list of available contracts"""
        try:
            response = await get_contracts.asyncio_detailed(
                client=self.client
            )
            if response.status_code == 200 and response.parsed:
                self.contracts = {
                    contract.id: contract
                    for contract in response.parsed.data
                }
                print(f"Found {len(self.contracts)} active contracts")
            else:
                print(f"Failed to get contracts: {response.status_code}")
        except Exception as e:
            print(f"Error updating contracts: {e}")

    async def accept_contract(self, contract_id: str) -> bool:
        """Accept a contract by ID"""
        try:
            response = await accept_contract.asyncio_detailed(
                contract_id=contract_id,
                client=self.client
            )
            if response.status_code == 200:
                print(f"Successfully accepted contract {contract_id}")
                await self.update_contracts()  # Refresh contracts
                return True
            else:
                print(f"Failed to accept contract: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error accepting contract: {e}")
            return False

    async def deliver_contract_cargo(
        self,
        contract_id: str,
        ship_symbol: str,
        trade_symbol: str,
        units: int
    ) -> bool:
        """Deliver cargo for a contract
        
        Args:
            contract_id: ID of the contract
            ship_symbol: Symbol of the ship delivering cargo
            trade_symbol: Symbol of the trade good
            units: Number of units to deliver
        """
        try:
            body = DeliverContractBody(
                ship_symbol=ship_symbol,
                trade_symbol=trade_symbol,
                units=units
            )
            response = await deliver_contract.asyncio_detailed(
                contract_id=contract_id,
                client=self.client,
                json_body=body.to_dict()
            )
            if response.status_code == 200:
                print(
                    f"Successfully delivered {units} units of {trade_symbol} "
                    f"for contract {contract_id}"
                )
                return True
            else:
                print(f"Failed to deliver cargo: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error delivering cargo: {e}")
            return False

    async def fulfill_contract(self, contract_id: str) -> bool:
        """Fulfill a completed contract"""
        try:
            response = await fulfill_contract.asyncio_detailed(
                contract_id=contract_id,
                client=self.client
            )
            if response.status_code == 200:
                print(f"Successfully fulfilled contract {contract_id}")
                await self.update_contracts()  # Refresh contracts
                return True
            else:
                print(f"Failed to fulfill contract: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error fulfilling contract: {e}")
            return False

    async def process_contract(self, contract: Contract) -> None:
        """Process a specific contract's requirements"""
        try:
            if not contract or not hasattr(contract, 'terms'):
                print('Contract has invalid format')
                return
                
            if not hasattr(contract.terms, 'deliver'):
                print(f'Contract {contract.id} has no delivery terms')
                return
                
            if not contract.terms.deliver:
                print(f'Contract {contract.id} has no delivery requirements')
                return

            for delivery in contract.terms.deliver:
                has_trade = hasattr(delivery, 'trade_symbol')
                has_units = hasattr(delivery, 'units_required')
                if not (has_trade and has_units):
                    print(
                        f'Delivery in contract {contract.id} '
                        'has invalid format'
                    )
                    continue

                # Check if contract can be fulfilled
                contract_details = await get_contract.asyncio(
                    contract_id=contract.id,
                    client=self.client
                )
                is_fulfilled = (
                    contract_details
                    and contract_details.data
                    and contract_details.data.fulfilled
                )
                if is_fulfilled:
                    await self.fulfill_contract(contract.id)
                    return
                    
        except Exception as e:
            contract_id = (
                contract.id if hasattr(contract, 'id') else 'unknown'
            )
            print(f'Error processing contract {contract_id}: {e}')