import datetime
from enum import Enum, IntEnum
from typing import Optional, Union

from pydantic import Schema

from .base import ObjectWithSchedule
from .faculty import Faculty

__all__ = ['Group', 'GroupType', 'GroupKind', 'GroupLevel']


class GroupType(str, Enum):
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
    group_id: int = Schema(None, alias='id')
    name: str
    level: GroupLevel
    group_type: str = Schema(None, alias='type')
    kind: GroupKind
    spec: str
    faculty: Faculty

    async def get_schedule(self, date: Optional[Union[datetime.datetime, datetime.date]] = None):
        return await self.api.get_group_schedule(self.group_id, date)
