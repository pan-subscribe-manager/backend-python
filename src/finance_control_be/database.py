import os
from loguru import logger

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URI = os.environ.get("FC_DATABASE_URI")
if not DATABASE_URI:
    raise ValueError(
        "FC_DATABASE_URI environment variable not set. It must be a valid SQLAlchemy connection string."
    )


engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)
