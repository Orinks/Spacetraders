from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.refuel_ship_body import RefuelShipBody
from ...models.refuel_ship_response_200 import RefuelShipResponse200
from ...types import Response


def _get_kwargs(
    ship_symbol: str,
    *,
    body: RefuelShipBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/my/ships/{ship_symbol}/refuel",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[RefuelShipResponse200]:
    if response.status_code == 200:
        response_200 = RefuelShipResponse200.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[RefuelShipResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    ship_symbol: str,
    *,
    client: AuthenticatedClient,
    body: RefuelShipBody,
) -> Response[RefuelShipResponse200]:
    """Refuel Ship

     Refuel your ship by buying fuel from the local market.

    Requires the ship to be docked in a waypoint that has the `Marketplace` trait, and the market must
    be selling fuel in order to refuel.

    Each fuel bought from the market replenishes 100 units in your ship's fuel.

    Ships will always be refuel to their frame's maximum fuel capacity when using this action.

    Args:
        ship_symbol (str):
        body (RefuelShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RefuelShipResponse200]
    """

    kwargs = _get_kwargs(
        ship_symbol=ship_symbol,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    ship_symbol: str,
    *,
    client: AuthenticatedClient,
    body: RefuelShipBody,
) -> Optional[RefuelShipResponse200]:
    """Refuel Ship

     Refuel your ship by buying fuel from the local market.

    Requires the ship to be docked in a waypoint that has the `Marketplace` trait, and the market must
    be selling fuel in order to refuel.

    Each fuel bought from the market replenishes 100 units in your ship's fuel.

    Ships will always be refuel to their frame's maximum fuel capacity when using this action.

    Args:
        ship_symbol (str):
        body (RefuelShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RefuelShipResponse200
    """

    return sync_detailed(
        ship_symbol=ship_symbol,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    ship_symbol: str,
    *,
    client: AuthenticatedClient,
    body: RefuelShipBody,
) -> Response[RefuelShipResponse200]:
    """Refuel Ship

     Refuel your ship by buying fuel from the local market.

    Requires the ship to be docked in a waypoint that has the `Marketplace` trait, and the market must
    be selling fuel in order to refuel.

    Each fuel bought from the market replenishes 100 units in your ship's fuel.

    Ships will always be refuel to their frame's maximum fuel capacity when using this action.

    Args:
        ship_symbol (str):
        body (RefuelShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RefuelShipResponse200]
    """

    kwargs = _get_kwargs(
        ship_symbol=ship_symbol,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ship_symbol: str,
    *,
    client: AuthenticatedClient,
    body: RefuelShipBody,
) -> Optional[RefuelShipResponse200]:
    """Refuel Ship

     Refuel your ship by buying fuel from the local market.

    Requires the ship to be docked in a waypoint that has the `Marketplace` trait, and the market must
    be selling fuel in order to refuel.

    Each fuel bought from the market replenishes 100 units in your ship's fuel.

    Ships will always be refuel to their frame's maximum fuel capacity when using this action.

    Args:
        ship_symbol (str):
        body (RefuelShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RefuelShipResponse200
    """

    return (
        await asyncio_detailed(
            ship_symbol=ship_symbol,
            client=client,
            body=body,
        )
    ).parsed
