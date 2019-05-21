import datetime
from typing import Optional, Union

from pydantic import Schema

from .base import StrScheduleObject

__all__ = ['Teacher']


class Teacher(StrScheduleObject):
    teacher_id: int = Schema(None, alias='id')
    oid: int
    full_name: str
    first_name: str
    middle_name: str
    last_name: str
    grade: str
    chair: str

    async def get_schedule(self, date: Optional[Union[datetime.datetime, datetime.date]] = None):
        return await self.api.get_teacher_schedule(self.teacher_id, date)
