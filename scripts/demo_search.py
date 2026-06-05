"""Демонстрация полного цикла: индексация в Elasticsearch + kNN-поиск.

Индексирует небольшой набор вопросов и ищет похожие на тестовый запрос.
Это проверка связки «эмбеддинги + Elasticsearch» до загрузки большого датасета.

Перед запуском подними Elasticsearch:
    docker compose up -d

Запуск (из корня проекта, при активном .venv):
    python scripts/demo_search.py
"""

import sys
from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы работал импорт пакета app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.search import (  # noqa: E402
    create_index,
    get_client,
    index_questions,
    search_similar,
)

QUESTIONS = [
    "How do I reverse a string in Python?",
    "How to center a div horizontally in CSS?",
    "What is the time complexity of quicksort?",
    "How to make an HTTP request in JavaScript?",
    "How can I read a file line by line in Python?",
    "What is the best way to implement a singleton in Java?",
    "How do I install packages with pip?",
    "How to convert a list to a set in Python?",
]

QUERY = "Python: how to invert the order of characters in a string?"
TOP_K = 3


def main() -> None:
    client = get_client()

    print("Создаю индекс (пересоздаю, если уже есть)...")
    create_index(client, recreate=True)

    print(f"Индексирую {len(QUESTIONS)} вопросов...")
    indexed = index_questions(client, QUESTIONS)
    print(f"Проиндексировано документов: {indexed}\n")

    print(f"Запрос: {QUERY}\n")
    print(f"Топ-{TOP_K} похожих вопросов (в скобках — косинусная близость):")
    for rank, result in enumerate(search_similar(client, QUERY, k=TOP_K), start=1):
        print(f"  {rank}. [{result['score']:.2f}] {result['question']}")

    print(
        "\nОжидаем, что на первом месте окажется вопрос про reverse a string —"
        "\nон про то же самое, что и запрос, только другими словами."
    )


if __name__ == "__main__":
    main()
