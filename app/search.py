"""Работа с Elasticsearch: индекс с векторным полем и kNN-поиск.

Каждый вопрос хранится вместе со своим эмбеддингом в поле типа dense_vector.
Поиск похожих вопросов выполняется приближённым kNN (алгоритм HNSW).

Про оценку близости:
для similarity="cosine" Elasticsearch считает _score = (1 + cosine) / 2.
Чтобы оценки совпадали с привычной косинусной близостью (0..1, как в демо
эмбеддингов), мы переводим _score обратно: cosine = 2 * _score - 1.
"""

from elasticsearch import Elasticsearch, helpers

from app.config import settings
from app.embeddings import embed_text, embed_texts


def get_client() -> Elasticsearch:
    """Создаёт клиент Elasticsearch по адресу из настроек."""
    return Elasticsearch(settings.elasticsearch_url)


def create_index(client: Elasticsearch, recreate: bool = False) -> None:
    """Создаёт индекс с текстовым полем question и векторным полем embedding.

    Если recreate=True, существующий индекс удаляется и создаётся заново.
    """
    if client.indices.exists(index=settings.index_name):
        if recreate:
            client.indices.delete(index=settings.index_name)
        else:
            return

    client.indices.create(
        index=settings.index_name,
        mappings={
            "properties": {
                "question": {"type": "text"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": settings.embedding_dim,
                    "index": True,
                    "similarity": "cosine",
                },
            }
        },
    )


def index_questions(
    client: Elasticsearch,
    questions: list[str],
    batch_size: int = 256,
) -> int:
    """Считает эмбеддинги вопросов и пакетно загружает их в индекс.

    Пустые и повторяющиеся вопросы отбрасываются.
    Возвращает количество успешно проиндексированных документов.
    """
    unique = list(dict.fromkeys(q.strip() for q in questions if q and q.strip()))

    vectors = embed_texts(unique, batch_size=64, show_progress=True)

    actions = (
        {
            "_index": settings.index_name,
            "_source": {"question": question, "embedding": vector},
        }
        for question, vector in zip(unique, vectors)
    )

    success, _ = helpers.bulk(client, actions, chunk_size=batch_size)
    client.indices.refresh(index=settings.index_name)
    return success


def search_similar(
    client: Elasticsearch,
    query: str,
    k: int = 5,
    num_candidates: int = 100,
) -> list[dict]:
    """Находит k наиболее похожих вопросов через kNN.

    Возвращает список словарей вида {"question": str, "score": float},
    где score — косинусная близость (0..1, больше = похожее).
    """
    query_vector = embed_text(query)

    response = client.search(
        index=settings.index_name,
        knn={
            "field": "embedding",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": max(num_candidates, k),
        },
        size=k,
        source=["question"],
    )

    threshold = settings.similarity_threshold
    results = []
    for hit in response["hits"]["hits"]:
        cosine = 2 * hit["_score"] - 1
        results.append(
            {
                "question": hit["_source"]["question"],
                "score": cosine,
                "is_duplicate": cosine >= threshold,
            }
        )
    return results
