"""Загрузка и предпросмотр датасета дубликатов Stack Exchange.

Датасет: sentence-transformers/stackexchange-duplicates, формат title-title-pair.
Каждая строка — пара заголовков вопросов, помеченных как дубликаты.

Запуск (из корня проекта, при активном .venv):
    python scripts/explore_data.py
"""

from datasets import load_dataset

DATASET = "sentence-transformers/stackexchange-duplicates"
CONFIG = "title-title-pair"
PREVIEW_COUNT = 5


def main() -> None:
    print(f"Загружаю {DATASET} [{CONFIG}]...")
    print("(первый раз скачивается с Hugging Face, дальше берётся из кэша)\n")

    # B615 подавлено осознанно: датасет — доверенный публичный источник (sentence-transformers)
    dataset = load_dataset(DATASET, CONFIG, split="train")  # nosec B615

    print(f"Всего пар дубликатов: {len(dataset):,}")
    print(f"Колонки: {dataset.column_names}\n")
    print(f"Первые {PREVIEW_COUNT} пар (заголовок 1 <-> заголовок 2):\n")

    for i in range(PREVIEW_COUNT):
        row = dataset[i]
        print(f"{i + 1}.")
        print(f"   title1: {row['title1']}")
        print(f"   title2: {row['title2']}")
        print()


if __name__ == "__main__":
    main()
