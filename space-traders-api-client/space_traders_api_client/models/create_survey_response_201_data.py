from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.cooldown import Cooldown
    from ..models.survey import Survey


T = TypeVar("T", bound="CreateSurveyResponse201Data")


@_attrs_define
class CreateSurveyResponse201Data:
    """
    Attributes:
        cooldown (Cooldown): A cooldown is a period of time in which a ship cannot perform certain actions.
        surveys (list['Survey']): Surveys created by this action.
    """

    cooldown: "Cooldown"
    surveys: list["Survey"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cooldown = self.cooldown.to_dict()

        surveys = []
        for surveys_item_data in self.surveys:
            surveys_item = surveys_item_data.to_dict()
            surveys.append(surveys_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cooldown": cooldown,
                "surveys": surveys,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.cooldown import Cooldown
        from ..models.survey import Survey

        d = src_dict.copy()
        cooldown = Cooldown.from_dict(d.pop("cooldown"))

        surveys = []
        _surveys = d.pop("surveys")
        for surveys_item_data in _surveys:
            surveys_item = Survey.from_dict(surveys_item_data)

            surveys.append(surveys_item)

        create_survey_response_201_data = cls(
            cooldown=cooldown,
            surveys=surveys,
        )

        create_survey_response_201_data.additional_properties = d
        return create_survey_response_201_data

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
