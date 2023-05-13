import pandas as pd
import itertools
import logging

from sqlalchemy import select, exc
from fastapi import HTTPException, status

from .base import BaseService
from time_api.db import tables
from time_api import schemas
from time_api.services.lessons import LessonService
from time_api.services.subgroups import SubgroupService
from time_api.services.classes import ClassService
from time_api.services.lessons_hotfix import LessonHotfixService

import datetime as dt


logger = logging.getLogger(__name__)


class TimetableService(BaseService):
    async def hotfix(
            self,
            lessons: list[dict],
            school_id: int
    ):
        hotfix_service = LessonHotfixService(self.session, self.response) 
        lesson_service = LessonService(self.session, self.response)
        for lesson in lessons:
            lesson_schema = schemas.lessons.LessonCreate(
                name=lesson['name'],
                start_time=schemas.times.Time(
                    hour=lesson['start_hour'],
                    minute=lesson['start_minute']
                ),
                end_time=schemas.times.Time(
                    hour=lesson['end_hour'],
                    minute=lesson['end_minute']
                ),
                week=lesson['week'],
                weekday=lesson['weekday'],
                room=lesson['room'] if lesson['room'] else '',
                school_id=school_id,
                teacher_id=lesson['teacher_id']
            )
            lesson_id = (await lesson_service.get(lesson_schema=lesson_schema)).lesson_id
            for_date = dt.date.today()
            days_bias = (int(lesson['weekday']) - for_date.weekday()) % 7
            for_date += dt.timedelta(days=days_bias)
            hotfix_schema = schemas.lessons.LessonHotfixCreate(
                lesson_id=lesson_id,
                name=lesson["name"],
                start_time=schemas.times.Time(
                    hour=lesson['start_hour'],
                    minute=lesson['start_minute']
                ),
                end_time=schemas.times.Time(
                    hour=lesson['end_hour'],
                    minute=lesson['end_minute']
                ),
                week=lesson['week'],
                weekday=lesson['weekday'],
                room=lesson['room'],
                school_id=school_id,
                teacher_id=lesson['teacher_id'],
                for_date=for_date
            )
            await hotfix_service.create(hotfix_schema)

    async def create(
            self,
            lessons: list[dict],
            school_id: int
    ):
        lesson_service = LessonService(session=self.session, response=self.response)
        subgroup_service = SubgroupService(session=self.session, response=self.response)
        class_service = ClassService(self.session, self.response)
        for lesson in lessons:
            lesson_schema = schemas.lessons.LessonCreate(
                name=lesson['name'],
                start_time=schemas.times.Time(
                    hour=lesson['start_hour'],
                    minute=lesson['start_minute']
                ),
                end_time=schemas.times.Time(
                    hour=lesson['end_hour'],
                    minute=lesson['end_minute']
                ),
                week=lesson['week'],
                weekday=lesson['weekday'],
                room=lesson['room'] if lesson['room'] else '',
                school_id=school_id,
                teacher_id=lesson['teacher_id']
            )
            lesson_id = (await lesson_service.create(lesson_schema))['lesson_id']
            class_id = (await class_service.get(class_schema=schemas.classes.ClassCreate(
                number=lesson['class_number'],
                letter=lesson['class_letter'],
                school_id=school_id))
            ).class_id

            subgroup_id = (await subgroup_service.get(
                    subgroup_schema=schemas.subgroups.BaseSubgroup(
                        name=lesson['subgroup'],
                        class_id=class_id
                    )
            )).subgroup_id
            await lesson_service.add_subgroup_to_lesson(
                schemas.subgroups_lessons.LessonSubgroup(
                    subgroup_id=subgroup_id,
                    lesson_id=lesson_id
                )
            )


class_teachers = {
    (8, 'а'): 'Гомонова Екатерина Борисовна',
    (8, 'б'): 'Храмцова Александра Анатольевна',
    (8, 'в'): 'Иванова Светлана Владимировна',
    (9, 'а'): 'Каменяр Анна Александровна',
    (9, 'б'): 'Брадис Ольга Львовна',
    (9, 'в'): 'Иванова Светлана Владимировна',
    (10, 'а'): 'Рынина Татьяна Михайловна',
    (10, 'б'): 'Яковлева Светлана Николаевна',
    (10, 'в'): 'Зубакова Мария Александровна',
    (11, 'а'): 'Пенигина Наталья Николаевна',
    (11, 'б'): 'Яковлева Светлана Николаевна',
    (11, 'в'): 'Яремчук Наталья Викторовна'
}

class_teachers = {
    (8, 'а'): 'Гомонова Екатерина Борисовна',
    (8, 'б'): 'Храмцова Александра Анатольевна',
    (8, 'в'): 'Иванова Светлана Владимировна',
    (9, 'а'): 'Каменяр Анна Александровна',
    (9, 'б'): 'Брадис Ольга Львовна',
    (9, 'в'): 'Иванова Светлана Владимировна',
    (10, 'а'): 'Рынина Татьяна Михайловна',
    (10, 'б'): 'Яковлева Светлана Николаевна',
    (10, 'в'): 'Зубакова Мария Александровна',
    (11, 'а'): 'Пенигина Наталья Николаевна',
    (11, 'б'): 'Яковлева Светлана Николаевна',
    (11, 'в'): 'Яремчук Наталья Викторовна'
}

required_lessons = ['Разговоры о важном', 'физика', 'история', 'русский язык',
       'биология', 'география', 'физическая культура',
       'алгебра и начала анализа', 'литература', 'информатика и ИКТ',
       'английский язык', 'алгебра', 'ИЗО',
       'информатика и информационные технологии', 'химия', 'астрономия',
       'геометрия', 'психология', 'обществознание', 'право', 'ОБЖ', 'черчение']

