from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class EmailNotValidError:
    pass


class Validators:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False
