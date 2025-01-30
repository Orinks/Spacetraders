from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.transfer_cargo_transfer_cargo_200_response import TransferCargoTransferCargo200Response
from ...models.transfer_cargo_transfer_cargo_request import TransferCargoTransferCargoRequest
from ...types import Response


def _get_kwargs(
    ship_symbol: str,
    *,
    body: TransferCargoTransferCargoRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/my/ships/{ship_symbol}/transfer",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[TransferCargoTransferCargo200Response]:
    if response.status_code == 200:
        response_200 = TransferCargoTransferCargo200Response.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[TransferCargoTransferCargo200Response]:
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
    body: TransferCargoTransferCargoRequest,
) -> Response[TransferCargoTransferCargo200Response]:
    """Transfer Cargo

     Transfer cargo between ships.

    The receiving ship must be in the same waypoint as the transferring ship, and it must able to hold
    the additional cargo after the transfer is complete. Both ships also must be in the same state,
    either both are docked or both are orbiting.

    The response body's cargo shows the cargo of the transferring ship after the transfer is complete.

    Args:
        ship_symbol (str):
        body (TransferCargoTransferCargoRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TransferCargoTransferCargo200Response]
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
    body: TransferCargoTransferCargoRequest,
) -> Optional[TransferCargoTransferCargo200Response]:
    """Transfer Cargo

     Transfer cargo between ships.

    The receiving ship must be in the same waypoint as the transferring ship, and it must able to hold
    the additional cargo after the transfer is complete. Both ships also must be in the same state,
    either both are docked or both are orbiting.

    The response body's cargo shows the cargo of the transferring ship after the transfer is complete.

    Args:
        ship_symbol (str):
        body (TransferCargoTransferCargoRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TransferCargoTransferCargo200Response
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
    body: TransferCargoTransferCargoRequest,
) -> Response[TransferCargoTransferCargo200Response]:
    """Transfer Cargo

     Transfer cargo between ships.

    The receiving ship must be in the same waypoint as the transferring ship, and it must able to hold
    the additional cargo after the transfer is complete. Both ships also must be in the same state,
    either both are docked or both are orbiting.

    The response body's cargo shows the cargo of the transferring ship after the transfer is complete.

    Args:
        ship_symbol (str):
        body (TransferCargoTransferCargoRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TransferCargoTransferCargo200Response]
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
    body: TransferCargoTransferCargoRequest,
) -> Optional[TransferCargoTransferCargo200Response]:
    """Transfer Cargo

     Transfer cargo between ships.

    The receiving ship must be in the same waypoint as the transferring ship, and it must able to hold
    the additional cargo after the transfer is complete. Both ships also must be in the same state,
    either both are docked or both are orbiting.

    The response body's cargo shows the cargo of the transferring ship after the transfer is complete.

    Args:
        ship_symbol (str):
        body (TransferCargoTransferCargoRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TransferCargoTransferCargo200Response
    """

    return (
        await asyncio_detailed(
            ship_symbol=ship_symbol,
            client=client,
            body=body,
        )
    ).parsed
