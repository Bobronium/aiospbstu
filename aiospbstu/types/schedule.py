import datetime
import functools
from typing import List, Union, Optional

from pydantic import Schema

from .auditory import Auditory
from .base import BaseScheduleObject
from .day import Day
from .group import Group
from .teacher import Teacher
from .week import Week
from .. import exceptions
from ..utils.error_handler import handle_exceptions

__all__ = ['Schedule']


class Schedule(BaseScheduleObject):
    week: Week
    days: List[Day]
    group: Optional[Group]
    teacher: Optional[Teacher]
    auditory: Optional[Auditory] = Schema(None, alias='room')

    @handle_exceptions
    async def get_day(self,
                      date: Optional[Union[datetime.datetime, datetime.date]] = None,
                      weekday: Optional[int] = None,
                      find_next: Optional[bool] = False,
                      find_prev: Optional[bool] = False) -> Day:

        days = reversed(self.days) if find_prev else self.days

        find_by_attr = 'date' if date else 'weekday'
        find_by_value = date or weekday

        for day in days:
            day_value = getattr(day, find_by_attr)
            if (day_value == find_by_value
                    or find_next and day_value > find_by_value
                    or find_prev and day_value < find_by_value):
                return day

        raise exceptions.DayNotFoundByDate(
            f'Day with {"date" if date else "weekday"}: "{date or weekday}" not found in {self}'
        )

    @property
    def first_day(self):
        if self.days:
            return self.days[0]

    @property
    def last_day(self):
        if self.days:
            return self.days[-1]

    @property
    @functools.lru_cache()
    def days_count(self):
        return len(self.days)

    @property
    @functools.lru_cache()
    def site_url(self):
        method = getattr(self.api.methods, f"SITE_{self.owner_type.upper()}_SCHEDULE")
        params = {f'{self.owner_type}_id': self.owner.identity, 'date': self.week.date_start}
        return method(**params).url

    @property
    @functools.lru_cache()
    def ical_url(self):
        if self.owner_type in ('group', 'teacher'):
            return self.site_url.replace('?date=', '/ical?date=')

    @property
    @functools.lru_cache()
    def owner_type(self):
        return self.owner.__class__.__name__.lower()

    @property
    @functools.lru_cache()
    def owner(self):
        if self.group:
            return self.group
        elif self.teacher:
            return self.teacher
        elif self.auditory:
            return self.auditory

    def __iter__(self) -> Day:
        for day in self.days:
            yield day
