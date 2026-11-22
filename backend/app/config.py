import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # LLM Provider: "gemini" or "lmstudio"
    LLM_PROVIDER: str = "gemini"

    # Google Gemini Settings (Official google-genai SDK)
    GEMINI_API_KEY: str = ""
    GEMINI_CHAT_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBED_MODEL: str = "gemini-embedding-001"

    # LM Studio Settings (Local offline development)
    LMSTUDIO_BASE_URL: str = "http://localhost:1234/v1"
    LMSTUDIO_CHAT_MODEL: str = "local-model"
    LMSTUDIO_EMBED_MODEL: str = "text-embedding-nomic-embed-text-v1.5"
    LMSTUDIO_API_KEY: str = "not-needed"

    # Server & CORS
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "https://citemind-frontend.vercel.app,http://localhost:3000,http://127.0.0.1:3000"

    # Evaluation & Data Storage
    ENABLE_EVAL_LOGGING: bool = True
    FAITHFULNESS_THRESHOLD: float = 0.70
    DATA_DIR: str = "backend/data"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return ["*"]
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        for default_origin in ["https://citemind-frontend.vercel.app", "http://localhost:3000"]:
            if default_origin not in origins:
                origins.append(default_origin)
        return origins


settings = Settings()
