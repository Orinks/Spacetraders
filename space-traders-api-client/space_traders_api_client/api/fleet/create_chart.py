from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_chart_response_201 import CreateChartResponse201
from ...types import Response


def _get_kwargs(
    ship_symbol: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/my/ships/{ship_symbol}/chart",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[CreateChartResponse201]:
    if response.status_code == 201:
        response_201 = CreateChartResponse201.from_dict(response.json())

        return response_201
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[CreateChartResponse201]:
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
) -> Response[CreateChartResponse201]:
    """Create Chart

     Command a ship to chart the waypoint at its current location.

    Most waypoints in the universe are uncharted by default. These waypoints have their traits hidden
    until they have been charted by a ship.

    Charting a waypoint will record your agent as the one who created the chart, and all other agents
    would also be able to see the waypoint's traits.

    Args:
        ship_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateChartResponse201]
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
) -> Optional[CreateChartResponse201]:
    """Create Chart

     Command a ship to chart the waypoint at its current location.

    Most waypoints in the universe are uncharted by default. These waypoints have their traits hidden
    until they have been charted by a ship.

    Charting a waypoint will record your agent as the one who created the chart, and all other agents
    would also be able to see the waypoint's traits.

    Args:
        ship_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateChartResponse201
    """

    return sync_detailed(
        ship_symbol=ship_symbol,
        client=client,
    ).parsed


async def asyncio_detailed(
    ship_symbol: str,
    *,
    client: AuthenticatedClient,
) -> Response[CreateChartResponse201]:
    """Create Chart

     Command a ship to chart the waypoint at its current location.

    Most waypoints in the universe are uncharted by default. These waypoints have their traits hidden
    until they have been charted by a ship.

    Charting a waypoint will record your agent as the one who created the chart, and all other agents
    would also be able to see the waypoint's traits.

    Args:
        ship_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateChartResponse201]
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
) -> Optional[CreateChartResponse201]:
    """Create Chart

     Command a ship to chart the waypoint at its current location.

    Most waypoints in the universe are uncharted by default. These waypoints have their traits hidden
    until they have been charted by a ship.

    Charting a waypoint will record your agent as the one who created the chart, and all other agents
    would also be able to see the waypoint's traits.

    Args:
        ship_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateChartResponse201
    """

    return (
        await asyncio_detailed(
            ship_symbol=ship_symbol,
            client=client,
        )
    ).parsed
