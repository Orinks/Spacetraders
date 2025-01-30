from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.register_body import RegisterBody
from ...models.register_response_201 import RegisterResponse201
from ...types import Response


def _get_kwargs(
    *,
    body: RegisterBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/register",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[RegisterResponse201]:
    if response.status_code == 201:
        response_201 = RegisterResponse201.from_dict(response.json())

        return response_201
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[RegisterResponse201]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: RegisterBody,
) -> Response[RegisterResponse201]:
    """Register New Agent

     Creates a new agent and ties it to an account.
    The agent symbol must consist of a 3-14 character string, and will be used to represent your agent.
    This symbol will prefix the symbol of every ship you own. Agent symbols will be cast to all
    uppercase characters.

    This new agent will be tied to a starting faction of your choice, which determines your starting
    location, and will be granted an authorization token, a contract with their starting faction, a
    command ship that can fly across space with advanced capabilities, a small probe ship that can be
    used for reconnaissance, and 150,000 credits.

    > #### Keep your token safe and secure
    >
    > Save your token during the alpha phase. There is no way to regenerate this token without starting
    a new agent. In the future you will be able to generate and manage your tokens from the SpaceTraders
    website.

    If you are new to SpaceTraders, It is recommended to register with the COSMIC faction, a faction
    that is well connected to the rest of the universe. After registering, you should try our
    interactive [quickstart guide](https://docs.spacetraders.io/quickstart/new-game) which will walk you
    through basic API requests in just a few minutes.

    Args:
        body (RegisterBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegisterResponse201]
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
    client: Union[AuthenticatedClient, Client],
    body: RegisterBody,
) -> Optional[RegisterResponse201]:
    """Register New Agent

     Creates a new agent and ties it to an account.
    The agent symbol must consist of a 3-14 character string, and will be used to represent your agent.
    This symbol will prefix the symbol of every ship you own. Agent symbols will be cast to all
    uppercase characters.

    This new agent will be tied to a starting faction of your choice, which determines your starting
    location, and will be granted an authorization token, a contract with their starting faction, a
    command ship that can fly across space with advanced capabilities, a small probe ship that can be
    used for reconnaissance, and 150,000 credits.

    > #### Keep your token safe and secure
    >
    > Save your token during the alpha phase. There is no way to regenerate this token without starting
    a new agent. In the future you will be able to generate and manage your tokens from the SpaceTraders
    website.

    If you are new to SpaceTraders, It is recommended to register with the COSMIC faction, a faction
    that is well connected to the rest of the universe. After registering, you should try our
    interactive [quickstart guide](https://docs.spacetraders.io/quickstart/new-game) which will walk you
    through basic API requests in just a few minutes.

    Args:
        body (RegisterBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegisterResponse201
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: RegisterBody,
) -> Response[RegisterResponse201]:
    """Register New Agent

     Creates a new agent and ties it to an account.
    The agent symbol must consist of a 3-14 character string, and will be used to represent your agent.
    This symbol will prefix the symbol of every ship you own. Agent symbols will be cast to all
    uppercase characters.

    This new agent will be tied to a starting faction of your choice, which determines your starting
    location, and will be granted an authorization token, a contract with their starting faction, a
    command ship that can fly across space with advanced capabilities, a small probe ship that can be
    used for reconnaissance, and 150,000 credits.

    > #### Keep your token safe and secure
    >
    > Save your token during the alpha phase. There is no way to regenerate this token without starting
    a new agent. In the future you will be able to generate and manage your tokens from the SpaceTraders
    website.

    If you are new to SpaceTraders, It is recommended to register with the COSMIC faction, a faction
    that is well connected to the rest of the universe. After registering, you should try our
    interactive [quickstart guide](https://docs.spacetraders.io/quickstart/new-game) which will walk you
    through basic API requests in just a few minutes.

    Args:
        body (RegisterBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegisterResponse201]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: RegisterBody,
) -> Optional[RegisterResponse201]:
    """Register New Agent

     Creates a new agent and ties it to an account.
    The agent symbol must consist of a 3-14 character string, and will be used to represent your agent.
    This symbol will prefix the symbol of every ship you own. Agent symbols will be cast to all
    uppercase characters.

    This new agent will be tied to a starting faction of your choice, which determines your starting
    location, and will be granted an authorization token, a contract with their starting faction, a
    command ship that can fly across space with advanced capabilities, a small probe ship that can be
    used for reconnaissance, and 150,000 credits.

    > #### Keep your token safe and secure
    >
    > Save your token during the alpha phase. There is no way to regenerate this token without starting
    a new agent. In the future you will be able to generate and manage your tokens from the SpaceTraders
    website.

    If you are new to SpaceTraders, It is recommended to register with the COSMIC faction, a faction
    that is well connected to the rest of the universe. After registering, you should try our
    interactive [quickstart guide](https://docs.spacetraders.io/quickstart/new-game) which will walk you
    through basic API requests in just a few minutes.

    Args:
        body (RegisterBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegisterResponse201
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
