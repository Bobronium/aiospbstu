import functools
import re
from typing import Union, List, Type, Optional

from pydantic import validator, create_model, Schema

from .base import BaseScheduleObject
from ..utils.string import snake_to_camel

__all__ = ['Method', "MethodTemplate"]


class Method(BaseScheduleObject):
    name: str
    endpoint: str
    params: dict
    expected_keys: Union[str, List[str], dict]

    use_base_site_url: bool = False

    def __str__(self):
        return self.endpoint

    @property
    @functools.lru_cache()
    def url(self):
        if self.use_base_site_url:
            return f'{self.api.BASE_URL}/{self.endpoint}'
        return f'{self.api.API_URL}/{self.endpoint}'


class MethodTemplate(BaseScheduleObject):
    endpoint_template: str
    expected_keys: Optional[Union[str, List[str], dict]] = Schema({})

    use_base_site_url: bool = False

    @property
    @functools.lru_cache()
    def name(self) -> str:
        return self._name.upper()

    @property
    @functools.lru_cache()
    def class_name(self) -> str:
        return snake_to_camel(self._name)

    @property
    @functools.lru_cache()
    def needed_params(self) -> List[str]:
        return re.findall(r'{(.*?)}', self.endpoint_template)

    @functools.lru_cache()
    def get_method(self, **kwargs) -> Method:
        for param in self.needed_params:
            if param not in kwargs:
                raise ValueError(f'Parameter "{param}" not found in "{kwargs}", needed params: {self.needed_params}')

        for k, v in kwargs.items():
            if k not in self.needed_params:
                raise ValueError(f'Unexpected parameter: "{k}={v}", allowed params: {self.needed_params}')
            elif v is None:
                raise ValueError(f'Parameter "{k}" is unfilled')

        endpoint = self.endpoint_template.format(**kwargs)
        # FIXME: Change pydantic.create_model rtype from BaseModel to Model TypeVar
        # noinspection PyTypeChecker
        method_class: Type[Method] = create_model(self.class_name, **self.expected_keys, **kwargs, __base__=Method)

        return method_class(name=self.name,
                            endpoint=endpoint,
                            expected_keys=self.expected_keys,
                            params=kwargs,
                            use_base_site_url=self.use_base_site_url)

    def __call__(self, **kwargs) -> Method:
        # FIXME: pydantic have problems with functools.lru_cache, so self is needed here
        # TODO: Figure out why this happens, create an issue on pydantic repo
        return self.get_method(self, **kwargs)

    def __set_name__(self, owner, name):
        self.__dict__.update(_name=name.lower())

    @validator('expected_keys', whole=True)
    def _make_keys_dict(cls, keys) -> dict:
        if isinstance(keys, str):
            return {f'{keys}_key': keys}
        elif isinstance(keys, dict):
            return keys
        return {f'{k}_key': k for k in keys}
