from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.warp_ship_body import WarpShipBody
from ...models.warp_ship_response_200 import WarpShipResponse200
from ...types import Response


def _get_kwargs(
    ship_symbol: str,
    *,
    body: WarpShipBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/my/ships/{ship_symbol}/warp",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[WarpShipResponse200]:
    if response.status_code == 200:
        response_200 = WarpShipResponse200.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[WarpShipResponse200]:
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
    body: WarpShipBody,
) -> Response[WarpShipResponse200]:
    """Warp Ship

     Warp your ship to a target destination in another system. The ship must be in orbit to use this
    function and must have the `Warp Drive` module installed. Warping will consume the necessary fuel
    from the ship's manifest.

    The returned response will detail the route information including the expected time of arrival. Most
    ship actions are unavailable until the ship has arrived at its destination.

    Args:
        ship_symbol (str):
        body (WarpShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WarpShipResponse200]
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
    body: WarpShipBody,
) -> Optional[WarpShipResponse200]:
    """Warp Ship

     Warp your ship to a target destination in another system. The ship must be in orbit to use this
    function and must have the `Warp Drive` module installed. Warping will consume the necessary fuel
    from the ship's manifest.

    The returned response will detail the route information including the expected time of arrival. Most
    ship actions are unavailable until the ship has arrived at its destination.

    Args:
        ship_symbol (str):
        body (WarpShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WarpShipResponse200
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
    body: WarpShipBody,
) -> Response[WarpShipResponse200]:
    """Warp Ship

     Warp your ship to a target destination in another system. The ship must be in orbit to use this
    function and must have the `Warp Drive` module installed. Warping will consume the necessary fuel
    from the ship's manifest.

    The returned response will detail the route information including the expected time of arrival. Most
    ship actions are unavailable until the ship has arrived at its destination.

    Args:
        ship_symbol (str):
        body (WarpShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WarpShipResponse200]
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
    body: WarpShipBody,
) -> Optional[WarpShipResponse200]:
    """Warp Ship

     Warp your ship to a target destination in another system. The ship must be in orbit to use this
    function and must have the `Warp Drive` module installed. Warping will consume the necessary fuel
    from the ship's manifest.

    The returned response will detail the route information including the expected time of arrival. Most
    ship actions are unavailable until the ship has arrived at its destination.

    Args:
        ship_symbol (str):
        body (WarpShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WarpShipResponse200
    """

    return (
        await asyncio_detailed(
            ship_symbol=ship_symbol,
            client=client,
            body=body,
        )
    ).parsed
