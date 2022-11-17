from dataclasses import dataclass
from datetime import time
from typing import Optional
import json
import logging

from aiohttp import web

logger = logging.getLogger(__name__)


@dataclass
class LessonInfo:
    class_id: int
    name: str
    weekday: int
    week: Optional[int]
    start_time: time
    end_time: time
    teacher_name: str

    @classmethod
    def from_raw(cls, lesson):
        return cls(
            class_id=lesson['class_id'],
            name=lesson['name'],
            weekday=lesson['weekday'],
            week=lesson['week'],
            start_time=lesson['start_time'],
            end_time=lesson['end_time'],
            teacher_name=lesson['teacher_name']
        )

    def to_dict(self):
        dct = self.__dict__.copy()
        dct.pop('class_id', None)
        dct['start_time'] = [self.start_time.hour,
                             self.start_time.minute]
        dct['end_time'] = [self.end_time.hour,
                           self.end_time.minute]
        return dct


@dataclass
class ClassInfo:
    class_id: int
    number: int
    letter: str

    @staticmethod
    def from_lesson(lesson):
        return ClassInfo(
            class_id=lesson['class_id'],
            number=lesson['number'],
            letter=lesson['letter']
        )

    def to_dict_with_lessons(self, lessons: list[LessonInfo]):
        dct = self.__dict__
        dct['lessons'] = []
        for lesson in lessons:
            if lesson.class_id == self.class_id:
                dct['lessons'].append(lesson.to_dict())
        return dct


@dataclass
class SchoolInfo:
    school_id: int

    def to_dict_with_classes(self, classes):
        dct = self.__dict__
        dct['classes'] = classes
        return dct


class LessonFormer:
    def __init__(self):
        self.classes: list[ClassInfo] = []
        self.lessons: list[LessonInfo] = []

    def add_class(self, class_info: ClassInfo):
        already_added_keys = [class_.class_id for class_ in self.classes]
        if class_info.class_id not in already_added_keys:
            self.classes.append(class_info)

    def add_lesson(self, lesson: LessonInfo):
        self.lessons.append(lesson)

    def add_lessons(self, lessons: list[LessonInfo]):
        self.lessons.extend(lessons)

    def classes_to_dict_with_school_info(self, school_info: SchoolInfo):
        classes = []
        for class_ in self.classes:
            classes.append(class_.to_dict_with_lessons(self.lessons))

        dct = school_info.to_dict_with_classes(classes)
        return dct

    def class_to_dict(self):
        if len(self.classes) > 1:
            raise ValueError("Expected one class but more was added")
        return self.classes[0].to_dict_with_lessons(self.lessons)


class JsonResponse(web.Response):
    def __init__(self, data):
        answer = json.dumps(
            data,
            ensure_ascii=False,
            indent=4
        )
        super(JsonResponse, self).__init__(
            text=answer,
            content_type='application/json'
        )


class ImTeapotResponse(web.Response):
    def __init__(self):
        super(ImTeapotResponse, self).__init__(
            status=418,
            reason='You are so stupid that you can not use declared interface'
        )


class ConflictResponse(web.Response):
    def __init__(self):
        super(ConflictResponse, self).__init__(
            status=409,
            reason='Some description'
        )
