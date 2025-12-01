"""Shared configuration for both Streamlit and FastAPI apps."""

from pathlib import Path

from dotenv import load_dotenv

from .helper import my_get_env, where_am_i

# Load environment variables from .env file in project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

ENV = where_am_i()

# Local user
USER_ID_LOCAL = 1
USER_NAME_LOCAL = "Torben"

# LLM configuration
LLM_PROVIDER = my_get_env("LLM_PROD") if ENV == "PROD" else my_get_env("LLM_LOCAL")
LLM_MODEL = (
    my_get_env("LLM_PROD_MODEL") if ENV == "PROD" else my_get_env("LLM_LOCAL_MODEL")
)

# FastAPI parameters
# JWT Configuration
FASTAPI_JWT_SECRET_KEY = my_get_env("FASTAPI_JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24
