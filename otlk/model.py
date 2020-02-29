from dataclasses import asdict, dataclass
from os import path
from typing import Any, ClassVar, Dict

from pandas import DataFrame, Series, json_normalize

from otlk.const import CONFIG_PATH, UNLIMITED_NUM
from otlk.ingest import ingest, retry_when_invalid


@dataclass
class BaseModel:
    base_endpoint: ClassVar[str] = ""
    id_: str = "me"

    @property
    def endpoint(self):
        id_ = id_ if (id_ := self.id_) == "me" else f"users/{id_}"
        return path.join(id_, self.base_endpoint)

    @property
    def value(self) -> Dict:
        raise NotImplementedError

    def as_dict(self) -> Dict:
        dict_ = asdict(self)
        dict_.update(self.value)
        return dict_


class User(BaseModel):
    base_endpoint = ""

    @property
    def value(self) -> Dict:
        return retry_when_invalid(
            CONFIG_PATH,
            lambda access_token: ingest(access_token, endpoint=self.endpoint),
        )

    def as_series(self) -> Series:
        data = Series(self.as_dict())
        data.name = self.id_
        return data


class People(BaseModel):
    base_endpoint = "people"

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
