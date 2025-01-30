from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.purchase_cargo_purchase_cargo_201_response import PurchaseCargoPurchaseCargo201Response
from ...models.purchase_cargo_purchase_cargo_request import PurchaseCargoPurchaseCargoRequest
from ...types import Response


def _get_kwargs(
    ship_symbol: str,
    *,
    body: PurchaseCargoPurchaseCargoRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/my/ships/{ship_symbol}/purchase",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PurchaseCargoPurchaseCargo201Response]:
    if response.status_code == 201:
        response_201 = PurchaseCargoPurchaseCargo201Response.from_dict(response.json())

        return response_201
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PurchaseCargoPurchaseCargo201Response]:
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
    body: PurchaseCargoPurchaseCargoRequest,
) -> Response[PurchaseCargoPurchaseCargo201Response]:
    """Purchase Cargo

     Purchase cargo from a market.

    The ship must be docked in a waypoint that has `Marketplace` trait, and the market must be selling a
    good to be able to purchase it.

    The maximum amount of units of a good that can be purchased in each transaction are denoted by the
    `tradeVolume` value of the good, which can be viewed by using the Get Market action.

    Purchased goods are added to the ship's cargo hold.

    Args:
        ship_symbol (str):
        body (PurchaseCargoPurchaseCargoRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PurchaseCargoPurchaseCargo201Response]
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
    body: PurchaseCargoPurchaseCargoRequest,
) -> Optional[PurchaseCargoPurchaseCargo201Response]:
    """Purchase Cargo

     Purchase cargo from a market.

    The ship must be docked in a waypoint that has `Marketplace` trait, and the market must be selling a
    good to be able to purchase it.

    The maximum amount of units of a good that can be purchased in each transaction are denoted by the
    `tradeVolume` value of the good, which can be viewed by using the Get Market action.

    Purchased goods are added to the ship's cargo hold.

    Args:
        ship_symbol (str):
        body (PurchaseCargoPurchaseCargoRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PurchaseCargoPurchaseCargo201Response
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
    body: PurchaseCargoPurchaseCargoRequest,
) -> Response[PurchaseCargoPurchaseCargo201Response]:
    """Purchase Cargo

     Purchase cargo from a market.

    The ship must be docked in a waypoint that has `Marketplace` trait, and the market must be selling a
    good to be able to purchase it.

    The maximum amount of units of a good that can be purchased in each transaction are denoted by the
    `tradeVolume` value of the good, which can be viewed by using the Get Market action.

    Purchased goods are added to the ship's cargo hold.

    Args:
        ship_symbol (str):
        body (PurchaseCargoPurchaseCargoRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PurchaseCargoPurchaseCargo201Response]
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
    body: PurchaseCargoPurchaseCargoRequest,
) -> Optional[PurchaseCargoPurchaseCargo201Response]:
    """Purchase Cargo

     Purchase cargo from a market.

    The ship must be docked in a waypoint that has `Marketplace` trait, and the market must be selling a
    good to be able to purchase it.

    The maximum amount of units of a good that can be purchased in each transaction are denoted by the
    `tradeVolume` value of the good, which can be viewed by using the Get Market action.

    Purchased goods are added to the ship's cargo hold.

    Args:
        ship_symbol (str):
        body (PurchaseCargoPurchaseCargoRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PurchaseCargoPurchaseCargo201Response
    """

    return (
        await asyncio_detailed(
            ship_symbol=ship_symbol,
            client=client,
            body=body,
        )
    ).parsed
