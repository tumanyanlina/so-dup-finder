"""Тесты модуля эмбеддингов.

Загружают реальную модель (при первом запуске она скачивается ~90 МБ,
дальше берётся из кэша), поэтому работают чуть медленнее модульных.
"""

import numpy as np

from app.config import settings
from app.embeddings import embed_text, embed_texts


def test_embed_text_dimension():
    vector = embed_text("how to read a file in python")
    assert len(vector) == settings.embedding_dim


def test_embed_text_is_normalized():
    vector = np.array(embed_text("how to read a file in python"))
    assert abs(np.linalg.norm(vector) - 1.0) < 1e-3


def test_embed_texts_returns_all():
    vectors = embed_texts(["a", "b", "c"])
    assert len(vectors) == 3
    assert all(len(v) == settings.embedding_dim for v in vectors)


def test_similar_closer_than_unrelated():
    related_a, related_b, unrelated = (
        np.array(v)
        for v in embed_texts(
            [
                "how to reverse a string in python",
                "python invert the order of characters in a string",
                "how to bake a chocolate cake",
            ]
        )
    )
    # Векторы нормализованы -> косинусная близость = скалярное произведение
    similarity_related = float(related_a @ related_b)
    similarity_unrelated = float(related_a @ unrelated)
    assert similarity_related > similarity_unrelated
