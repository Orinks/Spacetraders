from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_status_response_200_announcements_item import GetStatusResponse200AnnouncementsItem
    from ..models.get_status_response_200_leaderboards import GetStatusResponse200Leaderboards
    from ..models.get_status_response_200_links_item import GetStatusResponse200LinksItem
    from ..models.get_status_response_200_server_resets import GetStatusResponse200ServerResets
    from ..models.get_status_response_200_stats import GetStatusResponse200Stats


T = TypeVar("T", bound="GetStatusResponse200")


@_attrs_define
class GetStatusResponse200:
    """
    Attributes:
        status (str): The current status of the game server.
        version (str): The current version of the API.
        reset_date (str): The date when the game server was last reset.
        description (str):
        stats (GetStatusResponse200Stats):
        leaderboards (GetStatusResponse200Leaderboards):
        server_resets (GetStatusResponse200ServerResets):
        announcements (list['GetStatusResponse200AnnouncementsItem']):
        links (list['GetStatusResponse200LinksItem']):
    """

    status: str
    version: str
    reset_date: str
    description: str
    stats: "GetStatusResponse200Stats"
    leaderboards: "GetStatusResponse200Leaderboards"
    server_resets: "GetStatusResponse200ServerResets"
    announcements: list["GetStatusResponse200AnnouncementsItem"]
    links: list["GetStatusResponse200LinksItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        version = self.version

        reset_date = self.reset_date

        description = self.description

        stats = self.stats.to_dict()

        leaderboards = self.leaderboards.to_dict()

        server_resets = self.server_resets.to_dict()

        announcements = []
        for announcements_item_data in self.announcements:
            announcements_item = announcements_item_data.to_dict()
            announcements.append(announcements_item)

        links = []
        for links_item_data in self.links:
            links_item = links_item_data.to_dict()
            links.append(links_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "version": version,
                "resetDate": reset_date,
                "description": description,
                "stats": stats,
                "leaderboards": leaderboards,
                "serverResets": server_resets,
                "announcements": announcements,
                "links": links,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_status_response_200_announcements_item import GetStatusResponse200AnnouncementsItem
        from ..models.get_status_response_200_leaderboards import GetStatusResponse200Leaderboards
        from ..models.get_status_response_200_links_item import GetStatusResponse200LinksItem
        from ..models.get_status_response_200_server_resets import GetStatusResponse200ServerResets
        from ..models.get_status_response_200_stats import GetStatusResponse200Stats

        d = src_dict.copy()
        status = d.pop("status")

        version = d.pop("version")

        reset_date = d.pop("resetDate")

        description = d.pop("description")

        stats = GetStatusResponse200Stats.from_dict(d.pop("stats"))

        leaderboards = GetStatusResponse200Leaderboards.from_dict(d.pop("leaderboards"))

        server_resets = GetStatusResponse200ServerResets.from_dict(d.pop("serverResets"))

        announcements = []
        _announcements = d.pop("announcements")
        for announcements_item_data in _announcements:
            announcements_item = GetStatusResponse200AnnouncementsItem.from_dict(announcements_item_data)

            announcements.append(announcements_item)

        links = []
        _links = d.pop("links")
        for links_item_data in _links:
            links_item = GetStatusResponse200LinksItem.from_dict(links_item_data)

            links.append(links_item)

        get_status_response_200 = cls(
            status=status,
            version=version,
            reset_date=reset_date,
            description=description,
            stats=stats,
            leaderboards=leaderboards,
            server_resets=server_resets,
            announcements=announcements,
            links=links,
        )

        get_status_response_200.additional_properties = d
        return get_status_response_200

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
