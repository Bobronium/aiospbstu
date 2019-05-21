import datetime
from typing import List, Optional, Union

from pydantic import Schema

from .base import StrScheduleObject, ObjectWithSchedule

__all__ = ['Building']


class Building(StrScheduleObject):
    building_id: int = Schema(None, alias='id')
    name: str
    abbr: str
    address: str
    rooms: Optional[List['Auditory']]

    _might_have_rooms: Optional[bool] = True

    async def get_auditories(self) -> List['Auditory']:
        return await self.api.get_building_auditories(self.building_id)


class Auditory(ObjectWithSchedule):
    auditory_id: int = Schema(None, alias='id')
    name: str
    building: Building

    async def get_schedule(self, date: Optional[Union[datetime.datetime, datetime.date]] = None):
        return await self.api.get_auditory_schedule(self.auditory_id, date)


Building.update_forward_refs()
