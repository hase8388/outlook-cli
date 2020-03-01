from os import environ, path

HOME_PATH = environ["HOME"]
DEFAULT_CONFIG_PATH = path.join(HOME_PATH, ".config", "otlk", "config.json")
CONFIG_PATH = path if (path := environ["OTLK_CONFIG"]) else DEFAULT_CONFIG_PATH

AUTHORITY = "https://login.microsoftonline.com"
GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0/"
SCOPES = [
    "openid",
    "offline_access",
    "User.Read",
    "Calendars.Read",
    "Calendars.Read.Shared",
    "People.Read",
]

BAD_REQUEST = 400
UNAUTHORIZED = 401
FORBIDDEN = 403
NOT_FOUND = 404

UNLIMITED_NUM = 1000
