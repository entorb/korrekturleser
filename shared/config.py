"""Shared configuration for both Streamlit and FastAPI apps."""

from pathlib import Path

from dotenv import load_dotenv

from .helper import my_get_env

# Load environment variables from .env file in project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


# Local user
USER_ID_LOCAL = 1
USER_NAME_LOCAL = "Torben"

# LLM configuration
LLM_PROVIDER = "Gemini"
LLM_MODEL = "gemini-2.5-flash-lite"  # "gemini-2.5-flash", "gemini-2.5-pro"
# LLM_MODEL = "Ollama"
# LLM_PROVIDER = "llama3.2:1b"

# FastAPI parameters
# JWT Configuration
JWT_SECRET_KEY = my_get_env("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24
