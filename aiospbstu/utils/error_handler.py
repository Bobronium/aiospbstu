import functools
import inspect
import logging

import pydantic

from .. import exceptions

log = logging.getLogger('aiospbstu')


def handle_exceptions(func):
    @functools.wraps(func)
    async def inner(class_instance, *args, **kwargs):
        try:
            skip_exceptions = class_instance.skip_exceptions
        except AttributeError:
            skip_exceptions = ()
            log.warning(f'Unable to get skip_exceptions for {func.__name__} from class {type(class_instance).__name__}')

        # TODO: figure out better way of catching pydantic.ValidationError
        try:
            try:
                return await func(class_instance, *args, **kwargs)
            except pydantic.ValidationError as e:
                raise exceptions.ResponseValueError(cause=e)
        except skip_exceptions as e:
            log.exception('Skipped exception in request:', exc_info=e)
            return getattr(e, 'response', None)

    return inner


def error_handler(cls):
    for coroutine in (obj for obj in cls.__dict__.values() if inspect.iscoroutinefunction(obj)):
        setattr(cls, coroutine.__name__, handle_exceptions(coroutine))

    return cls
