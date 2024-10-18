import http

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


header = {
    "user-agent": UserAgent().random
}

WEEK_DAYS = {
    1: 'Понедельник',
    2: 'Вторник',
    3: 'Среда',
    4: 'Четверг',
    5: 'Пятница',
    6: 'Суббота',
}

group = '21-ИСП(9)-4'

result_message_week = ''
result_message_day = ""

url = f"https://backend-isu.gstou.ru/api/timetable/public/entrie/?group={group}"
response = requests.get(url, headers=header)

def get_info_week():
    link = 'https://timetable.gstou.ru/'
    res = requests.get(link, headers=header)
    if response.status_code == http.HTTPStatus.OK:
        soup = BeautifulSoup(res.content, 'html.parser')
        info = soup.find('ul', class_='infoForUser')
        result = info.text.strip().replace('\n', '--').split('--')
        week_info = {
            'Дата': result[0],
            'День недели': result[1],
            'Неделя': result[2]
        }
        return week_info
    else:
        return 'Произошла ошибка'

if response.status_code == http.HTTPStatus.OK:
    schedule_data = response.json()
    sorted_schedule = sorted(schedule_data, key=lambda x: (x.get('week_day', 0), x.get('period', 0)))
    week_info_data = get_info_week()
    class_schedule = {}

    for lesson in sorted_schedule:

        discipline = lesson.get('discipline', {}).get('name', 'Неизвестная дисциплина')
        week_day = lesson.get('week_day', 'Не указан')
        week_number = lesson.get('week', 'Не указан')
        period = lesson.get('period', 'Не указан')
        auditorium = lesson.get('auditorium', {}).get('name', 'Не указана')
        teacher = lesson.get('discipline', {}).get('lecture_teacher', {}).get('name', 'Преподаватель не указан')

        if week_info_data['Неделя'][0] == str(week_number) or week_number is None:
            day_name = WEEK_DAYS.get(week_day, 'Не указан')
            lesson_info = {
                'Пара': period,
                'Дисциплина': discipline,
                'Аудитория': auditorium,
                'Преподаватель': teacher,
                'Неделя': '1 и 2' if week_number is None else week_number
            }

            if day_name not in class_schedule:
                class_schedule[day_name] = []
            class_schedule[day_name].append(lesson_info)

    sorted_class_schedule = {day: class_schedule[day] for day in WEEK_DAYS.values() if day in class_schedule}

    for day, lessons in sorted_class_schedule.items():

        result_message_week += f"День недели: {day}\n"

        for lesson in lessons:
            result_message_week += f" Пара: {lesson['Пара']} | {lesson['Дисциплина']} | {lesson['Аудитория']} | {lesson['Преподаватель']}\n"
        result_message_week += ("-" * 5) + '\n'

    result_message_day += f"День недели: {week_info_data['День недели']}\n"
    for lesson in sorted_class_schedule[week_info_data['День недели']]:
        result_message_day += f"Пара: {lesson['Пара']} | {lesson['Дисциплина']} | {lesson['Аудитория']} | {lesson['Преподаватель']}\n"

else:
    result_message_day += 'Произошла ошибка при получении данных расписания'
    result_message_week += 'Произошла ошибка при получении данных расписания'

def get_day_schedule():
    return result_message_day


def get_week_schedule():
    return result_message_week

