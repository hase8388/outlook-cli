from dataclasses import asdict, dataclass
from os import path
from typing import Any, Dict

from pandas import DataFrame, Series

from otlk.const import CONFIG_PATH
from otlk.ingest import ingest, retry_when_invalid


@dataclass
class User:
    id_: str = "me"

    @property
    def value(self) -> Dict:
        id_ = id_ if (id_ := self.id_) == "me" else f"users/{id_}"
        return retry_when_invalid(CONFIG_PATH, ingest, endpoint=id_)

    def as_dict(self) -> Dict:
        dict_ = asdict(self)
        dict_.update(self.value)
        return dict_

    def as_series(self) -> Series:
        data = Series(self.as_dict())
        data.name = self.id_
        return data
