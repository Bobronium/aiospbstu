import datetime
from enum import IntEnum
from typing import List, Optional

from pydantic import Schema

from .auditory import Auditory
from .base import StrScheduleObject
from .group import Group
from .teacher import Teacher
from .type_obj import TypeObj

__all__ = ['Lesson']


class LessonType(IntEnum):
    """
    practical_lesson - практическое занятие (если нет типа, должен быть по-умолчанию)
    laboratory_work - лабораторная работа
    lecture - лекция
    seminar - семинар
    consultation - консультация
    extracurricular_facility - внеучебное занятие
    credit - зачет
    exam - экзамен
    additional_exam - доп. экзамен
    """
    practical_lesson = 0
    laboratory_work = 1
    lecture = 2
    seminar = 3
    consultation = 4
    extracurricular_facility = 5
    credit = 6
    exam = 7
    additional_exam = 8


class Lesson(StrScheduleObject):
    subject: str
    subject_short: str
    lesson_type: int = Schema(None, alias='type')
    additional_info: str
    time_start: datetime.time
    time_end: datetime.time
    parity: int
    type_obj: TypeObj = Schema(None, alias='typeObj')
    groups: List[Group]
    teachers: Optional[List[Teacher]]
    auditories: List[Auditory]
