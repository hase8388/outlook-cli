from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from os import path
from typing import ClassVar, Dict, List

import numpy
from pandas import DataFrame, Series, date_range, json_normalize, to_datetime

from otlk.const import CREDENTIAL_PATH, MINIMAL_TERM, UNLIMITED_NUM
from otlk.ingest import ingest, retry_when_invalid
from otlk.util import round_min_dt


@dataclass
class BaseModel:
    user_id: str
    base_endpoint: ClassVar[str]

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


@dataclass
class EmptyTerms(BaseModel):
    user_id: str
    attendees: List[str]
    start_datetime: datetime
    end_datetime: datetime
    interval_min: int
    base_endpoint: ClassVar[str] = "calendar/getschedule"

    def __post_init__(self):
        # 最小取得単位で丸める
        self.start_datetime = round_min_dt(self.start_datetime, MINIMAL_TERM)
        self.end_datetime = round_min_dt(self.end_datetime, MINIMAL_TERM)

    def request(self):
        data = {
            "schedules": self.attendees,
            "startTime": {
                "dateTime": self.start_datetime.isoformat(),
                "timeZone": "Asia/Tokyo",
            },
            "endTime": {
                "dateTime": self.end_datetime.isoformat(),
                "timeZone": "Asia/Tokyo",
            },
            # 最小取得単位で取得
            "availabilityViewInterval": MINIMAL_TERM,
        }

        return retry_when_invalid(
            CREDENTIAL_PATH,
            lambda access_token: ingest(
                access_token, endpoint=self.endpoint, method="POST", data=data
            ),
        )

    def as_dataframe(self):
        value = DataFrame(self.value)
        # 空いている時間帯にflagを追加
        data = DataFrame(
            list(value["availabilityView"].apply(lambda x: list(x)).values)
        ).T
        data.columns = value["scheduleId"]
        data["start_dt"] = date_range(
            self.start_datetime, self.end_datetime, freq=f"{MINIMAL_TERM}T"
        )[:-1]
        data["end_dt"] = data["start_dt"] + timedelta(minutes=MINIMAL_TERM)
        data["is_empty"] = (
            numpy.sum(data.loc[:, self.attendees].astype(int), axis=1) == 0
        )

        # 予定が連続して空いている場合、結合する
        rows = []
        start_dts = []
        for _, row in data.iterrows():
            if row["is_empty"]:
                start_dts.append(row["start_dt"])
            elif len(start_dts):
                rows.append([min(start_dts), row["start_dt"]])
                start_dts = []
            else:
                start_dts = []

        if len(start_dts):
            rows.append([min(start_dts), max(start_dts)])

        return DataFrame(rows, columns=["from", "to"])
