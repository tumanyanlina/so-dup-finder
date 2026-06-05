"""Оценка качества поиска дубликатов на размеченных парах.

Идея: берём пару дубликатов (title1, title2), задаём title1 как запрос
и проверяем, нашёлся ли title2 среди результатов поиска.

Метрики:
- Recall@k — доля пар, где известный дубликат найден в топ-k (k = 1, 5, 10).
- MRR — средняя обратная позиция дубликата в выдаче (1/ранг), мера того,
  насколько высоко правильный ответ стоит в списке.

Перед запуском: Elasticsearch поднят и проиндексирован тем же объёмом,
что и при индексации (см. INDEXED_PAIRS ниже = MAX_PAIRS в index_data.py):
    docker compose up -d
    python scripts/index_data.py

Запуск (из корня проекта, при активном .venv):
    python scripts/evaluate.py
"""

import random
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы работал импорт пакета app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datasets import load_dataset  # noqa: E402

from app.search import get_client, search_similar  # noqa: E402

DATASET = "sentence-transformers/stackexchange-duplicates"
CONFIG = "title-title-pair"
INDEXED_PAIRS = 10000   # должно совпадать с MAX_PAIRS в scripts/index_data.py
SAMPLE_SIZE = 300       # сколько пар взять для оценки
SEARCH_K = 10           # глубина поиска
SEED = 42               # фиксируем случайность для воспроизводимости


def main() -> None:
    random.seed(SEED)

    # B615 подавлено осознанно: датасет — доверенный публичный источник (sentence-transformers)
    dataset = load_dataset(DATASET, CONFIG, split="train")  # nosec B615
    dataset = dataset.select(range(min(INDEXED_PAIRS, len(dataset))))

    # Берём валидные пары (непустые и не совпадающие дословно)
    pairs = [
        (row["title1"].strip(), row["title2"].strip())
        for row in dataset
        if row["title1"].strip()
        and row["title2"].strip()
        and row["title1"].strip() != row["title2"].strip()
    ]
    # B311 ложное срабатывание: выборка для оценки (seed фиксирован), не криптография
    sample = random.sample(pairs, min(SAMPLE_SIZE, len(pairs)))  # nosec B311

    client = get_client()

    hits_at = {1: 0, 5: 0, 10: 0}
    reciprocal_sum = 0.0

    print(f"Оцениваю на {len(sample)} парах (глубина поиска k={SEARCH_K})...\n")
    for query, target in sample:
        # Ищем чуть глубже, чтобы после удаления самого запроса осталось SEARCH_K
        results = search_similar(client, query, k=SEARCH_K + 1)
        ranked = [r["question"] for r in results if r["question"] != query][:SEARCH_K]

        rank = None
        for position, question in enumerate(ranked, start=1):
            if question == target:
                rank = position
                break

        if rank is not None:
            reciprocal_sum += 1.0 / rank
            for cutoff in hits_at:
                if rank <= cutoff:
                    hits_at[cutoff] += 1

    n = len(sample)
    print("Результаты:")
    print(f"  Recall@1:  {hits_at[1] / n:.3f}")
    print(f"  Recall@5:  {hits_at[5] / n:.3f}")
    print(f"  Recall@10: {hits_at[10] / n:.3f}")
    print(f"  MRR:       {reciprocal_sum / n:.3f}")


if __name__ == "__main__":
    main()
