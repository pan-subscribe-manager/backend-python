import os
from fastapi import FastAPI

from finance_control_be.controllers import auth, internal, user
from finance_control_be.database import SessionLocal
from finance_control_be.models import Base

# initialize the database
with SessionLocal() as session:
    Base.metadata.create_all(bind=session.get_bind())


app = FastAPI(debug=os.environ.get("FC_DEBUG") == "1")

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(internal.router)


# uri postgres
# postgresql://user:password@postgresserver/db
