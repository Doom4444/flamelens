from typing import Generator
from app.config import Settings, get_settings


def get_app_settings() -> Settings:
    """Dependency for injecting application settings."""
    return get_settings()
