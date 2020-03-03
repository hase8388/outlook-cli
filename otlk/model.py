from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from os import path
from typing import Any, ClassVar, Dict

from pandas import DataFrame, Series, json_normalize, to_datetime

from otlk.const import CREDENTIAL_PATH, UNLIMITED_NUM
from otlk.ingest import ingest, retry_when_invalid


@dataclass
class BaseModel:
    user_id: str
    base_endpoint: ClassVar[str] = ""

    @property
    def endpoint(self):
        user_id_ = user_id if (user_id := self.user_id) == "me" else f"users/{user_id}"

        return path.join(user_id_, self.base_endpoint)

    def request(self) -> Dict:
        raise NotImplementedError

    @property
    def value(self) -> Dict:
        # 正常に値を取得できた場合、valueの中にデータが入っているので、取り出す
        return self.request()["value"]

    def as_dict(self) -> Dict:
        dict_ = asdict(self)
        dict_.update(self.request())
        return dict_


@dataclass
class User(BaseModel):
    user_id: str = "me"
    base_endpoint: ClassVar[str] = ""

    def request(self) -> Dict:
        return retry_when_invalid(
            CREDENTIAL_PATH,
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

    def request(self) -> Dict:
        # デフォルトだと10件のみなので、全て取得する
        params = {"top": UNLIMITED_NUM}
        return retry_when_invalid(
            CREDENTIAL_PATH,
            lambda access_token: ingest(
                access_token, endpoint=self.endpoint, params=params
            ),
        )

    def as_dataframe(self) -> DataFrame:
        data = DataFrame(self.value)
        # アドレスはuser_idに統一
        data = data.rename(columns={"userPrincipalName": "user_id"})
        data = data.sort_values("user_id", ignore_index=True)
        return data


@dataclass
class Event(BaseModel):
    user_id: str
    start_datetime: datetime
    end_datetime: datetime
    base_endpoint: ClassVar[str] = "calendarView"

    def request(self):
        # デフォルトだと10件のみなので、全て取得する
        params = {
            "top": UNLIMITED_NUM,
            "startDateTime": self.start_datetime.isoformat(),
            "endDateTime": self.end_datetime.isoformat(),
        }
        return retry_when_invalid(
            CREDENTIAL_PATH,
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
        data = json_normalize(self.value).loc[:, columns]
        # キャンセル済みは削除
        data = data[~data["isCancelled"]].drop("isCancelled", axis=1)
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
