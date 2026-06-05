"""Индексация реального датасета вопросов StackExchange в Elasticsearch.

Берёт пары дубликатов, разворачивает их в общий список уникальных вопросов
и загружает в индекс. Количество пар ограничено (MAX_PAIRS), чтобы расчёт
эмбеддингов укладывался в разумное время на ноутбуке.

Перед запуском подними Elasticsearch:
    docker compose up -d

Запуск (из корня проекта, при активном .venv):
    python scripts/index_data.py
"""

import sys
from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы работал импорт пакета app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datasets import load_dataset  # noqa: E402

from app.search import create_index, get_client, index_questions  # noqa: E402

DATASET = "sentence-transformers/stackexchange-duplicates"
CONFIG = "title-title-pair"
MAX_PAIRS = 10000  # сколько пар взять из датасета (больше -> дольше считается)


def build_corpus(max_pairs: int) -> list[str]:
    """Загружает пары дубликатов и разворачивает их в общий список вопросов."""
    # B615 подавлено осознанно: датасет — доверенный публичный источник (sentence-transformers)
    dataset = load_dataset(DATASET, CONFIG, split="train")  # nosec B615
    if max_pairs:
        dataset = dataset.select(range(min(max_pairs, len(dataset))))
    # title1 и title2 — это оба вопросы, объединяем в один корпус
    return list(dataset["title1"]) + list(dataset["title2"])


def main() -> None:
    client = get_client()
    print(f"Загружаю датасет (первые {MAX_PAIRS} пар)...")
    corpus = build_corpus(MAX_PAIRS)
    print(f"Вопросов до удаления дублей: {len(corpus):,}")
    print("Создаю индекс (пересоздаю, если уже есть)...")
    create_index(client, recreate=True)
    print("Считаю эмбеддинги и загружаю в Elasticsearch (это займёт пару минут)...")
    indexed = index_questions(client, corpus)
    print(f"\nГотово. Уникальных вопросов в индексе: {indexed:,}")


if __name__ == "__main__":
    main()
