import datetime

from django.core.exceptions import ValidationError


def validate_date_not_in_future(value):
    """Проверка на ввод даты из будущего."""
    if value > datetime.datetime.now().year:
        raise ValidationError('Дата из будущего')
