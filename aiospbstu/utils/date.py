import datetime
from typing import Union


def iso_date(date: Union[datetime.datetime, datetime.date, None]) -> datetime.date:
    if date is None:
        return datetime.datetime.now().date()
    if isinstance(date, datetime.datetime):
        return date.date()
    elif isinstance(date, datetime.date):
        return date
    else:
        raise ValueError(f'Object {date} ({type(date)}) is not an instance of datetime.datetime or datetime.date')
