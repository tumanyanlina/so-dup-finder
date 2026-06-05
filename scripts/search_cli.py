"""Интерактивный поиск похожих вопросов по проиндексированным данным.

Запускать после scripts/index_data.py. Вводишь вопрос — получаешь похожие.
Пустая строка завершает работу.

Запуск (из корня проекта, при активном .venv):
    python scripts/search_cli.py
"""

import sys
from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы работал импорт пакета app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.search import get_client, search_similar  # noqa: E402

TOP_K = 5


def main() -> None:
    client = get_client()
    print("Поиск похожих вопросов. Введи вопрос (пустая строка — выход).\n")

    while True:
        query = input("Вопрос> ").strip()
        if not query:
            print("Выход.")
            break

        results = search_similar(client, query, k=TOP_K)
        if not results:
            print("  ничего не найдено\n")
            continue

        for rank, result in enumerate(results, start=1):
            print(f"  {rank}. [{result['score']:.2f}] {result['question']}")
        print()


if __name__ == "__main__":
    main()
