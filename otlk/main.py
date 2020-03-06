import logging
from datetime import datetime, timedelta
from os import makedirs
from os.path import dirname, exists, join

import click
from pandas import to_datetime
from requests import HTTPError
from yaml import safe_load

from otlk.const import CONFIG_DIR, CONFIG_PATH, LOG_FORMAT, NOW, TIME_FORMAT, TODAY
from otlk.model import EmptyTerms, Event, People, User

logger = logging.getLogger(__name__)

config = {}
if exists(CONFIG_PATH):
    with open(CONFIG_PATH) as fh:
        config = config if (config := safe_load(fh)) else {}


def _add_domain(user_id: str):
    domain = domain if (domain := config.get("domain")) else ""
    user_id = user_id if ("@" in user_id or user_id == "me") else user_id + "@" + domain
    return user_id


@click.group()
def otlk():
    pass


def _me():
    display_cols = [
        "id",
        "displayName",
        "user_id",
        "mobilePhone",
        "officeLocation",
        "mobilePhone",
    ]
    me = User().as_series().loc[display_cols]
    click.echo(me.to_markdown())


@otlk.command()
def me():
    """自身のユーザー情報を表示
    """
    _me()


@otlk.command()
@click.option("-d", "--domain", type=str, help="user_idのdomain名でフィルタ")
@click.option(
    "-f",
    "--format",
    type=click.Choice(["markdown", "csv"]),
    default="markdown",
    help="出力形式",
)
def people(domain: str, format: str):
    """ユーザー一覧をを表示
    """
    display_cols = ["displayName", "user_id", "companyName"]
    people = People()
    data = people.as_dataframe().loc[:, display_cols]
    # フィルタリング
    if domain:
        user_ids = data["user_id"].astype(str)
        data = data[user_ids.str.endswith(domain)]

    if format == "markdown":
        click.echo(data.to_markdown())
    elif format == "csv":
        click.echo(data.to_csv(index=True))
    else:
        logger.error("想定していない形式です")


@otlk.command()
@click.argument("user_id", default="me", type=str)
@click.option(
    "-s",
    "--start",
    default=TODAY.strftime(TIME_FORMAT),
    type=str,
    help=f"対象時間(から)[{TIME_FORMAT}]",
)
@click.option(
    "-e",
    "--end",
    default=(TODAY + timedelta(days=1)).strftime(TIME_FORMAT),
    type=str,
    help=f"対象時間(まで)[{TIME_FORMAT}]",
)
@click.option("-d", "--is_detail", default=False, is_flag=True)
def event(user_id: str, start: str, end: str, is_detail: bool):
    """対象ユーザーのイベントを取得
    
    """
    event = Event(
        user_id=_add_domain(user_id),
        start_datetime=to_datetime(start),
        end_datetime=to_datetime(end),
    )
    summary_col = ["subject", "locations", "start.dateTime", "end.dateTime"]
    data = event.as_dataframe()
    data = data if is_detail else data.loc[:, summary_col]
    click.echo((data.to_markdown()))


@otlk.command()
@click.argument("user_ids", type=str, required=True, nargs=-1)
@click.option(
    "-s",
    "--start",
    default=NOW.strftime(TIME_FORMAT),
    type=str,
    help=f"対象時間(から)[{TIME_FORMAT}]",
)
@click.option(
    "-e",
    "--end",
    default=(NOW + timedelta(days=3)).strftime(TIME_FORMAT),
    type=str,
    help=f"対象時間(まで)[{TIME_FORMAT}]",
)
@click.option("-m", "--minutes", default=30, type=int, help="確保したい空き時間[m]")
def empty(user_ids, start, end, minutes):
    """対象ユーザー同士での共通した空き時間を取得
    
    """
    user_ids = [_add_domain(user_id) for user_id in user_ids]
    start = to_datetime(start)
    end = to_datetime(end)
    data = EmptyTerms(
        "me",
        attendees=user_ids,
        start_datetime=start,
        end_datetime=end,
        interval_min=minutes,
    ).as_dataframe()
    # to_mark_down時にunixtimeに変換されてしまうため、strに変換
    data["from"] = data["from"].dt.strftime(TIME_FORMAT)
    data["to"] = data["to"].dt.strftime(TIME_FORMAT)
    click.echo(data.to_markdown())


def main():
    makedirs(CONFIG_DIR, exist_ok=True)
    fh = logging.FileHandler(join(CONFIG_DIR, "otlk.log"))
    logging.basicConfig(format=LOG_FORMAT, handlers=[fh], level=logging.INFO)

    try:
        otlk()
    except KeyError as e:
        logger.error(e, exc_info=True)
        click.echo("指定された情報はありませんでした", err=True)

    except HTTPError as e:
        logger.error(e, exc_info=True)
        click.echo("情報の取得に失敗しました", err=True)


if __name__ == "__main__":
    main()
