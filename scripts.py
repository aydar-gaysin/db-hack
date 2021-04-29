import argparse
import django
import logging
import os
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from datacenter.models import Chastisement
from datacenter.models import Commendation
from datacenter.models import Lesson
from datacenter.models import Mark
from datacenter.models import Schoolkid
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist


PUPILS_NAME = 'Нина Костина'
STUDY_SUBJECT = 'Литература'


def school_kid_search(schoolkid_name):
    if not schoolkid_name:
        logging.info(f'Ошибка! Не введено имя ученика. Запустите программу'
                     f'повторно, указав уникальное имя ученика.')
        return
    try:
        schoolkid = Schoolkid.objects.get \
            (full_name__contains=schoolkid_name)
    except MultipleObjectsReturned:
        schoolkid_queryset = Schoolkid.objects.filter \
            (full_name__contains=schoolkid_name)
        logging.info(f'Нашел учеников с именем {schoolkid_name}: '
                     f'{len(schoolkid_queryset)}.\nЗапустите программу '
                     f'повторно, указав уникальное имя ученика.')
        return None
    except ObjectDoesNotExist:
        logging.info(f'Не нашел учеников с именем {schoolkid_name}. '
                     f'Запустите программу повторно, указав корректное имя '
                     f'ученика.')
        return None
    return schoolkid


def study_subject_search(schoolkid, subject):
    if not schoolkid:
        logging.info(f'Не могу найти предмет, не зная точного имени ученика!')
        return
    try:
        subject_lessons = Lesson.objects.get(
            year_of_study=schoolkid.year_of_study,
            group_letter=schoolkid.group_letter, subject__title=subject)
    except MultipleObjectsReturned:
        logging.debug(f'Предмет "{subject}" найден в базе.')
    except ObjectDoesNotExist:
        logging.info(f'Не нашел предмет с названием "{subject}". '
                     f'Запустите программу повторно, указав корректное '
                     f'название предмета.')
        return
    return subject


def create_commendation(schoolkid, subject):
    commendations = [
        'Молодец!',
        'Ты меня приятно удивил!',
        'Великолепно!',
        'Прекрасно!',
        'Ты меня очень обрадовал!',
        'Именно этого я давно ждал от тебя!',
        'Сказано здорово – просто и ясно!',
        'Ты, как всегда, точен!',
        'Очень хороший ответ!',
        'Талантливо!',
        'Ты сегодня прыгнул выше головы!',
        'Так держать!',
        'С каждым разом у тебя получается всё лучше!',
        'Я вижу, как ты стараешься!',
        'Ты растешь над собой!',
        'Ты многое сделал, я это вижу!'
    ]
    commendation = random.choice(commendations)

    subject_lessons = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter, subject__title=subject)
    lessons_quantity = len(subject_lessons)
    pick_lesson = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter,
        subject__title=subject)[random.randint(0, lessons_quantity)]
    Commendation.objects.create(text=commendation,
                                created=pick_lesson.date, schoolkid=schoolkid,
                                subject=pick_lesson.subject,
                                teacher=pick_lesson.teacher)
    logging.info(f'Ученику {schoolkid} на уроке "{pick_lesson.subject}" '
                 f'{pick_lesson.date} успешно добавлена похвала: '
                 f'"{commendation}".')


def fix_marks(schoolkid_name):
    schoolkid = Schoolkid.objects.get(full_name__contains=schoolkid_name)
    bad_points = Mark.objects.filter(schoolkid=schoolkid, points__lt=4)
    bad_points_quantity = bad_points.count()
    logging.info(f'Найдено {bad_points_quantity} плохих оценок.')
    if not bad_points_quantity:
        return
    for bad_point in bad_points:
        bad_point.points = 5
        bad_point.save()
    logging.info(f'Все плохие оценки исправлены.')


def remove_chastisements(schoolkid_name):
    schoolkid = Schoolkid.objects.get(full_name__contains=schoolkid_name)
    pupil_chastisements = Chastisement.objects.filter(schoolkid=schoolkid)
    pupil_chastisements.delete()
    logging.info(f'Все замечания для {schoolkid} успешно удалены.')


def create_parser():
    parser = argparse.ArgumentParser(description='Скрипт работает с '
                                                 'базой электронного '
                                                 'дневника. При '
                                                 'указании фамилии и '
                                                 'имени ученика:\n'
                                                 '1) меняет оценки "2" и "3"'
                                                 'на "5";\n 2) удаляет '
                                                 'замечания к ученику.\n При'
                                                 'указании названия предмета '
                                                 '(опционально), добавляет '
                                                 'похвалу ученика, выбрав '
                                                 'дату урока случайным '
                                                 'образом.')

    parser.add_argument('pupil_surname',
                        type=str, help='Укажите фамилию ученика на '
                                       'кириллице')
    parser.add_argument('pupil_name',
                        type=str, help='Укажите фамилию ученика на '
                                       'кириллице')
    parser.add_argument('-p', '--pupil_patronymic',
                        type=str, help='Укажите отчество ученика на '
                                       'кириллице')
    parser.add_argument('-s', '--subject',
                        type=str, help='Укажите название школьного предмета '
                                       'на кириллице')
    return parser


def main():
    logging.basicConfig(format='{message}', level=logging.INFO, style='{')
    parser = create_parser()
    args = parser.parse_args()
    schoolkid_surname = args.pupil_surname
    schoolkid_name = args.pupil_name
    schoolkid_patronymic = args.pupil_patronymic

    if not schoolkid_patronymic:
        schoolkid_patronymic = ''
    fullname = f'{schoolkid_surname} {schoolkid_name} {schoolkid_patronymic}'
    schoolkid = school_kid_search(fullname)
    print('------------------------------------------------------------------')
    if schoolkid:
        fix_marks(schoolkid.full_name)
        remove_chastisements(schoolkid.full_name)

    if args.subject:
        subject = args.subject
        study_subject = study_subject_search(schoolkid, subject)
        if study_subject:
            create_commendation(schoolkid, study_subject)
    print('------------------------------------------------------------------')


if __name__ == '__main__':
    main()
