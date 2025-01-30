from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_ship_waypoint_scan_response_201 import CreateShipWaypointScanResponse201
from ...types import Response


def _get_kwargs(
    ship_symbol: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/my/ships/{ship_symbol}/scan/waypoints",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[CreateShipWaypointScanResponse201]:
    if response.status_code == 201:
        response_201 = CreateShipWaypointScanResponse201.from_dict(response.json())

        return response_201
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[CreateShipWaypointScanResponse201]:
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
) -> Response[CreateShipWaypointScanResponse201]:
    """Scan Waypoints

     Scan for nearby waypoints, retrieving detailed information on each waypoint in range. Scanning
    uncharted waypoints will allow you to ignore their uncharted state and will list the waypoints'
    traits.

    Requires a ship to have the `Sensor Array` mount installed to use.

    The ship will enter a cooldown after using this function, during which it cannot execute certain
    actions.

    Args:
        ship_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateShipWaypointScanResponse201]
    """

    kwargs = _get_kwargs(
        ship_symbol=ship_symbol,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    ship_symbol: str,
    *,
    client: AuthenticatedClient,
) -> Optional[CreateShipWaypointScanResponse201]:
    """Scan Waypoints

     Scan for nearby waypoints, retrieving detailed information on each waypoint in range. Scanning
    uncharted waypoints will allow you to ignore their uncharted state and will list the waypoints'
    traits.

    Requires a ship to have the `Sensor Array` mount installed to use.

    The ship will enter a cooldown after using this function, during which it cannot execute certain
    actions.

    Args:
        ship_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateShipWaypointScanResponse201
    """

    return sync_detailed(
        ship_symbol=ship_symbol,
        client=client,
    ).parsed


async def asyncio_detailed(
    ship_symbol: str,
    *,
    client: AuthenticatedClient,
) -> Response[CreateShipWaypointScanResponse201]:
    """Scan Waypoints

     Scan for nearby waypoints, retrieving detailed information on each waypoint in range. Scanning
    uncharted waypoints will allow you to ignore their uncharted state and will list the waypoints'
    traits.

    Requires a ship to have the `Sensor Array` mount installed to use.

    The ship will enter a cooldown after using this function, during which it cannot execute certain
    actions.

    Args:
        ship_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateShipWaypointScanResponse201]
    """

    kwargs = _get_kwargs(
        ship_symbol=ship_symbol,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ship_symbol: str,
    *,
    client: AuthenticatedClient,
) -> Optional[CreateShipWaypointScanResponse201]:
    """Scan Waypoints

     Scan for nearby waypoints, retrieving detailed information on each waypoint in range. Scanning
    uncharted waypoints will allow you to ignore their uncharted state and will list the waypoints'
    traits.

    Requires a ship to have the `Sensor Array` mount installed to use.

    The ship will enter a cooldown after using this function, during which it cannot execute certain
    actions.

    Args:
        ship_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateShipWaypointScanResponse201
    """

    return (
        await asyncio_detailed(
            ship_symbol=ship_symbol,
            client=client,
        )
    ).parsed
