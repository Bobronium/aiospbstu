from typing import List, Optional

from pydantic import Schema

from .base import StrScheduleObject, ObjectWithSchedule, AnyDate

__all__ = ['Building']


class Building(StrScheduleObject):
    id: int
    name: str
    abbr: str
    address: str
    rooms: Optional[List['Auditory']]

    async def get_auditories(self) -> List['Auditory']:
        if not self.rooms:
            self.rooms = await self.api.get_building_auditories(self.id)
        return self.rooms


class Auditory(ObjectWithSchedule):
    auditory_id: int = Schema(None, alias='id')
    name: str
    building: Building

    async def get_schedule(self, date: Optional[AnyDate] = None):
        return await self.api.get_auditory_schedule(self.auditory_id, date)


Building.update_forward_refs()
