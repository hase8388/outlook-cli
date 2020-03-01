import json
from os import makedirs, path

import click

from otlk.const import CONFIG_PATH
from otlk.ingest import logger
from otlk.model import People, User


def prompt_password(message: str, default: str = "") -> str:
    """ユーザーと対話的にパスワード入力
    """

    input = click.prompt(
        message, hide_input=True, type=str, default=default, show_default=False
    )
    return input


@click.group()
def otlk():
    pass


@otlk.command()
def init():
    """認証情報の初期化
    """
    config_dict = {}
    config_dict["access_token"] = prompt_password("Access Tokenを入力してください")
    config_dict["client_id"] = prompt_password("Client Idを入力してください[省略可]", default="")
    config_dict["client_secret"] = prompt_password(
        "Client Secretを入力してください[省略可]", default=""
    )
    config_dict["refresh_token"] = prompt_password(
        "Refresh Tokenをを入力してください[省略可]", default=""
    )

    makedirs(path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as fh:
        json.dump(config_dict, fh)


@otlk.command()
def me():
    """自身のユーザー情報を表示します
    """
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
