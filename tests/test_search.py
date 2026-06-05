"""Интеграционные тесты поиска (требуют запущенного Elasticsearch).

Если Elasticsearch недоступен, тесты аккуратно пропускаются.
Работа идёт во ВРЕМЕННОМ индексе, чтобы не затронуть рабочие данные.
"""

import pytest

from app.config import settings
from app.search import create_index, get_client, index_questions, search_similar


@pytest.fixture
def es_client():
    client = get_client()
    try:
        available = client.ping()
    except Exception:
        available = False
    if not available:
        pytest.skip("Elasticsearch недоступен — интеграционные тесты пропущены")
    return client


@pytest.fixture
def temp_index(es_client, monkeypatch):
    # Подменяем имя индекса на временное, чтобы не трогать рабочий индекс
    monkeypatch.setattr(settings, "index_name", "so_questions_pytest")
    create_index(es_client, recreate=True)
    yield es_client
    es_client.indices.delete(index=settings.index_name, ignore_unavailable=True)


def test_index_questions_returns_count(temp_index):
    count = index_questions(
        temp_index,
        ["how to reverse a string in python", "how to center a div in css"],
    )
    assert count == 2


def test_search_finds_semantic_duplicate(temp_index):
    index_questions(
        temp_index,
        [
            "how to reverse a string in python",
            "how to center a div in css",
            "what is the time complexity of quicksort",
        ],
    )
    results = search_similar(
        temp_index, "python invert the order of characters in a string", k=3
    )
    assert results
    # Ближайшим по смыслу должен оказаться вопрос про reverse a string
    assert results[0]["question"] == "how to reverse a string in python"
    assert "score" in results[0]
    assert "is_duplicate" in results[0]
