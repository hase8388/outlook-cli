from datetime import datetime


def round_min_dt(dt: datetime, round_min: int):
    rounded = datetime(
        dt.year, dt.month, dt.day, dt.hour, (dt.minute // round_min) * round_min
    )
    return rounded
