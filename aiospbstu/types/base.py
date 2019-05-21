import abc
import datetime
import functools
from typing import Optional, Union, TypeVar

from pydantic import BaseModel

__all__ = ['BaseScheduleObject', 'StrScheduleObject', 'ObjectWithSchedule']

UniScheduleModel = TypeVar('UniScheduleModel', bound='BaseScheduleObject')


class BaseScheduleObject(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    @property
    @functools.lru_cache()
    def api(self):
        """
        :rtype: aiospbstu.api.PolyScheduleAPI
        """
        from .. import PolyScheduleAPI
        api = PolyScheduleAPI.get_current()
        if api is None:
            raise RuntimeError("Can't get api instance from context. "
                               "You can fix it with setting current instance: "
                               "'PolyScheduleAPI.set_current(api_instance)'")
        return api

    @property
    def skip_exceptions(self):
        return self.api.skip_exceptions

    @property
    @functools.lru_cache()
    def identity(self):
        obj = self.__class__.__name__.lower()
        if hasattr(self, f'{obj}_id'):
            return getattr(self, f'{obj}_id')

    def __hash__(self):
        def _hash(obj):
            buf = 0
            if isinstance(obj, list):
                for item in obj:
                    buf += _hash(item)
            elif isinstance(obj, dict):
                for dict_key, dict_value in obj.items():
                    buf += hash(dict_key) + _hash(dict_value)
            else:
                try:
                    buf += hash(obj)
                except TypeError:  # Skip unhashable objects
                    pass
            return buf

        result = 0
        for key, value in sorted(self.fields.items()):
            result += hash(key) + _hash(value)

        return result


class StrScheduleObject(BaseScheduleObject):

    def __str__(self):
        if hasattr(self, 'full_name'):
            return self.full_name
        if hasattr(self, 'subject_short'):
            return self.subject
        return self.name or super().__str__()


class ObjectWithSchedule(BaseScheduleObject, abc.ABC):

    async def get_schedule(self, date: Optional[Union[datetime.datetime, datetime.date]] = None):
        pass
