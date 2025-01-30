from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_system_response_200 import GetSystemResponse200
from ...types import Response


def _get_kwargs(
    system_symbol: str = "X1-OE",
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/systems/{system_symbol}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GetSystemResponse200]:
    if response.status_code == 200:
        response_200 = GetSystemResponse200.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GetSystemResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    system_symbol: str = "X1-OE",
    *,
    client: AuthenticatedClient,
) -> Response[GetSystemResponse200]:
    """Get System

     Get the details of a system.

    Args:
        system_symbol (str):  Default: 'X1-OE'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSystemResponse200]
    """

    kwargs = _get_kwargs(
        system_symbol=system_symbol,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    system_symbol: str = "X1-OE",
    *,
    client: AuthenticatedClient,
) -> Optional[GetSystemResponse200]:
    """Get System

     Get the details of a system.

    Args:
        system_symbol (str):  Default: 'X1-OE'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSystemResponse200
    """

    return sync_detailed(
        system_symbol=system_symbol,
        client=client,
    ).parsed


async def asyncio_detailed(
    system_symbol: str = "X1-OE",
    *,
    client: AuthenticatedClient,
) -> Response[GetSystemResponse200]:
    """Get System

     Get the details of a system.

    Args:
        system_symbol (str):  Default: 'X1-OE'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSystemResponse200]
    """

    kwargs = _get_kwargs(
        system_symbol=system_symbol,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    system_symbol: str = "X1-OE",
    *,
    client: AuthenticatedClient,
) -> Optional[GetSystemResponse200]:
    """Get System

     Get the details of a system.

    Args:
        system_symbol (str):  Default: 'X1-OE'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSystemResponse200
    """

    return (
        await asyncio_detailed(
            system_symbol=system_symbol,
            client=client,
        )
    ).parsed
