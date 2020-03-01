from datetime import datetime, timedelta

import click
from pandas import to_datetime

from otlk.const import TIME_FORMAT, TODAY
from otlk.ingest import logger
from otlk.model import Event, People, User


@click.group()
def otlk():
    pass


def prompt_password(input: str, default: str = None) -> str:
    """ユーザーと対話的にパスワード入力
    """

    input_ = click.prompt(
        text=input, hide_input=False, type=str, default=default, show_default=False
    )
    return input_


def _me():
    display_cols = [
        "id",
        "displayName",
        "mail",
        "mobilePhone",
        "officeLocation",
        "mobilePhone",
    ]
    me = User().as_series().loc[display_cols]
    click.echo(me.to_markdown())


@otlk.command()
def me():
    """自身のユーザー情報を表示します
    """
    _me()


@otlk.command()
@click.option("-d", "--domain", type=str, help="domain名でフィルタ")
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
    display_cols = ["displayName", "userPrincipalName", "companyName"]
    people = People()
    data = people.as_dataframe().loc[:, display_cols]
    # フィルタリング
    if domain:
        principals = data["userPrincipalName"].astype(str)
        data = data[principals.str.endswith(domain)]

    if format == "markdown":
        click.echo(data.to_markdown())
    elif format == "csv":
        click.echo(data.to_csv(index=True))
    else:
        logger.error("想定していない形式です")


@otlk.command()
@click.option("-a", "--address", default="me", type=str)
@click.option("-s", "--start", default=TODAY.strftime(TIME_FORMAT), type=str)
@click.option(
    "-e", "--end", default=(TODAY + timedelta(days=1)).strftime(TIME_FORMAT), type=str
)
@click.option("-d", "--is_detail", default=False, is_flag=True)
def event(address: str, start: str, end: str, is_detail: bool):
    """対象ユーザーのイベントを取得
    
    :param address: 対象ユーザーのアドレス
    :type address: str
    :param start: 対象時間(から)["%Y/%m/%d/ %H:%M"]
    :type start: から
    :param end: 対象時間(まで)["%Y/%m/%d/ %H:%M"]
    :type end: str
    :param is_detail: 詳細まで出力するか
    :type is_detail: book
    """
    event = Event(
        user_id=address,
        start_datetime=to_datetime(start),
        end_datetime=to_datetime(end),
    )
    summary_col = ["subject", "locations", "start.dateTime", "end.dateTime"]
    data = event.as_dataframe()
    data = data if is_detail else data.loc[:, summary_col]
    click.echo((data.to_markdown()))


def main():
    otlk()


if __name__ == "__main__":
    main()
