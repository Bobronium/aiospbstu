from pydantic import Schema

from .base import BaseScheduleObject

__all__ = ['Faculty']


class Faculty(BaseScheduleObject):
    faculty_id: int = Schema(None, alias='id')
    name: str
    abbr: str

    async def get_groups(self):
        return await self.api.get_faculty_groups(self.faculty_id)
