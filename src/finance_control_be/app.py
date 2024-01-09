import os
from fastapi import FastAPI

from finance_control_be.controllers import auth, user


app = FastAPI(debug=os.environ.get("FC_DEBUG") == "1")

app.include_router(auth.router)
app.include_router(user.router)
