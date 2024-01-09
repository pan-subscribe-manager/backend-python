import os

from loguru import logger


SECRET_KEY = os.environ.get("FC_SECRET_KEY")
if not SECRET_KEY:
    # generate a 32-bit secret key for this session.
    # also, print a warning about this.
    logger.warning(
        "FC_SECRET_KEY environment variable not set. "
        "It will be generated for this session, "
        "but you are warned that all tokens derived from this "
        "will be invalidated when the server restarts."
    )
    SECRET_KEY = os.urandom(32).hex()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
