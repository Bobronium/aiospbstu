from typing import List, Optional

from pydantic import Schema

from .auditory import Auditory
from .base import BaseScheduleObject, AnyDate, cached_property
from .day import Day
from .group import Group
from .teacher import Teacher
from .week import Week

__all__ = ['Schedule']


class Schedule(BaseScheduleObject):
    week: Week
    days: List[Day]
    group: Optional[Group]
    teacher: Optional[Teacher]
    auditory: Optional[Auditory] = Schema(None, alias='room')

    @classmethod
    async def get(cls, group_id=None, teacher_id=None, auditory_id=None, date: Optional[AnyDate] = None):
        kind = 'group' if group_id else 'teacher' if teacher_id else 'auditory'

        method = getattr(cls.api, f'get_{kind}_schedule')
        return await method(group_id or teacher_id or auditory_id, date)

    async def search_day(self,
                         date: Optional[AnyDate] = None,
                         weekday: Optional[int] = None,
                         find_next: Optional[bool] = False,
                         find_prev: Optional[bool] = False) -> Optional[Day]:

        days = reversed(self.days) if find_prev else self.days

        find_by_attr = 'date' if date else 'weekday'
        find_by_value = date or weekday

        for day in days:
            day_value = getattr(day, find_by_attr)
            if (day_value == find_by_value
                    or find_next and day_value > find_by_value
                    or find_prev and day_value < find_by_value):
                return day
        return None

    @property
    def first_day(self):
        if self.days:
            return self.days[0]

    @property
    def last_day(self):
        if self.days:
            return self.days[-1]

    @property
    def days_count(self):
        return len(self.days)

    @cached_property
    def site_url(self):
        method = getattr(self.api.methods, f"SITE_{self.owner_type.upper()}_SCHEDULE")
        params = {f'{self.owner_type}_id': self.owner.id, 'date': self.week.date_start}
        return method.get_url(base_url=self.api.BASE_URL, params=params)

    @cached_property
    def ical_url(self):
        if self.owner_type in ('group', 'teacher'):
            return self.site_url.replace('?date=', '/ical?date=')

    @cached_property
    def owner_type(self):
        return self.owner.__class__.__name__.lower()

    @cached_property
    def owner(self):
        return self.group or self.teacher or self.auditory

    def __iter__(self) -> Day:
        for day in self.days:
            yield day
