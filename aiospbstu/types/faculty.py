from typing import Optional, List, TYPE_CHECKING

from pydantic import Schema

from .base import BaseScheduleObject

__all__ = ['Faculty']

if TYPE_CHECKING:
    from aiospbstu.types import Group


class Faculty(BaseScheduleObject):
    id: int = Schema(None, alias='id')
    name: str
    abbr: str
    groups: Optional[List['Group']]

    async def get_groups(self):
        if not self.groups:
            self.groups = await self.api.get_faculty_groups(self.id)
        return self.groups
