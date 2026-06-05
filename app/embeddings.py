"""Преобразование текста в векторы (эмбеддинги).

Используется модель sentence-transformers, заданная в настройках (app/config.py).
Векторы нормализуются (длина = 1), поэтому косинусная близость равна
скалярному произведению — это удобно и согласуется с kNN-поиском Elasticsearch.
"""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import settings


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Загружает модель один раз и кэширует её (повторные вызовы — без перезагрузки)."""
    return SentenceTransformer(settings.embedding_model)


def embed_text(text: str) -> list[float]:
    """Один текст -> нормализованный вектор."""
    vector = get_model().encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_texts(
    texts: list[str],
    batch_size: int = 64,
    show_progress: bool = False,
) -> list[list[float]]:
    """Список текстов -> список нормализованных векторов."""
    vectors = get_model().encode(
        texts,
        normalize_embeddings=True,
        batch_size=batch_size,
        show_progress_bar=show_progress,
    )
    return [vector.tolist() for vector in vectors]
