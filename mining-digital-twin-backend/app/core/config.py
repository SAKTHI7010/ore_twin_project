"""
Ore Beneficiation Digital Twin - Backend Configuration
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        protected_namespaces=("settings_",),
    )

    app_env: str = "development"
    log_level: str = "INFO"
    allowed_origins: str = "http://localhost:8501"
    model_version: str = "1.0.0"
    demo_mode: bool = True
    data_source_url: str = ""

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
