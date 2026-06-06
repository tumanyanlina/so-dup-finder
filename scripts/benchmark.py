"""Замер производительности поиска: латентность запросов.

Прогоняет набор типовых запросов много раз и считает статистику времени
ответа функции search_similar (эмбеддинг запроса + kNN-поиск в Elasticsearch).
Первые запросы идут на "разогрев" (загрузка модели) и в статистику не входят.

Перед запуском: Elasticsearch поднят и проиндексирован.
Запуск (из корня проекта, при активном .venv):
    python scripts/benchmark.py
"""

import statistics
import sys
import time
from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы работал импорт пакета app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.search import get_client, search_similar  # noqa: E402

QUERIES = [
    "how to read a file in python",
    "how to reverse a string",
    "center a div with css",
    "convert string to integer",
    "how to undo last git commit",
    "remove duplicates from a list",
    "what is a closure in javascript",
    "how to loop through a dictionary",
    "merge two dictionaries",
    "how to handle exceptions",
]
WARMUP = 3   # сколько прогонов на разогрев (не учитываются)
REPEATS = 5  # сколько раз прогнать весь список для замера


def main() -> None:
    client = get_client()

    print(f"Разогрев ({WARMUP} запросов, загрузка модели)...")
    for query in QUERIES[:WARMUP]:
        search_similar(client, query, k=5)

    print(f"Замер: {REPEATS} прогонов по {len(QUERIES)} запросов...\n")
    latencies_ms = []
    for _ in range(REPEATS):
        for query in QUERIES:
            start = time.perf_counter()
            search_similar(client, query, k=5)
            latencies_ms.append((time.perf_counter() - start) * 1000)

    latencies_ms.sort()
    n = len(latencies_ms)
    p95 = latencies_ms[max(0, int(n * 0.95) - 1)]

    print(f"Измерено запросов:    {n}")
    print(f"Средняя латентность:  {statistics.mean(latencies_ms):.1f} мс")
    print(f"Медиана:              {statistics.median(latencies_ms):.1f} мс")
    print(f"p95:                  {p95:.1f} мс")
    print(f"min / max:            {latencies_ms[0]:.1f} / {latencies_ms[-1]:.1f} мс")
    print(f"\nПропускная способность: ~{1000 / statistics.mean(latencies_ms):.0f} запросов/с")


if __name__ == "__main__":
    main()
