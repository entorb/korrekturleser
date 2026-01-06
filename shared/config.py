"""Shared configuration for both Streamlit and FastAPI apps."""

from pathlib import Path

from dotenv import load_dotenv

from .helper import my_get_env

# Load environment variables from .env file in project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# Local user
USER_ID_LOCAL = 1
USER_NAME_LOCAL = "Torben"

lst = my_get_env("LLM_PROVIDERS")
LLM_PROVIDERS = [item.strip() for item in lst.split(",")]

LLM_PROVIDER_DEFAULT = LLM_PROVIDERS[0]

# FastAPI parameters
# JWT Configuration
FASTAPI_JWT_SECRET_KEY = my_get_env("FASTAPI_JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24
