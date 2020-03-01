from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from os import path
from typing import Any, ClassVar, Dict

from pandas import DataFrame, Series, json_normalize, to_datetime

from otlk.const import CONFIG_PATH, UNLIMITED_NUM
from otlk.ingest import ingest, retry_when_invalid


@dataclass
class BaseModel:
    user_id: str
    base_endpoint: ClassVar[str] = ""

    @property
    def endpoint(self):
        user_id_ = user_id if (user_id := self.user_id) == "me" else f"users/{user_id}"

        return path.join(user_id_, self.base_endpoint)

    @property
    def value(self) -> Dict:
        raise NotImplementedError

    def as_dict(self) -> Dict:
        dict_ = asdict(self)
        dict_.update(self.value)
        return dict_


@dataclass
class User(BaseModel):
    user_id: str = "me"
    base_endpoint: ClassVar[str] = ""

    @property
    def value(self) -> Dict:
        return retry_when_invalid(
            CONFIG_PATH,
            lambda access_token: ingest(access_token, endpoint=self.endpoint),
        )

    def as_series(self) -> Series:
        data = Series(self.as_dict())
        data.name = self.user_id
        return data


@dataclass
class People(BaseModel):
    user_id: str = "me"
    base_endpoint: ClassVar[str] = "people"

    @property
    def value(self) -> Dict:
        # デフォルトだと10件のみなので、全て取得する
        params = {"top": UNLIMITED_NUM}
        return retry_when_invalid(
            CONFIG_PATH,
            lambda access_token: ingest(
                access_token, endpoint=self.endpoint, params=params
            ),
        )

    def as_dataframe(self) -> DataFrame:
        data = DataFrame(self.value["value"])
        data = data.sort_values("surname")
        data = data.set_index("id")
        return data


@dataclass
class Event(BaseModel):
    user_id: str
    start_datetime: datetime
    end_datetime: datetime
    base_endpoint: ClassVar[str] = "calendarView"

    @property
    def value(self):
        # デフォルトだと10件のみなので、全て取得する
        params = {
            "top": UNLIMITED_NUM,
            "startDateTime": self.start_datetime.isoformat(),
            "endDateTime": self.end_datetime.isoformat(),
        }
        return retry_when_invalid(
            CONFIG_PATH,
            lambda access_token: ingest(
                access_token, endpoint=self.endpoint, params=params
            ),
        )

    def as_dataframe(self):
        columns = [
            "subject",
            "isAllDay",
            "isCancelled",
            "isOrganizer",
            "type",
            "webLink",
            "onlineMeetingUrl",
            "locations",
            "attendees",
            "start.dateTime",
            "end.dateTime",
            "organizer.emailAddress.name",
        ]
        data = json_normalize(self.value["value"]).loc[:, columns]
        # 見やすいように整形
        data["start.dateTime"] = to_datetime(data["start.dateTime"])
        data["end.dateTime"] = to_datetime(data["end.dateTime"])
        data["locations"] = data["locations"].map(
            lambda x: [x["displayName"] for x in x]
        )
        data["attendees"] = data["attendees"].map(
            lambda x: [x["emailAddress"]["name"] for x in x]
        )

        data = data.sort_values("start.dateTime", ignore_index=True)
        return data
