from datetime import datetime
from os import environ, getenv, path

HOME_PATH = environ["HOME"]
DEFAULT_CREDENTIAL_PATH = path.join(HOME_PATH, ".config", "otlk", "credential.json")
CREDENTIAL_PATH = (
    path if (path := getenv("OTLK_CREDENTIAL")) else DEFAULT_CREDENTIAL_PATH
)

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

TODAY = datetime.now()
TIME_FORMAT = "%Y/%m/%d/ %H:%M"
