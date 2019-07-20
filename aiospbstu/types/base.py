import abc
import datetime
from typing import Optional, Union, TypeVar, TYPE_CHECKING

import pydantic
from pydantic import BaseModel

__all__ = [
    'AnyDate',
    'BaseScheduleObject',
    'StrScheduleObject',
    'ObjectWithSchedule',
    'cached_property',
    'cached_class_property'
]

UniScheduleModel = TypeVar('UniScheduleModel', bound='BaseScheduleObject')
AnyDate = Union[str, datetime.datetime, datetime.date]

if TYPE_CHECKING:
    from .. import PolyScheduleAPI


class _Missing:
    pass


class _CachedProperty:
    __slots__ = 'getter', '_cached'

    def __init__(self, getter):
        self.getter = getter
        self._cached = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self
        instance_id = id(instance)
        cached = self._cached.get(instance_id, _Missing)
        if cached is _Missing:
            cached = self._cached[instance_id] = self.getter(instance)
        return cached


class _CachedClassProperty:
    __slots__ = 'getter', '_cached'

    def __init__(self, getter):
        self.getter = getter
        self._cached = None

    def __get__(self, instance, owner):
        if self._cached is None:
            self._cached = self.getter(owner)
        return self._cached


cached_property = _CachedProperty
cached_class_property = _CachedClassProperty


def patch_pydantic():
    # We need it until this gets released: https://github.com/samuelcolvin/pydantic/pull/679
    pydantic.main.TYPE_BLACKLIST = pydantic.main.TYPE_BLACKLIST + (cached_class_property, cached_property)


patch_pydantic()


class BaseScheduleObject(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    @cached_class_property
    def api(self) -> 'PolyScheduleAPI':
        from .. import PolyScheduleAPI
        api = PolyScheduleAPI.get_current()
        if api is None:
            raise RuntimeError("Can't get api instance from context. "
                               "You can fix it with setting current instance: "
                               "'PolyScheduleAPI.set_current(api_instance)'")
        return api

    @cached_class_property
    def skip_exceptions(self):
        return self.api.skip_exceptions


class StrScheduleObject(BaseScheduleObject):
    _str = 'name'

    def __str__(self):
        return getattr(self, self._str, super().__str__())


class ObjectWithSchedule(BaseScheduleObject, abc.ABC):

    @abc.abstractmethod
    async def get_schedule(self, date: Optional[AnyDate] = None):
        ...
