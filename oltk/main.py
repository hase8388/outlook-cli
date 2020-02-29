import json
from os import makedirs, path

import click

from oltk.const import CONFIG_PATH


@click.group()
def oltk():
    pass


@oltk.command()
def init():
    """認証情報の初期化
    """
    config_dict = {}
    config_dict["access_token"] = click.prompt(
        "Access Tokenを入力してください", hide_input=True, type=str
    )
    config_dict["client_id"] = click.prompt(
        "Client Idを入力してください[省略可]",
        hide_input=True,
        type=str,
        default="",
        show_default=False,
    )
    config_dict["client_secret"] = click.prompt(
        "Client Secretを入力してください[省略可]",
        hide_input=True,
        type=str,
        default="",
        show_default=False,
    )
    makedirs(path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as fh:
        json.dump(config_dict, fh)


def main():
    oltk()


if __name__ == "__main__":
    main()
