from typing import Optional, List

from .base import StrScheduleObject, AnyDate

__all__ = ['Teacher']


class Teacher(StrScheduleObject):
    id: int
    oid: int
    full_name: str
    first_name: str
    middle_name: str
    last_name: str
    grade: str
    chair: str

    _str = 'full_name'

    async def get_schedule(self, date: Optional[AnyDate] = None):
        return await self.api.get_teacher_schedule(self.id, date)

    @classmethod
    async def search(cls, name: str) -> List['Teacher']:
        return await cls.api.search_teacher(teacher_name=name)
