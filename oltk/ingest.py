import json
import logging
from os import path
from typing import Any, Dict, Optional

import requests

from oltk.const import AUTHORITY, CONFIG_PATH, GRAPH_ENDPOINT, NOT_FOUND, SCOPES

logger = logging.Logger("oltk.ingest")


def refresh_token(config_path: str) -> Optional[str]:
    """access_tokenを再発行する
    :param config_path: 設定ファイルの保存先
    :type config_path: str
    :return: 新しいtoken
    :rtype: access_token
    """

    url = path.join(AUTHORITY, "common/oauth2/v2.0/token")
    with open(CONFIG_PATH) as fh:
        credentials = json.load(fh)

    data = {
        "scope": " ".join(str(i) for i in SCOPES),
        "client_id": credentials["client_id"],
        "client_secret": credentials["client_secret"],
        "refresh_token": credentials["refresh_token"],
        "grant_type": "refresh_token",
    }

    response = requests.post(url, data)

    if response.ok:
        response = response.json()
        credentials.update(response)
        with open(config_path, "w") as fh:
            json.dump(credentials, fh)
        return response["access_token"]
    else:
        logger.error(f"Access Tokenを正常に再発行できませんでした")
        print(response.text)
        response.raise_for_status()


def ingest(
    token: str,
    endpoint: str,
    method: str = "GET",
    time_zone: str = "Asia/Tokyo",
    params: Dict[Any, Any] = None,
    data: Dict[Any, Any] = None,
) -> Optional[Dict[Any, Any]]:
    """情報を取得する
    """
    url = path.join(GRAPH_ENDPOINT, endpoint)

    headers = {
        "Authorization": f"Bearer {token}",
        "Prefer": f'outlook.timezone="{time_zone}"',
    }
    response = None
    if method == "GET":
        response = requests.get(url, headers=headers, params=params)
    elif method == "POST":
        response = requests.post(url, headers=headers, params=params, json=data)
    else:
        logger.error(f"{method=}は対応していない形式です")
        raise RuntimeError()
    if response.ok:
        return response.json()["value"]
    else:
        status = response.status_code
        if status == NOT_FOUND:
            logger.warning("一致する情報が見つかりませんでした")
            return {}
        else:
            logger.error(f"リクエストは無効です:{status=}")
            response.raise_for_status()