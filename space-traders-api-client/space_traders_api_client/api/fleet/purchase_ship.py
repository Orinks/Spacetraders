from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.purchase_ship_body import PurchaseShipBody
from ...models.purchase_ship_response_201 import PurchaseShipResponse201
from ...types import Response


def _get_kwargs(
    *,
    body: PurchaseShipBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/my/ships",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PurchaseShipResponse201]:
    if response.status_code == 201:
        response_201 = PurchaseShipResponse201.from_dict(response.json())

        return response_201
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PurchaseShipResponse201]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: PurchaseShipBody,
) -> Response[PurchaseShipResponse201]:
    """Purchase Ship

     Purchase a ship from a Shipyard. In order to use this function, a ship under your agent's ownership
    must be in a waypoint that has the `Shipyard` trait, and the Shipyard must sell the type of the
    desired ship.

    Shipyards typically offer ship types, which are predefined templates of ships that have dedicated
    roles. A template comes with a preset of an engine, a reactor, and a frame. It may also include a
    few modules and mounts.

    Args:
        body (PurchaseShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PurchaseShipResponse201]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: PurchaseShipBody,
) -> Optional[PurchaseShipResponse201]:
    """Purchase Ship

     Purchase a ship from a Shipyard. In order to use this function, a ship under your agent's ownership
    must be in a waypoint that has the `Shipyard` trait, and the Shipyard must sell the type of the
    desired ship.

    Shipyards typically offer ship types, which are predefined templates of ships that have dedicated
    roles. A template comes with a preset of an engine, a reactor, and a frame. It may also include a
    few modules and mounts.

    Args:
        body (PurchaseShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PurchaseShipResponse201
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: PurchaseShipBody,
) -> Response[PurchaseShipResponse201]:
    """Purchase Ship

     Purchase a ship from a Shipyard. In order to use this function, a ship under your agent's ownership
    must be in a waypoint that has the `Shipyard` trait, and the Shipyard must sell the type of the
    desired ship.

    Shipyards typically offer ship types, which are predefined templates of ships that have dedicated
    roles. A template comes with a preset of an engine, a reactor, and a frame. It may also include a
    few modules and mounts.

    Args:
        body (PurchaseShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PurchaseShipResponse201]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: PurchaseShipBody,
) -> Optional[PurchaseShipResponse201]:
    """Purchase Ship

     Purchase a ship from a Shipyard. In order to use this function, a ship under your agent's ownership
    must be in a waypoint that has the `Shipyard` trait, and the Shipyard must sell the type of the
    desired ship.

    Shipyards typically offer ship types, which are predefined templates of ships that have dedicated
    roles. A template comes with a preset of an engine, a reactor, and a frame. It may also include a
    few modules and mounts.

    Args:
        body (PurchaseShipBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PurchaseShipResponse201
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
