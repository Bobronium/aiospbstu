from typing import ClassVar, Union, TypeVar

UniScheduleException = TypeVar('UniScheduleException', bound='BaseUniScheduleError')


class BaseUniScheduleError(Exception):

    def __init__(self,
                 message: str = None,
                 url: str = None,
                 response: Union[dict, str] = None,
                 cause: ClassVar[Exception] = None):

        if not message:
            message = 'Exception occurred'
        if url:
            message += f', request: {url}'
            if response:
                message += f', response: {response}'
        if cause:
            message += f'. Caused by {cause.__class__.__name__}: {cause}'

        super().__init__(message)
        self.url = url
        self.response = response
        self.cause = cause


class NetworkError(BaseUniScheduleError):
    pass


class AioHttpError(NetworkError):
    pass


class BadResponseCodeError(NetworkError):
    pass


class ApiError(BaseUniScheduleError):
    pass


class ApiResponseError(ApiError):
    pass


class ApiInternalError(ApiResponseError):
    expected_text = 'Ошибка получения данных'


class ResponseValueError(ApiResponseError, ValueError):
    pass


class ResponseTypeError(ApiResponseError, TypeError):
    pass


class JSONDecodeError(ApiResponseError, ValueError):
    pass


class NotFoundError(BaseUniScheduleError):
    pass


class ApiNotFoundError(ApiResponseError, NotFoundError):
    expected_text = 'не найден'


class GroupNotFoundByIDError(ApiNotFoundError):
    pass


class TeacherNotFoundByIDError(ApiNotFoundError):
    pass


class FacultyNotFoundByIDError(ApiNotFoundError):
    pass


class BuildingNotFoundByIDError(ApiNotFoundError):
    pass


class AuditoryNotFoundByIDError(ApiNotFoundError):
    pass


class LocalNotFoundError(NotFoundError):
    pass


class DayNotFoundByDate(LocalNotFoundError):
    pass
