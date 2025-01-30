from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_survey_response_201 import CreateSurveyResponse201
from ...types import Response


def _get_kwargs(
    ship_symbol: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/my/ships/{ship_symbol}/survey",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[CreateSurveyResponse201]:
    if response.status_code == 201:
        response_201 = CreateSurveyResponse201.from_dict(response.json())

        return response_201
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[CreateSurveyResponse201]:
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
) -> Response[CreateSurveyResponse201]:
    """Create Survey

     Create surveys on a waypoint that can be extracted such as asteroid fields. A survey focuses on
    specific types of deposits from the extracted location. When ships extract using this survey, they
    are guaranteed to procure a high amount of one of the goods in the survey.

    In order to use a survey, send the entire survey details in the body of the extract request.

    Each survey may have multiple deposits, and if a symbol shows up more than once, that indicates a
    higher chance of extracting that resource.

    Your ship will enter a cooldown after surveying in which it is unable to perform certain actions.
    Surveys will eventually expire after a period of time or will be exhausted after being extracted
    several times based on the survey's size. Multiple ships can use the same survey for extraction.

    A ship must have the `Surveyor` mount installed in order to use this function.

    Args:
        ship_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateSurveyResponse201]
    """

    kwargs = _get_kwargs(
        ship_symbol=ship_symbol,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    ship_symbol: str,
    *,
    client: AuthenticatedClient,
) -> Optional[CreateSurveyResponse201]:
    """Create Survey

     Create surveys on a waypoint that can be extracted such as asteroid fields. A survey focuses on
    specific types of deposits from the extracted location. When ships extract using this survey, they
    are guaranteed to procure a high amount of one of the goods in the survey.

    In order to use a survey, send the entire survey details in the body of the extract request.

    Each survey may have multiple deposits, and if a symbol shows up more than once, that indicates a
    higher chance of extracting that resource.

    Your ship will enter a cooldown after surveying in which it is unable to perform certain actions.
    Surveys will eventually expire after a period of time or will be exhausted after being extracted
    several times based on the survey's size. Multiple ships can use the same survey for extraction.

    A ship must have the `Surveyor` mount installed in order to use this function.

    Args:
        ship_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateSurveyResponse201
    """

    return sync_detailed(
        ship_symbol=ship_symbol,
        client=client,
    ).parsed


async def asyncio_detailed(
    ship_symbol: str,
    *,
    client: AuthenticatedClient,
) -> Response[CreateSurveyResponse201]:
    """Create Survey

     Create surveys on a waypoint that can be extracted such as asteroid fields. A survey focuses on
    specific types of deposits from the extracted location. When ships extract using this survey, they
    are guaranteed to procure a high amount of one of the goods in the survey.

    In order to use a survey, send the entire survey details in the body of the extract request.

    Each survey may have multiple deposits, and if a symbol shows up more than once, that indicates a
    higher chance of extracting that resource.

    Your ship will enter a cooldown after surveying in which it is unable to perform certain actions.
    Surveys will eventually expire after a period of time or will be exhausted after being extracted
    several times based on the survey's size. Multiple ships can use the same survey for extraction.

    A ship must have the `Surveyor` mount installed in order to use this function.

    Args:
        ship_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateSurveyResponse201]
    """

    kwargs = _get_kwargs(
        ship_symbol=ship_symbol,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ship_symbol: str,
    *,
    client: AuthenticatedClient,
) -> Optional[CreateSurveyResponse201]:
    """Create Survey

     Create surveys on a waypoint that can be extracted such as asteroid fields. A survey focuses on
    specific types of deposits from the extracted location. When ships extract using this survey, they
    are guaranteed to procure a high amount of one of the goods in the survey.

    In order to use a survey, send the entire survey details in the body of the extract request.

    Each survey may have multiple deposits, and if a symbol shows up more than once, that indicates a
    higher chance of extracting that resource.

    Your ship will enter a cooldown after surveying in which it is unable to perform certain actions.
    Surveys will eventually expire after a period of time or will be exhausted after being extracted
    several times based on the survey's size. Multiple ships can use the same survey for extraction.

    A ship must have the `Surveyor` mount installed in order to use this function.

    Args:
        ship_symbol (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateSurveyResponse201
    """

    return (
        await asyncio_detailed(
            ship_symbol=ship_symbol,
            client=client,
        )
    ).parsed
