"""Тесты настроек приложения."""

from app.config import settings


def test_embedding_dim_matches_model():
    # all-MiniLM-L6-v2 выдаёт векторы размерности 384
    assert settings.embedding_dim == 384


def test_index_name_is_set():
    assert settings.index_name


def test_threshold_in_valid_range():
    assert 0.0 < settings.similarity_threshold <= 1.0
