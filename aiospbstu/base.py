import asyncio
import logging
import ssl
from http import HTTPStatus
from typing import Optional, Type, Union

import aiohttp
import certifi

from . import exceptions as exc
from .types.method import Method
from .utils import json
from .utils.mixins import ContextInstanceMixin

log = logging.getLogger('aiospbstu')


class BaseScheduleApi(ContextInstanceMixin):
    BASE_URL, API_ENDPOINT = 'https://ruz.spbstu.ru', '/api/v1/ruz'
    API_URL = BASE_URL + API_ENDPOINT

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context, loop=self.loop)
        self.session = aiohttp.ClientSession(connector=connector, loop=self.loop, json_serialize=json.dumps)

        self.set_current(self)

    async def request(
            self, method: Method,
            on_api_error_exception: Optional[Type[Exception]] = exc.ApiResponseError) -> Optional[Union[dict, list]]:
        """
        Base method to get response from API

        :param on_api_error_exception: Exceptions to raise if '{"error": True}' is in API response
        :param method: Method class instance with url and expected_keys attrs

        :raises ApiError, NetworkError
        """
        url = method.url
        log.debug('Make request: "%s"' % url)

        try:
            async with self.session.get(url) as response:
                body = await response.text()
        except aiohttp.ClientError as e:
            raise exc.NetworkError(url=url, cause=e)

        log.debug('Response for "%s": [%d] "%r"', url, response.status, body)

        if response.content_type != 'application/json':
            raise exc.ResponseTypeError(url=url, response=body)

        try:
            result_json = json.loads(body)
        except ValueError as e:
            raise exc.JSONDecodeError(url=url, response=body, cause=e)

        if result_json.get('error', False):
            error_text = result_json.get("text", None)
            expected_text = getattr(on_api_error_exception, 'expected_text', None)
            error_message = f'Api returned error: {error_text}'
            if not expected_text or (error_text and expected_text in error_text):
                raise on_api_error_exception(error_text, url=url, response=result_json)
            elif error_text and exc.ApiInternalError.expected_text in error_text:
                raise exc.ApiInternalError(error_message, url=url, response=result_json)

            raise exc.ApiResponseError(error_message, url=url, response=result_json)

        for key in method.expected_keys.values():
            if key not in result_json:
                raise exc.ResponseValueError(
                    f'Key {key} not found in response, expected keys: {method.expected_keys}',
                    url=url, response=result_json
                )

        if HTTPStatus.OK <= response.status <= HTTPStatus.IM_USED:
            return result_json

        raise exc.ApiError(f'Bad API response [{response.status}]', url=url, response=result_json)
