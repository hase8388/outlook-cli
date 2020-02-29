import json
from os import makedirs, path

import click

from oltk.const import CONFIG_PATH


def prompt_password(message: str, default: str = "") -> str:
    """ユーザーと対話的にパスワード入力
    :param message: [description]
    :type message: str
    :param default: [description], defaults to ""
    :type default: str, optional
    :return: [description]
    :rtype: str
    """

    input = click.prompt(
        message, hide_input=True, type=str, default=default, show_default=False
    )
    return input


@click.group()
def oltk():
    pass


@oltk.command()
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


def main():
    oltk()


if __name__ == "__main__":
    main()