def get_teacher(class_number, class_letter, lesson: str) -> str:
    return 1, ''

def read_df(file: bytes):
    df = pd.read_excel(file, header=4)
    df['WeekDay'] = df['WeekDay'].fillna(method='ffill')
    df.iloc[1] = df.iloc[1].fillna(method='ffill')
    return df

def split_class_name(class_name):
    try:
        letter = class_name[-1]
    except Exception:
        return None, None
    number = class_name[:(len(class_name) + 1) // 2]
    return number, letter.capitalize()

def split_time(time: str):
    start_time, end_time = (
        [int(y) for y in x.strip().split('.')] for x in time.split('-')
    )
    return start_time, end_time

def insert_columns():
    for column in ['StartHour', 'StartMinute', 'EndMinute', 'EndHour', 'ClassLetter', 'ClassNumber']:
        df.insert(0, column, pd.Series([]))

def split_lesson(lesson_with_room):
    if '\\' in lesson_with_room.split()[-1]:
            room = lesson_with_room.split()[-1].split('\\')
            lesson = ' '.join(lesson_with_room.split()[:-1])
    else:
        try:
            room = [int(lesson_with_room.split()[-1]), int(lesson_with_room.split()[-1])]
        except ValueError:
            room = [None, None]
            lesson = ' '.join(lesson_with_room.split())
        else:
            lesson = ' '.join(lesson_with_room.split()[:-1])
    if lesson == 'психология акт.зал':
        lesson = 'психология'
    return lesson, room


def get_weekday_number(weekday_name):
    return {
        'понедельник': 0,
        'вторник': 1,
        'среда': 2,
        'четверг': 3,
        'пятница': 4,
        'суббота': 5}[weekday_name.lower()]
    

def split_lesson_times(start: tuple[int, int], end: tuple[int, int]):
    if (end[0] * 60 + end[1] - start[0] * 60 - start[1]) <= 80:
        return [(start[0], start[1], end[0], end[1])]
    first_start_hour, first_start_minute = start
    second_end_hour, second_end_minute = end
    first_end_minute = (first_start_minute + 40) % 60
    first_end_hour = (first_start_hour + (first_start_minute + 40) // 60) % 24
    second_start_minute = (second_end_minute - 40) % 60
    second_start_hour = (second_end_hour + (second_end_minute - 40) // 60) % 24
    first_data = (first_start_hour, first_start_minute, first_end_hour, first_end_minute)
    second_data = (second_start_hour, second_start_minute, second_end_hour, second_end_minute)
    return [first_data, second_data]

def process_day(start: int, end: int, df, ndf):
    class_columns = [column for column in df.columns if column.startswith('Unnamed')]
    class_names = dict([(column, df[column].iloc[start]) for column in class_columns])
    for i in range(start + 1, end):
        if str(df.iloc[i].WeekDay).lower() == 'nan':
            continue
        for class_column in class_names:
            lesson = str(df[class_column].iloc[i])
            if lesson.lower() != 'nan' and str(df.iloc[i].Time).lower() != 'nan':
                lesson = lesson.replace('(1/2гр)', ' ')
                number, letter = split_class_name(class_names[class_column])
                start, end = split_time(df.iloc[i].Time)
                for start_hour, start_minute, end_hour, end_minute in split_lesson_times(start, end):
                    lesson_without_room, room = split_lesson(lesson)
                    teacher_id, teacher = get_teacher(number, letter, lesson_without_room)
                    weekday = get_weekday_number(df.iloc[i].WeekDay)
                    required = lesson in required_lessons
                    for room_index, subgroup in enumerate(['англ. Татьяна Петровна', 'англ. Светлана Николаевна']):
                        new_row = pd.DataFrame({
                            'class_number': [number],
                            'class_letter': [letter],
                            'subgroup': [subgroup],
                            'name': [lesson_without_room],
                            'teacher_id': [teacher_id],
                            'week': [0],
                            'weekday': [weekday],
                            'start_hour': [start_hour],
                            'start_minute': [start_minute],
                            'end_hour': [end_hour],
                            'end_minute': [end_minute],
                            'room': room[room_index],
                            'required': required,
                            'teacher': teacher
                        })
                        ndf = pd.concat([ndf, new_row], ignore_index = True)
    return ndf
                

def process_by_days(df, ndf):
    gen = filter(
        lambda index: (df.iloc[index].Time == 'время'),
        range(len(df))
    )
    end = next(gen)
    while True:
        try:
            start = end
            end = next(gen)
            ndf = process_day(start, end, df, ndf)
        except StopIteration:
            end = len(df)
            ndf = process_day(start, end, df, ndf) 
            break
    return ndf


def get_lessons_list(lessons_file: bytes) -> list[dict]:
    ndf = pd.DataFrame(columns=[
        'class_number', 
        'class_letter', 
        'subgroup', 
        'name',
        'teacher_id',
        'week',
        'weekday',
        'start_hour',
        'start_minute',
        'end_hour',
        'end_minute',
        'room',
        'required'
    ])
    return process_by_days(read_df(lessons_file), ndf).to_dict(orient='records')


def get_timetable_data(lessons_file: bytes) -> dict[str, list]:
    ndf = pd.DataFrame(columns=[
        'class_number', 
        'class_letter', 
        'subgroup', 
        'name',
        'teacher_id',
        'week',
        'weekday',
        'start_hour',
        'start_minute',
        'end_hour',
        'end_minute',
        'room',
        'required'
    ])
    data = process_by_days(read_df(lessons_file), ndf).to_dict()
    ret = {}
    ret['class_numbers'] = list(set(data['class_number'].values()))
    ret['class_letters'] = list(set(data['class_letter'].values()))
    ret['subgroup_names'] = list(set(data['subgroup'].values()))
    return ret

