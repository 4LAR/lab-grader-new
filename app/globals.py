import os

from config import Config

config = Config("config.ini")
config.print()

################################################################################

import re

#
def all_names_varians(name):
    # Удаляем все пробелы
    name = re.sub(r'\s+', '', name)

    # Проверка форматов имен
    patterns = [
        r'([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.([А-ЯЁA-Z][а-яёa-z]+)',  # "И.О.Фамилия"
        r'([А-ЯЁA-Z][а-яёa-z]+)([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.',  # "ФамилияИ.О."
        r'([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.([А-ЯЁA-Z][а-яёa-z]+)',  # "И.О. Фамилия" (с пробелом)
        r'([А-ЯЁA-Z][а-яёa-z]+) ([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.'   # "Фамилия И.О." (с пробелом)
    ]

    for pattern in patterns:
        match = re.match(pattern, name)
        if match:
            initials = f"{match.group(1)}.{match.group(2)}."
            surname = match.group(3)
            return f"{surname} {initials}"

    # Если ни один формат не подошел, возвращаем исходное имя
    return name

def fix_full_name(full_name):
    name_parts = re.sub(r'\s+', ' ', full_name).strip().split()

    if len(name_parts) == 3:
        return f"{name_parts[0]} {name_parts[1][0]}.{name_parts[2][0]}."

    return full_name

################################################################################

import yaml

def load_course_config(course_file):
    with open(course_file, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def get_lab_config(course_config, lab_id):
    course = course_config.get('course', None)
    if course is None:
        return None
    labs = course.get('labs', None)
    if labs is None:
        return None
    lab_key = str(lab_id)
    return labs.get(lab_key, None)
