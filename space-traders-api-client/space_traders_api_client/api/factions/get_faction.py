from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_faction_response_200 import GetFactionResponse200
from ...types import Response


def _get_kwargs(
    faction_symbol: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/factions/{faction_symbol}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GetFactionResponse200]:
    if response.status_code == 200:
        response_200 = GetFactionResponse200.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GetFactionResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    faction_symbol: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[GetFactionResponse200]:
    """Get Faction

     View the details of a faction.

    Args:
        faction_symbol (str):  Example: COSMIC.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetFactionResponse200]
    """

    kwargs = _get_kwargs(
        faction_symbol=faction_symbol,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    faction_symbol: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[GetFactionResponse200]:
    """Get Faction

     View the details of a faction.

    Args:
        faction_symbol (str):  Example: COSMIC.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetFactionResponse200
    """

    return sync_detailed(
        faction_symbol=faction_symbol,
        client=client,
    ).parsed


async def asyncio_detailed(
    faction_symbol: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[GetFactionResponse200]:
    """Get Faction

     View the details of a faction.

    Args:
        faction_symbol (str):  Example: COSMIC.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetFactionResponse200]
    """

    kwargs = _get_kwargs(
        faction_symbol=faction_symbol,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    faction_symbol: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[GetFactionResponse200]:
    """Get Faction

     View the details of a faction.

    Args:
        faction_symbol (str):  Example: COSMIC.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetFactionResponse200
    """

    return (
        await asyncio_detailed(
            faction_symbol=faction_symbol,
            client=client,
        )
    ).parsed
