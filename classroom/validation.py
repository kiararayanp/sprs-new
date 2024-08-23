import re


class Validation:
    @staticmethod
    def is_empty(value):
        """Check if the value is empty."""
        return not bool(value.strip())

    @staticmethod
    def min_length(value, min_length):
        """Check if the value meets the minimum length requirement."""
        return len(value) >= min_length

    @staticmethod
    def is_valid_email(value):
        """Check if the value is a valid email address using regular expressions."""
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_regex, value))

    @staticmethod
    def is_valid_name(value):
        """Check if the value only contains spaces and alphabets."""
        name_regex = r"^[A-Za-z ]+$"
        return bool(re.match(name_regex, value))

    @staticmethod
    def does_password_match(password, confirm_password):
        """Check if the password and confirm password match."""
        return password == confirm_password

    @staticmethod
    def does_image_exist(value):
        """Check if the incoming image file is not empty."""
        return not bool(value)

    @staticmethod
    def is_valid_image(value):
        """Check if the value is a valid image file."""
        image_extensions = ["jpg", "jpeg", "png", "webp", "gif"]
        return value.split(".")[-1].lower() in image_extensions

    @staticmethod
    def validate_all(value, validations):
        """Validate the value against a list of validation functions."""
        for validation in validations:
            if not validation(value):
                return False
        return True
