import os

from dotenv import load_dotenv

PLACEHOLDER_API_KEY = "your_api_key_here"


def load_env() -> None:
    load_dotenv()


def get_zhipu_api_key() -> str | None:
    load_dotenv()

    api_key = os.getenv("ZHIPU_API_KEY")
    if api_key is None:
        return None

    api_key = api_key.strip()
    if not api_key or api_key == PLACEHOLDER_API_KEY:
        return None

    return api_key
