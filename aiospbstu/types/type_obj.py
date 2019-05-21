from enum import Enum

from pydantic import Schema, validator

from ..types.base import StrScheduleObject

__all__ = ['TypeObj', 'LessonTypeName']


class LessonTypeName(str, Enum):
    practical_lesson = 'Практика'
    laboratory_work = 'Лабораторная'
    lecture = 'Лекция'
    seminar = 'Семинар'
    consultation = 'Консультация'
    extracurricular_facility = 'Внеучебное занятие'
    credit = 'Зачёт'
    diff_credit = 'Дифференцированный зачёт'
    coursework = 'Курсовая работа'
    exam = 'Экзамен'
    additional_exam = 'Доп. экзамен'

    # RUZ API returns names in the plural form
    # TODO: Think about better solution
    api_laboratory_work = 'Лабораторные'
    api_lecture = 'Лекции'
    api_extracurricular_facility = 'Внеучебные занятия'
    api_consultation = 'Консультации'
    api_credit = 'Зачет'


class TypeObj(StrScheduleObject):
    type_id: int = Schema(None, alias='id')
    name: LessonTypeName
    abbr: str

    @validator('name')
    def _fix_name(cls, enum_field: LessonTypeName):
        # RUZ API returns names in the plural form, fixing it
        if enum_field.name.startswith('api_'):
            return getattr(LessonTypeName, enum_field.name.replace('api_', ''))
        return enum_field
