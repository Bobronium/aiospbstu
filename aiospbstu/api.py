import asyncio
import logging
from typing import Optional, Union, List, Type, Tuple

from . import exceptions as exc, types
from .base import BaseScheduleApi
from .types import AnyDate, Method
from .utils.date import iso_date
from .utils.error_handler import error_handler

log = logging.getLogger('aiospbstu')


class Methods:
    # All API methods
    GET_FACULTIES = Method(
        endpoint='/faculties',
        expected_keys='faculties'
    )
    GET_TEACHERS = Method(
        endpoint='/teachers',
        expected_keys='teachers'
    )
    GET_BUILDINGS = Method(
        endpoint='/buildings',
        expected_keys='buildings'
    )
    GET_GROUP = Method(
        endpoint_template='/group/{group_id}',
        on_api_error=exc.GroupNotFoundByIDError
    )
    GET_FACULTY = Method(
        endpoint_template='/faculties/{faculty_id}',
        on_api_error=exc.FacultyNotFoundByIDError
    )
    GET_BUILDING = Method(
        endpoint_template='/buildings/{building_id}',
        on_api_error=exc.BuildingNotFoundByIDError
    )
    GET_TEACHER = Method(
        endpoint_template='/teachers/{teacher_id}',
        on_api_error=exc.TeacherNotFoundByIDError
    )
    SEARCH_GROUP = Method(
        endpoint_template='/search/groups?q={group_name}',
        expected_keys='groups'
    )
    SEARCH_TEACHER = Method(
        endpoint_template='/search/teachers?q={teacher_name}',
        expected_keys='teachers'
    )
    SEARCH_AUDITORY = Method(
        endpoint_template='/search/rooms?q={auditory_name}',
        expected_keys={'auditories_key': 'rooms'}
    )
    GET_BUILDING_AUDITORIES = Method(
        endpoint_template='/buildings/{building_id}/rooms',
        expected_keys={'auditories_key': 'rooms', 'building_key': 'building'},
        on_api_error=exc.FacultyNotFoundByIDError
    )
    GET_FACULTY_GROUPS = Method(
        endpoint_template='/faculties/{faculty_id}/groups',
        expected_keys=['faculty', 'groups'],
        on_api_error=exc.FacultyNotFoundByIDError
    )
    GET_GROUP_SCHEDULE = Method(
        endpoint_template='/scheduler/{group_id}?date={date}',
        on_api_error=exc.GroupNotFoundByIDError
    )
    GET_TEACHER_SCHEDULE = Method(
        endpoint_template='/teachers/{teacher_id}/scheduler?date={date}',
        on_api_error=exc.AuditoryNotFoundByIDError
    )
    GET_AUDITORY_SCHEDULE = Method(
        endpoint_template='/buildings/0/rooms/{auditory_id}/scheduler?date={date}'
    )

    # Site endpoints
    SITE_GROUP_SCHEDULE = Method(
        endpoint_template='/faculty/aiospbstu/groups/{group_id}?date={date}',
    )
    SITE_TEACHER_SCHEDULE = Method(
        endpoint_template='/teachers/{teacher_id}?date={date}',
    )
    SITE_AUDITORY_SCHEDULE = Method(
        endpoint_template='/places/aiospbstu/{auditory_id}?date={date}',
    )


