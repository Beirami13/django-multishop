from django.core.exceptions import ValidationError


def phone(value):
    if not value.isdigit():
        raise ValidationError("Phone number must contain only digits.")

    if not value.startswith("0"):
        raise ValidationError("Phone number must start with 0.")

    if len(value) != 11:
        raise ValidationError("Phone number must be 11 digits.")
