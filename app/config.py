"""Настройки приложения.

Значения читаются из переменных окружения или файла .env,
а при их отсутствии берутся значения по умолчанию.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Адрес Elasticsearch
    elasticsearch_url: str = "http://localhost:9200"

    # Имя индекса, где хранятся вопросы и их векторы
    index_name: str = "so_questions"

    # Модель для получения эмбеддингов
    embedding_model: str = "all-MiniLM-L6-v2"

    # Размерность вектора этой модели (фиксирована моделью)
    embedding_dim: int = 384

    # Порог косинусной близости, выше которого вопросы считаем дубликатами
    similarity_threshold: float = 0.8


settings = Settings()
