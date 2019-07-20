import datetime
from enum import IntEnum
from typing import List

from pydantic import validator

from .base import BaseScheduleObject
from .lesson import Lesson

__all__ = ['Day', 'Weekday']


class Weekday(IntEnum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6


class Day(BaseScheduleObject):
    weekday: Weekday
    date: datetime.date
    lessons: List[Lesson]

    @property
    def iso_weekday(self):
        return self.weekday + 1

    def __iter__(self):
        for lesson in self.lessons:
            yield lesson

    @validator('weekday', pre=True)
    def _format_weekday(cls, weekday):
        return weekday - 1

    @validator('lessons', pre=True, whole=True)
    def _filter_lessons_duplicates(cls, lessons: list):
        filtered_lessons = []
        is_duplicate = False

        for next_lesson_index, lesson in enumerate(lessons, start=1):

            if is_duplicate:
                is_duplicate = False
                continue

            next_lesson = lessons[next_lesson_index] if next_lesson_index < len(lessons) else None
            is_duplicate = (next_lesson and next_lesson['subject'] == lesson['subject']
                            and lesson['time_start'] == next_lesson['time_start']
                            and lesson['typeObj']['id'] == next_lesson['typeObj']['id'])

            if is_duplicate:
                if lesson['auditories'] and next_lesson['auditories']:
                    lesson['auditories'] += [audit for audit in next_lesson['auditories']
                                             if audit not in lesson['auditories']]
                if lesson['teachers'] and next_lesson['teachers']:
                    lesson['teachers'] += [teacher for teacher in next_lesson['teachers']
                                           if teacher not in lesson['teachers']]
                elif next_lesson['teachers']:
                    lesson['teachers'] = next_lesson['teachers']

                if lesson['additional_info'] != next_lesson['additional_info']:
                    lesson['additional_info'] += '\n' + next_lesson['additional_info']

            filtered_lessons.append(lesson)
        return filtered_lessons
