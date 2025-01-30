from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_agent_response_200 import GetAgentResponse200
from ...types import Response


def _get_kwargs(
    agent_symbol: str = "FEBA66",
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/agents/{agent_symbol}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GetAgentResponse200]:
    if response.status_code == 200:
        response_200 = GetAgentResponse200.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GetAgentResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    agent_symbol: str = "FEBA66",
    *,
    client: AuthenticatedClient,
) -> Response[GetAgentResponse200]:
    """Get Public Agent

     Fetch agent details.

    Args:
        agent_symbol (str):  Default: 'FEBA66'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAgentResponse200]
    """

    kwargs = _get_kwargs(
        agent_symbol=agent_symbol,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    agent_symbol: str = "FEBA66",
    *,
    client: AuthenticatedClient,
) -> Optional[GetAgentResponse200]:
    """Get Public Agent

     Fetch agent details.

    Args:
        agent_symbol (str):  Default: 'FEBA66'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAgentResponse200
    """

    return sync_detailed(
        agent_symbol=agent_symbol,
        client=client,
    ).parsed


async def asyncio_detailed(
    agent_symbol: str = "FEBA66",
    *,
    client: AuthenticatedClient,
) -> Response[GetAgentResponse200]:
    """Get Public Agent

     Fetch agent details.

    Args:
        agent_symbol (str):  Default: 'FEBA66'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAgentResponse200]
    """

    kwargs = _get_kwargs(
        agent_symbol=agent_symbol,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    agent_symbol: str = "FEBA66",
    *,
    client: AuthenticatedClient,
) -> Optional[GetAgentResponse200]:
    """Get Public Agent

     Fetch agent details.

    Args:
        agent_symbol (str):  Default: 'FEBA66'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAgentResponse200
    """

    return (
        await asyncio_detailed(
            agent_symbol=agent_symbol,
            client=client,
        )
    ).parsed
