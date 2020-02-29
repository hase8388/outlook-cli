from os import environ, path

HOME_PATH = environ["HOME"]
CONFIG_PATH = path.join(HOME_PATH, ".config", "oltk", "config.json")
