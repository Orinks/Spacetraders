import datetime
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.survey_size import SurveySize

if TYPE_CHECKING:
    from ..models.survey_deposit import SurveyDeposit


T = TypeVar("T", bound="Survey")


@_attrs_define
class Survey:
    """A resource survey of a waypoint, detailing a specific extraction location and the types of resources that can be
    found there.

        Attributes:
            signature (str): A unique signature for the location of this survey. This signature is verified when attempting
                an extraction using this survey.
            symbol (str): The symbol of the waypoint that this survey is for.
            deposits (list['SurveyDeposit']): A list of deposits that can be found at this location. A ship will extract one
                of these deposits when using this survey in an extraction request. If multiple deposits of the same type are
                present, the chance of extracting that deposit is increased.
            expiration (datetime.datetime): The date and time when the survey expires. After this date and time, the survey
                will no longer be available for extraction.
            size (SurveySize): The size of the deposit. This value indicates how much can be extracted from the survey
                before it is exhausted.
    """

    signature: str
    symbol: str
    deposits: list["SurveyDeposit"]
    expiration: datetime.datetime
    size: SurveySize
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        signature = self.signature

        symbol = self.symbol

        deposits = []
        for deposits_item_data in self.deposits:
            deposits_item = deposits_item_data.to_dict()
            deposits.append(deposits_item)

        expiration = self.expiration.isoformat()

        size = self.size.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "signature": signature,
                "symbol": symbol,
                "deposits": deposits,
                "expiration": expiration,
                "size": size,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.survey_deposit import SurveyDeposit

        d = src_dict.copy()
        signature = d.pop("signature")

        symbol = d.pop("symbol")

        deposits = []
        _deposits = d.pop("deposits")
        for deposits_item_data in _deposits:
            deposits_item = SurveyDeposit.from_dict(deposits_item_data)

            deposits.append(deposits_item)

        expiration = isoparse(d.pop("expiration"))

        size = SurveySize(d.pop("size"))

        survey = cls(
            signature=signature,
            symbol=symbol,
            deposits=deposits,
            expiration=expiration,
            size=size,
        )

        survey.additional_properties = d
        return survey

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
