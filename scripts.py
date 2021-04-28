import argparse
import django
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

PUPILS_NAME = 'Сергей'
STUDY_SUBJECT = 'Музыка'


def create_commendation(schoolkid_name, subject):
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
    schoolkid_queryset = Schoolkid.objects.filter\
        (full_name__contains=schoolkid_name)
    try:
        schoolkid = Schoolkid.objects.get(full_name__contains=schoolkid_name)
    except MultipleObjectsReturned:
        print(f'Нашел учеников с именем {schoolkid_name}: '
              f'{len(schoolkid_queryset)}. Не могу продолжить выполнение'
              f'сценария.')
        return
    except ObjectDoesNotExist:
        print(f'Не нашел учеников с именем {schoolkid_name}. '
              f'Не могу продолжить выполнение сценария.')
        return
    print(schoolkid)
    subject_lessons = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter, subject__title=subject)
    lessons_quantity = len(subject_lessons)
    pick_lesson = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter,
        subject__title=subject)[random.randint(0, lessons_quantity)]
    print(pick_lesson.date)
    Commendation.objects.create(text=commendation,
                                created=pick_lesson.date, schoolkid=schoolkid,
                                subject=pick_lesson.subject,
                                teacher=pick_lesson.teacher)


def fix_marks(schoolkid_name):
    schoolkid = Schoolkid.objects.filter(full_name__contains=schoolkid_name)
    bad_points = Mark.objects.filter(schoolkid=schoolkid, points__lt=4)
    for bad_point in bad_points:
        bad_point.points = 5
        bad_point.save()


def remove_chastisements(schoolkid_name):
    schoolkid = Schoolkid.objects.filter(full_name__contains=schoolkid_name)
    pupil_chastisements = Chastisement.objects.filter(schoolkid=schoolkid)
    pupil_chastisements.delete()


def main():
    return create_commendation(PUPILS_NAME, STUDY_SUBJECT)


if __name__ == '__main__':
    main()
