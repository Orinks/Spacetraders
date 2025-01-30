from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.jump_ship_body import JumpShipBody
from ...models.jump_ship_response_200 import JumpShipResponse200
from ...types import Response


def _get_kwargs(
    ship_symbol: str,
    *,
    body: JumpShipBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/my/ships/{ship_symbol}/jump",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[JumpShipResponse200]:
    if response.status_code == 200:
        response_200 = JumpShipResponse200.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[JumpShipResponse200]:
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
    body: JumpShipBody,
) -> Response[JumpShipResponse200]:
    """Jump Ship

     Jump your ship instantly to a target connected waypoint. The ship must be in orbit to execute a
    jump.

    A unit of antimatter is purchased and consumed from the market when jumping. The price of antimatter
    is determined by the market and is subject to change. A ship can only jump to connected waypoints

    Args:
        ship_symbol (str):
        body (JumpShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[JumpShipResponse200]
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
    body: JumpShipBody,
) -> Optional[JumpShipResponse200]:
    """Jump Ship

     Jump your ship instantly to a target connected waypoint. The ship must be in orbit to execute a
    jump.

    A unit of antimatter is purchased and consumed from the market when jumping. The price of antimatter
    is determined by the market and is subject to change. A ship can only jump to connected waypoints

    Args:
        ship_symbol (str):
        body (JumpShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        JumpShipResponse200
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
    body: JumpShipBody,
) -> Response[JumpShipResponse200]:
    """Jump Ship

     Jump your ship instantly to a target connected waypoint. The ship must be in orbit to execute a
    jump.

    A unit of antimatter is purchased and consumed from the market when jumping. The price of antimatter
    is determined by the market and is subject to change. A ship can only jump to connected waypoints

    Args:
        ship_symbol (str):
        body (JumpShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[JumpShipResponse200]
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
    body: JumpShipBody,
) -> Optional[JumpShipResponse200]:
    """Jump Ship

     Jump your ship instantly to a target connected waypoint. The ship must be in orbit to execute a
    jump.

    A unit of antimatter is purchased and consumed from the market when jumping. The price of antimatter
    is determined by the market and is subject to change. A ship can only jump to connected waypoints

    Args:
        ship_symbol (str):
        body (JumpShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        JumpShipResponse200
    """

    return (
        await asyncio_detailed(
            ship_symbol=ship_symbol,
            client=client,
            body=body,
        )
    ).parsed
