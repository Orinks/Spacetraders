from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.supply_construction_body import SupplyConstructionBody
from ...models.supply_construction_response_201 import SupplyConstructionResponse201
from ...types import Response


def _get_kwargs(
    system_symbol: str,
    waypoint_symbol: str,
    *,
    body: SupplyConstructionBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/systems/{system_symbol}/waypoints/{waypoint_symbol}/construction/supply",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[SupplyConstructionResponse201]:
    if response.status_code == 201:
        response_201 = SupplyConstructionResponse201.from_dict(response.json())

        return response_201
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[SupplyConstructionResponse201]:
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
    body: SupplyConstructionBody,
) -> Response[SupplyConstructionResponse201]:
    """Supply Construction Site

     Supply a construction site with the specified good. Requires a waypoint with a property of
    `isUnderConstruction` to be true.

    The good must be in your ship's cargo. The good will be removed from your ship's cargo and added to
    the construction site's materials.

    Args:
        system_symbol (str):
        waypoint_symbol (str):
        body (SupplyConstructionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SupplyConstructionResponse201]
    """

    kwargs = _get_kwargs(
        system_symbol=system_symbol,
        waypoint_symbol=waypoint_symbol,
        body=body,
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
    body: SupplyConstructionBody,
) -> Optional[SupplyConstructionResponse201]:
    """Supply Construction Site

     Supply a construction site with the specified good. Requires a waypoint with a property of
    `isUnderConstruction` to be true.

    The good must be in your ship's cargo. The good will be removed from your ship's cargo and added to
    the construction site's materials.

    Args:
        system_symbol (str):
        waypoint_symbol (str):
        body (SupplyConstructionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SupplyConstructionResponse201
    """

    return sync_detailed(
        system_symbol=system_symbol,
        waypoint_symbol=waypoint_symbol,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    system_symbol: str,
    waypoint_symbol: str,
    *,
    client: AuthenticatedClient,
    body: SupplyConstructionBody,
) -> Response[SupplyConstructionResponse201]:
    """Supply Construction Site

     Supply a construction site with the specified good. Requires a waypoint with a property of
    `isUnderConstruction` to be true.

    The good must be in your ship's cargo. The good will be removed from your ship's cargo and added to
    the construction site's materials.

    Args:
        system_symbol (str):
        waypoint_symbol (str):
        body (SupplyConstructionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SupplyConstructionResponse201]
    """

    kwargs = _get_kwargs(
        system_symbol=system_symbol,
        waypoint_symbol=waypoint_symbol,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    system_symbol: str,
    waypoint_symbol: str,
    *,
    client: AuthenticatedClient,
    body: SupplyConstructionBody,
) -> Optional[SupplyConstructionResponse201]:
    """Supply Construction Site

     Supply a construction site with the specified good. Requires a waypoint with a property of
    `isUnderConstruction` to be true.

    The good must be in your ship's cargo. The good will be removed from your ship's cargo and added to
    the construction site's materials.

    Args:
        system_symbol (str):
        waypoint_symbol (str):
        body (SupplyConstructionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SupplyConstructionResponse201
    """

    return (
        await asyncio_detailed(
            system_symbol=system_symbol,
            waypoint_symbol=waypoint_symbol,
            client=client,
            body=body,
        )
    ).parsed
