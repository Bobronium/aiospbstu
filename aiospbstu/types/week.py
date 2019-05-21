import datetime

from pydantic import validator

from .base import BaseScheduleObject

__all__ = ['Week']


class Week(BaseScheduleObject):
    date_start: datetime.date
    date_end: datetime.date
    is_odd: bool

    @validator('date_start', pre=True)
    def _set_proper_start_date(cls, v: str):
        return v.replace('.', '-')

    @validator('date_end', pre=True)
    def _set_proper_end_date(cls, v: str):
        return v.replace('.', '-')
