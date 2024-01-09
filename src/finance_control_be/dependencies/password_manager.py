import argon2


class PasswordManager:
    def __init__(self):
        self.hasher = argon2.PasswordHasher()

    def hash_password(self, password: str) -> str:
        return self.hasher.hash(password=password)

    def verify_password(self, input_password: str, hash: str) -> bool:
        try:
            self.hasher.verify(hash=hash, password=input_password)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False


def create_password_manager() -> PasswordManager:
    return PasswordManager()
