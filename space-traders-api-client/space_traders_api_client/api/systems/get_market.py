from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_market_response_200 import GetMarketResponse200
from ...types import Response


def _get_kwargs(
    system_symbol: str,
    waypoint_symbol: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/systems/{system_symbol}/waypoints/{waypoint_symbol}/market",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GetMarketResponse200]:
    if response.status_code == 200:
        response_200 = GetMarketResponse200.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GetMarketResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    system_symbol: str,
    waypoint_symbol: str,
    *,
    client: AuthenticatedClient,
) -> Response[GetMarketResponse200]:
    """Get Market

     Retrieve imports, exports and exchange data from a marketplace. Requires a waypoint that has the
    `Marketplace` trait to use.

    Send a ship to the waypoint to access trade good prices and recent transactions. Refer to the
    [Market Overview page](https://docs.spacetraders.io/game-concepts/markets) to gain better a
    understanding of the market in the game.

    Args:
        system_symbol (str):
        waypoint_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetMarketResponse200]
    """

    kwargs = _get_kwargs(
        system_symbol=system_symbol,
        waypoint_symbol=waypoint_symbol,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    system_symbol: str,
    waypoint_symbol: str,
    *,
    client: AuthenticatedClient,
) -> Optional[GetMarketResponse200]:
    """Get Market

     Retrieve imports, exports and exchange data from a marketplace. Requires a waypoint that has the
    `Marketplace` trait to use.

    Send a ship to the waypoint to access trade good prices and recent transactions. Refer to the
    [Market Overview page](https://docs.spacetraders.io/game-concepts/markets) to gain better a
    understanding of the market in the game.

    Args:
        system_symbol (str):
        waypoint_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetMarketResponse200
    """

    return sync_detailed(
        system_symbol=system_symbol,
        waypoint_symbol=waypoint_symbol,
        client=client,
    ).parsed


async def asyncio_detailed(
    system_symbol: str,
    waypoint_symbol: str,
    *,
    client: AuthenticatedClient,
) -> Response[GetMarketResponse200]:
    """Get Market

     Retrieve imports, exports and exchange data from a marketplace. Requires a waypoint that has the
    `Marketplace` trait to use.

    Send a ship to the waypoint to access trade good prices and recent transactions. Refer to the
    [Market Overview page](https://docs.spacetraders.io/game-concepts/markets) to gain better a
    understanding of the market in the game.

    Args:
        system_symbol (str):
        waypoint_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetMarketResponse200]
    """

    kwargs = _get_kwargs(
        system_symbol=system_symbol,
        waypoint_symbol=waypoint_symbol,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    system_symbol: str,
    waypoint_symbol: str,
    *,
    client: AuthenticatedClient,
) -> Optional[GetMarketResponse200]:
    """Get Market

     Retrieve imports, exports and exchange data from a marketplace. Requires a waypoint that has the
    `Marketplace` trait to use.

    Send a ship to the waypoint to access trade good prices and recent transactions. Refer to the
    [Market Overview page](https://docs.spacetraders.io/game-concepts/markets) to gain better a
    understanding of the market in the game.

    Args:
        system_symbol (str):
        waypoint_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetMarketResponse200
    """

    return (
        await asyncio_detailed(
            system_symbol=system_symbol,
            waypoint_symbol=waypoint_symbol,
            client=client,
        )
    ).parsed
