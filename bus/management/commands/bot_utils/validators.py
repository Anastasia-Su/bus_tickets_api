from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class Validators:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if a user has entered a valid email address."""

        try:
            validate_email(email)
            return True
        except ValidationError:
            return False
