import datetime
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Chart")


@_attrs_define
class Chart:
    """The chart of a system or waypoint, which makes the location visible to other agents.

    Attributes:
        waypoint_symbol (Union[Unset, str]): The symbol of the waypoint.
        submitted_by (Union[Unset, str]): The agent that submitted the chart for this waypoint.
        submitted_on (Union[Unset, datetime.datetime]): The time the chart for this waypoint was submitted.
    """

    waypoint_symbol: Union[Unset, str] = UNSET
    submitted_by: Union[Unset, str] = UNSET
    submitted_on: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        waypoint_symbol = self.waypoint_symbol

        submitted_by = self.submitted_by

        submitted_on: Union[Unset, str] = UNSET
        if not isinstance(self.submitted_on, Unset):
            submitted_on = self.submitted_on.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if waypoint_symbol is not UNSET:
            field_dict["waypointSymbol"] = waypoint_symbol
        if submitted_by is not UNSET:
            field_dict["submittedBy"] = submitted_by
        if submitted_on is not UNSET:
            field_dict["submittedOn"] = submitted_on

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        waypoint_symbol = d.pop("waypointSymbol", UNSET)

        submitted_by = d.pop("submittedBy", UNSET)

        _submitted_on = d.pop("submittedOn", UNSET)
        submitted_on: Union[Unset, datetime.datetime]
        if isinstance(_submitted_on, Unset):
            submitted_on = UNSET
        else:
            submitted_on = isoparse(_submitted_on)

        chart = cls(
            waypoint_symbol=waypoint_symbol,
            submitted_by=submitted_by,
            submitted_on=submitted_on,
        )

        chart.additional_properties = d
        return chart

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
