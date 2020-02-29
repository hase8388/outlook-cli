import json
from os import makedirs, path

import click

from otlk.const import CONFIG_PATH
from otlk.model import User


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


def main():
    otlk()


if __name__ == "__main__":
    main()
