from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_system_waypoints_response_200 import GetSystemWaypointsResponse200
from ...models.waypoint_trait_symbol import WaypointTraitSymbol
from ...models.waypoint_type import WaypointType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    system_symbol: str,
    *,
    page: Union[Unset, int] = 1,
    limit: Union[Unset, int] = 10,
    type_: Union[Unset, WaypointType] = UNSET,
    traits: Union[Unset, WaypointTraitSymbol, list[WaypointTraitSymbol]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    json_type_: Union[Unset, str] = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_.value

    params["type"] = json_type_

    json_traits: Union[Unset, list[str], str]
    if isinstance(traits, Unset):
        json_traits = UNSET
    elif isinstance(traits, WaypointTraitSymbol):
        json_traits = traits.value
    else:
        json_traits = []
        for traits_type_1_item_data in traits:
            traits_type_1_item = traits_type_1_item_data.value
            json_traits.append(traits_type_1_item)

    params["traits"] = json_traits

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/systems/{system_symbol}/waypoints",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GetSystemWaypointsResponse200]:
    if response.status_code == 200:
        response_200 = GetSystemWaypointsResponse200.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GetSystemWaypointsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    system_symbol: str,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = 1,
    limit: Union[Unset, int] = 10,
    type_: Union[Unset, WaypointType] = UNSET,
    traits: Union[Unset, WaypointTraitSymbol, list[WaypointTraitSymbol]] = UNSET,
) -> Response[GetSystemWaypointsResponse200]:
    """List Waypoints in System

     Return a paginated list of all of the waypoints for a given system.

    If a waypoint is uncharted, it will return the `Uncharted` trait instead of its actual traits.

    Args:
        system_symbol (str):
        page (Union[Unset, int]):  Default: 1.
        limit (Union[Unset, int]):  Default: 10.
        type_ (Union[Unset, WaypointType]): The type of waypoint.
        traits (Union[Unset, WaypointTraitSymbol, list[WaypointTraitSymbol]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSystemWaypointsResponse200]
    """

    kwargs = _get_kwargs(
        system_symbol=system_symbol,
        page=page,
        limit=limit,
        type_=type_,
        traits=traits,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    system_symbol: str,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = 1,
    limit: Union[Unset, int] = 10,
    type_: Union[Unset, WaypointType] = UNSET,
    traits: Union[Unset, WaypointTraitSymbol, list[WaypointTraitSymbol]] = UNSET,
) -> Optional[GetSystemWaypointsResponse200]:
    """List Waypoints in System

     Return a paginated list of all of the waypoints for a given system.

    If a waypoint is uncharted, it will return the `Uncharted` trait instead of its actual traits.

    Args:
        system_symbol (str):
        page (Union[Unset, int]):  Default: 1.
        limit (Union[Unset, int]):  Default: 10.
        type_ (Union[Unset, WaypointType]): The type of waypoint.
        traits (Union[Unset, WaypointTraitSymbol, list[WaypointTraitSymbol]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSystemWaypointsResponse200
    """

    return sync_detailed(
        system_symbol=system_symbol,
        client=client,
        page=page,
        limit=limit,
        type_=type_,
        traits=traits,
    ).parsed


async def asyncio_detailed(
    system_symbol: str,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = 1,
    limit: Union[Unset, int] = 10,
    type_: Union[Unset, WaypointType] = UNSET,
    traits: Union[Unset, WaypointTraitSymbol, list[WaypointTraitSymbol]] = UNSET,
) -> Response[GetSystemWaypointsResponse200]:
    """List Waypoints in System

     Return a paginated list of all of the waypoints for a given system.

    If a waypoint is uncharted, it will return the `Uncharted` trait instead of its actual traits.

    Args:
        system_symbol (str):
        page (Union[Unset, int]):  Default: 1.
        limit (Union[Unset, int]):  Default: 10.
        type_ (Union[Unset, WaypointType]): The type of waypoint.
        traits (Union[Unset, WaypointTraitSymbol, list[WaypointTraitSymbol]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSystemWaypointsResponse200]
    """

    kwargs = _get_kwargs(
        system_symbol=system_symbol,
        page=page,
        limit=limit,
        type_=type_,
        traits=traits,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    system_symbol: str,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = 1,
    limit: Union[Unset, int] = 10,
    type_: Union[Unset, WaypointType] = UNSET,
    traits: Union[Unset, WaypointTraitSymbol, list[WaypointTraitSymbol]] = UNSET,
) -> Optional[GetSystemWaypointsResponse200]:
    """List Waypoints in System

     Return a paginated list of all of the waypoints for a given system.

    If a waypoint is uncharted, it will return the `Uncharted` trait instead of its actual traits.

    Args:
        system_symbol (str):
        page (Union[Unset, int]):  Default: 1.
        limit (Union[Unset, int]):  Default: 10.
        type_ (Union[Unset, WaypointType]): The type of waypoint.
        traits (Union[Unset, WaypointTraitSymbol, list[WaypointTraitSymbol]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSystemWaypointsResponse200
    """

    return (
        await asyncio_detailed(
            system_symbol=system_symbol,
            client=client,
            page=page,
            limit=limit,
            type_=type_,
            traits=traits,
        )
    ).parsed
