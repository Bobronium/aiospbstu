from enum import IntEnum
from typing import Optional, List

from pydantic import Schema

from .base import ObjectWithSchedule, AnyDate
from .faculty import Faculty
from ..utils.strenum import StrEnum

__all__ = ['Group', 'GroupType', 'GroupKind', 'GroupLevel']


class GroupType(StrEnum):
    common = 'common'
    evening = 'evening'
    distance = 'distance'


class GroupKind(IntEnum):
    baccalaureate = 0
    magistracy = 1
    specialty = 2
    secondary = 6
    unknown = 3


class GroupLevel(IntEnum):
    first_grade = 1
    second_grade = 2
    third_grade = 3
    fourth_grade = 4
    fifth_grade = 5
    sixth_grade = 6


class Group(ObjectWithSchedule):
    id: int
    name: str
    level: GroupLevel
    group_type: str = Schema(None, alias='type')
    kind: GroupKind
    spec: str
    faculty: Faculty

    async def get_schedule(self, date: Optional[AnyDate] = None):
        return await self.api.get_group_schedule(self.id, date)

    @classmethod
    async def search(cls, name: str) -> List['Group']:
        return await cls.api.search_group(teacher_name=name)