@error_handler
class PolyScheduleAPI(BaseScheduleApi):
    """
    Simple asynchronous PolyTech schedule API client

    Example:
    .. code-block:: python3
        import asyncio
        from aiospbstu import exceptions, PolyScheduleAPI


        async def main():
            api = PolyScheduleAPI()

            faculties = await api.get_faculties()
            first_faculty = faculties[0]
            print(first_faculty.name)  # "Институт компьютерных наук и технологий"

            groups = await first_faculty.get_groups()
            schedule = await groups[0].get_schedule()

            ...

            try:
                faculty = await api.get_faculty(faculty_id=1)
            except exceptions.FacultyNotFoundByIDError as e:
                print(e.response)  # {'error': True, 'text': 'Факультет: 1 не найден'}

            ...

            api = PolyScheduleAPI(skip_exceptions=exceptions.ApiNotFoundError)

            response = await api.get_faculty(faculty_id=1)
            print(response)  # {'error': True, 'text': 'Факультет: 1 не найден'}


        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

    """
    methods = Methods()

    def __init__(self,
                 group_id: Optional[int] = None,
                 teacher_id: Optional[int] = None,
                 auditory_id: Optional[int] = None,
                 faculty_id: Optional[int] = None,
                 skip_exceptions: Optional[Union[Tuple[Type[exc.UniScheduleException]],
                                                 Type[exc.UniScheduleException]]] = (),
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        """

        :param group_id: Default group ID for requests where its needed
        :param teacher_id: Default teacher ID for schedule requests
        :param auditory_id: Default auditory ID for schedule requests
        :param faculty_id: Default faculty ID for schedule requests
        :param skip_exceptions: exceptions that will be suppressed, for example if you want to get responses
               even if server returned {"error": True}, use "skip_exceptions=exceptions.ApiResponseError"
        :param loop: asyncio event loop

        """
        super().__init__(loop)

        self.group_id = group_id
        self.teacher_id = teacher_id
        self.auditory_id = auditory_id
        self.faculty_id = faculty_id

        if not isinstance(skip_exceptions, tuple):
            skip_exceptions = (skip_exceptions,)
        for exception in skip_exceptions:
            if not issubclass(exception, BaseException):
                raise ValueError(f'Unexpected type of exception in skip_exceptions: {exception}')
            elif not issubclass(exception, exc.BaseUniScheduleError):
                log.warning(f'Expected subclass of {exc.BaseUniScheduleError} in skip_exceptions , got {exception}')

        self.skip_exceptions = skip_exceptions

    async def get_faculties(self) -> List[types.Faculty]:
        method = self.methods.GET_FACULTIES

        response = await self.request(method)

        return [types.Faculty(**faculty) for faculty in response[method.faculties_key]]

    async def get_teachers(self) -> List[types.Teacher]:
        method = self.methods.GET_TEACHERS

        response = await self.request(method)

        return [types.Teacher(**teacher)
                for teacher in response[method.teachers_key]]

    async def get_buildings(self) -> List[types.Building]:
        method = self.methods.GET_BUILDINGS

        response = await self.request(method)

        return [types.Building(**building)
                for building in response[method.buildings_key]]

    async def get_faculty(self, faculty_id: int) -> types.Faculty:
        method = self.methods.GET_FACULTY

        response = await self.request(method, faculty_id=faculty_id)

        return types.Faculty(**response)

    async def get_group(self, group_id: int) -> types.Group:
        method = self.methods.GET_GROUP

        response = await self.request(method, group_id=group_id)

        return types.Group(**response)

    async def get_teacher(self, teacher_id: int) -> types.Teacher:
        response = await self.request(self.methods.GET_TEACHER, teacher_id=teacher_id)

        return types.Teacher(**response)

    async def get_building(self, building_id: int) -> types.Building:
        response = await self.request(self.methods.GET_BUILDING, building_id=building_id)

        return types.Building(**response)

    async def search_group(self, group_name: Union[str, int]) -> List[types.Group]:
        method = self.methods.SEARCH_GROUP

        response = await self.request(method, group_name=group_name)

        return [types.Group(**group)
                for group in response[method.groups_key]] if response[method.groups_key] else []

    async def search_teacher(self, teacher_name: str) -> List[types.Teacher]:
        method = self.methods.SEARCH_TEACHER

        response = await self.request(method, teacher_name=teacher_name)

        return [types.Teacher(**teacher)
                for teacher in response[method.teachers_key]] if response[method.teachers_key] else []

    async def search_auditory(self, auditory_name: Union[str, int]) -> List[types.Auditory]:
        method = self.methods.SEARCH_AUDITORY

        response = await self.request(method, auditory_name=auditory_name)

        return [types.Auditory(**auditory)
                for auditory in response[method.auditories_key]] if response[method.auditories_key] else []

    async def get_faculty_groups(self, faculty_id: int) -> List[types.Group]:
        method = self.methods.GET_FACULTY_GROUPS

        response = await self.request(method, faculty_id=faculty_id or self.faculty_id)

        groups_faculty = types.Faculty(**response[method.faculty_key])
        return [types.Group(**group, faculty=groups_faculty)
                for group in response[method.groups_key]]

    async def get_building_auditories(self, building_id: int) -> List[types.Auditory]:
        method = self.methods.GET_BUILDING_AUDITORIES

        response = await self.request(method, building_id=building_id)

        auditories_building = types.Building(**response[method.building_key])
        return [types.Auditory(**auditory, building=auditories_building)
                for auditory in response[method.auditories_key]]

    async def get_group_schedule(self,
                                 group_id: int = None,
                                 date: Optional[AnyDate] = None) -> types.Schedule:
        response = await self.request(
            self.methods.GET_GROUP_SCHEDULE,
            group_id=group_id or self.group_id,
            date=iso_date(date)
        )
        return types.Schedule(**response)

    async def get_teacher_schedule(self, teacher_id: int = None,
                                   date: Optional[AnyDate] = None) -> types.Schedule:

        response = await self.request(
            self.methods.GET_TEACHER_SCHEDULE,
            teacher_id=teacher_id or self.teacher_id,
            date=iso_date(date)
        )
        return types.Schedule(**response)

    async def get_auditory_schedule(self, auditory_id: int = None,
                                    date: Optional[AnyDate] = None) -> types.Schedule:
        response = await self.request(
            self.methods.GET_AUDITORY_SCHEDULE,
            auditory_id=auditory_id or self.auditory_id,
            date=iso_date(date)
        )
        return types.Schedule(**response)
