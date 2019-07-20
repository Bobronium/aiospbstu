import re
from typing import Union, List, Optional, Dict, Tuple
from urllib.parse import urlencode

from pydantic import validator

from .base import BaseScheduleObject, cached_property
from ..utils.case import to_snake

__all__ = ['Method', ]


class Method(BaseScheduleObject):
    name: str = None
    endpoint: str = None
    endpoint_template: str = None
    expected_keys: Union[str, Dict[str, str]] = {}
    no_data_on_success: bool = False
    url_params_allowed: bool = False
    on_api_error: Optional[type]

    @cached_property
    def needed_endpoint_params(self) -> List[str]:
        if self.endpoint_template:
            return re.findall(r'{(.*?)}', self.endpoint_template)
        return []

    def get_url(self, base_url: str, params: dict = None) -> str:
        endpoint_params, url_params = self._filter_params(params)
        endpoint = self._get_endpoint(endpoint_params)

        url = base_url + endpoint

        if url_params:
            url += f'?{urlencode(params)}'
        return url

    def _get_endpoint(self, endpoint_params=None) -> str:
        if self.endpoint:
            return self.endpoint
        elif not self.endpoint_template:
            raise RuntimeError(f'Both self.endpoint and self.endpoint_template can not not be empty')
        elif not self.needed_endpoint_params:
            raise RuntimeError(f'Params to fill not found in endpoint_template: {self.endpoint_template}')
        elif not endpoint_params:
            raise ValueError(f'endpoint_params can not be empty on method {self.name}')

        return self.endpoint_template.format(**endpoint_params)

    def _filter_params(self, params: dict) -> Tuple[dict, dict]:
        params = params or {}
        endpoint_params = {}
        url_params = {}
        for k, v in params.items():
            if v is None:
                raise ValueError(f'Parameter "{k}" is unfilled')

            if k in self.needed_endpoint_params:
                endpoint_params[k] = v
            elif self.url_params_allowed or not self.needed_endpoint_params:
                url_params[k] = v
            else:
                raise ValueError(f'Unexpected parameter: "{k}={v}", allowed params: {self.needed_endpoint_params}')

        unfilled_param = next((param for param in self.needed_endpoint_params if param not in endpoint_params), None)
        if unfilled_param is not None:
            raise ValueError(f'Parameter "{unfilled_param}" not found in "{endpoint_params}",'
                             f' needed params: {self.needed_endpoint_params}')

        return endpoint_params, url_params

    def __set_name__(self, owner, name):
        try:
            self.name = name
        except Exception as e:
            print(e)

    def __str__(self):
        return f'{self.name}: {self.endpoint or self.endpoint_template}'

    def __getattr__(self, item):
        try:
            return BaseScheduleObject.__getattr__(self, item)
        except AttributeError as e:
            try:
                return self.expected_keys[item]
            except (KeyError, TypeError):
                raise e

    @validator('expected_keys', whole=True, pre=True)
    def _make_keys_dict(cls, keys) -> dict:
        if isinstance(keys, str):
            return {f'{to_snake(keys)}_key': keys}
        elif isinstance(keys, dict):
            return to_snake(keys)
        return {f'{to_snake(k)}_key': k for k in keys}
