import json
from os import makedirs, path

import click
from requests.exceptions import HTTPError

from otlk.const import CONFIG_PATH
from otlk.ingest import logger
from otlk.model import People, User


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


def main():
    otlk()


if __name__ == "__main__":
    main()
