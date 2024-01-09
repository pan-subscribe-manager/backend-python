class InvalidCredentialsException(Exception):
    def __init__(self):
        super().__init__("Invalid credential received.")


class InvalidTokenException(Exception):
    def __init__(self):
        super().__init__("Invalid token received.")


class InactiveUserException(Exception):
    def __init__(self):
        super().__init__("Inactive user.")
