import logging
from logging import error
from typing import Callable

import click
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)


def convert_std_error(func: Callable):
    """生じたエラーを標準エラー出力に変換
    
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            logger.error(e, exc_info=True)
            click.echo("指定された情報はありませんでした", err=True)

        except HTTPError as e:
            logger.error(e, exc_info=True)
            click.echo("情報の取得に失敗しました", err=True)

    return wrapper
