# methods here are only for internal use (DEBUG=1)

from fastapi import APIRouter
from finance_control_be.const import DEBUG

router = APIRouter(prefix="/internal", tags=["user", "authentication", "internal"], include_in_schema=False)

if DEBUG:
    @router.post("/users/initialize")
    def initialize_user() -> None:
        from finance_control_be.dependencies.password_manager import PasswordManager
        from finance_control_be.models.user import User
        from finance_control_be.database import SessionLocal

        with SessionLocal() as session:
            user = User.new_hashed(password="admin", password_manager=PasswordManager())
            user.username = "admin"
            user.full_name = "Admin@admin"
            user.email = "admin@email.tld"
            session.add(user)
            session.commit()
