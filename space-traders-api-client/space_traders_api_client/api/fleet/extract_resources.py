from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.extract_resources_body import ExtractResourcesBody
from ...models.extract_resources_response_201 import ExtractResourcesResponse201
from ...types import Response


def _get_kwargs(
    ship_symbol: str,
    *,
    body: ExtractResourcesBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/my/ships/{ship_symbol}/extract",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ExtractResourcesResponse201]:
    if response.status_code == 201:
        response_201 = ExtractResourcesResponse201.from_dict(response.json())

        return response_201
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ExtractResourcesResponse201]:
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
    body: ExtractResourcesBody,
) -> Response[ExtractResourcesResponse201]:
    """Extract Resources

     Extract resources from a waypoint that can be extracted, such as asteroid fields, into your ship.
    Send an optional survey as the payload to target specific yields.

    The ship must be in orbit to be able to extract and must have mining equipments installed that can
    extract goods, such as the `Gas Siphon` mount for gas-based goods or `Mining Laser` mount for ore-
    based goods.

    The survey property is now deprecated. See the `extract/survey` endpoint for more details.

    Args:
        ship_symbol (str):
        body (ExtractResourcesBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ExtractResourcesResponse201]
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
    body: ExtractResourcesBody,
) -> Optional[ExtractResourcesResponse201]:
    """Extract Resources

     Extract resources from a waypoint that can be extracted, such as asteroid fields, into your ship.
    Send an optional survey as the payload to target specific yields.

    The ship must be in orbit to be able to extract and must have mining equipments installed that can
    extract goods, such as the `Gas Siphon` mount for gas-based goods or `Mining Laser` mount for ore-
    based goods.

    The survey property is now deprecated. See the `extract/survey` endpoint for more details.

    Args:
        ship_symbol (str):
        body (ExtractResourcesBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ExtractResourcesResponse201
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
    body: ExtractResourcesBody,
) -> Response[ExtractResourcesResponse201]:
    """Extract Resources

     Extract resources from a waypoint that can be extracted, such as asteroid fields, into your ship.
    Send an optional survey as the payload to target specific yields.

    The ship must be in orbit to be able to extract and must have mining equipments installed that can
    extract goods, such as the `Gas Siphon` mount for gas-based goods or `Mining Laser` mount for ore-
    based goods.

    The survey property is now deprecated. See the `extract/survey` endpoint for more details.

    Args:
        ship_symbol (str):
        body (ExtractResourcesBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ExtractResourcesResponse201]
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
    body: ExtractResourcesBody,
) -> Optional[ExtractResourcesResponse201]:
    """Extract Resources

     Extract resources from a waypoint that can be extracted, such as asteroid fields, into your ship.
    Send an optional survey as the payload to target specific yields.

    The ship must be in orbit to be able to extract and must have mining equipments installed that can
    extract goods, such as the `Gas Siphon` mount for gas-based goods or `Mining Laser` mount for ore-
    based goods.

    The survey property is now deprecated. See the `extract/survey` endpoint for more details.

    Args:
        ship_symbol (str):
        body (ExtractResourcesBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ExtractResourcesResponse201
    """

    return (
        await asyncio_detailed(
            ship_symbol=ship_symbol,
            client=client,
            body=body,
        )
    ).parsed
