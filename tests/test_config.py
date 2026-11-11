import pytest

from api_lab.config import get_zhipu_api_key


@pytest.fixture(autouse=True)
def disable_dotenv(monkeypatch):
    monkeypatch.setattr("api_lab.config.load_dotenv", lambda: None)


def test_get_api_key_from_env(monkeypatch):
    monkeypatch.setenv("ZHIPU_API_KEY", "test_key_123")

    assert get_zhipu_api_key() == "test_key_123"


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("ZHIPU_API_KEY", raising=False)

    assert get_zhipu_api_key() is None


def test_placeholder_api_key_is_ignored(monkeypatch):
    monkeypatch.setenv("ZHIPU_API_KEY", "your_api_key_here")

    assert get_zhipu_api_key() is None


def test_blank_api_key_is_ignored(monkeypatch):
    monkeypatch.setenv("ZHIPU_API_KEY", "   ")

    assert get_zhipu_api_key() is None
