"""Демонстрация работы эмбеддингов.

Показывает, что похожие по смыслу вопросы получают высокую косинусную
близость, а разные — низкую. Это проверка идеи до интеграции с Elasticsearch.

Запуск (из корня проекта, при активном .venv):
    python scripts/demo_embeddings.py
"""

import sys
from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы работал импорт пакета app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402

from app.embeddings import embed_texts  # noqa: E402

QUESTIONS = [
    "How do I reverse a string in Python?",
    "Python: how to invert the order of characters in a string?",
    "How to center a div horizontally in CSS?",
    "What is the time complexity of quicksort?",
]


def main() -> None:
    print("Считаю эмбеддинги (первый запуск скачает модель ~90 МБ)...\n")
    vectors = np.array(embed_texts(QUESTIONS))

    # Векторы нормализованы, поэтому косинусная близость = скалярное произведение
    similarity = vectors @ vectors.T

    print("Вопросы:")
    for i, question in enumerate(QUESTIONS):
        print(f"  Q{i + 1}: {question}")

    print("\nМатрица косинусной близости (1.00 = максимум):\n")
    print("       " + "    ".join(f"Q{j + 1}" for j in range(len(QUESTIONS))))
    for i in range(len(QUESTIONS)):
        row = "  ".join(f"{similarity[i][j]:.2f}" for j in range(len(QUESTIONS)))
        print(f"  Q{i + 1}   {row}")

    print(
        "\nQ1 и Q2 — про одно и то же разными словами: их близость заметно выше,"
        "\nчем у любой пары с Q3 или Q4. Именно это и ловит семантический поиск."
    )


if __name__ == "__main__":
    main()
