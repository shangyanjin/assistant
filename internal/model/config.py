"""
Configuration models
"""
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Application configuration"""
    api_url: str = "http://127.0.0.1:11434"
    default_font_size: int = 12
    theme: str = "default"

