"""FastAPI-приложение: поиск похожих (дублирующихся) вопросов.

Перед запуском подними Elasticsearch и проиндексируй данные:
    docker compose up -d
    python scripts/index_data.py

Запуск сервера (из корня проекта, при активном .venv):
    uvicorn app.api:app --reload

Интерактивная веб-страница для тестирования: http://localhost:8000/docs
"""

from fastapi import FastAPI

from app.schemas import SearchRequest, SearchResponse, SimilarQuestion
from app.search import get_client, search_similar

app = FastAPI(
    title="StackOverflow Duplicate Finder",
    description="Поиск похожих вопросов по смыслу (эмбеддинги + Elasticsearch).",
    version="0.1.0",
)

client = get_client()


@app.get("/health")
def health() -> dict:
    """Проверка, что сервис жив и Elasticsearch доступен."""
    return {"status": "ok", "elasticsearch": client.ping()}


@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    """Находит вопросы, похожие на заданный, по семантической близости."""
    hits = search_similar(client, request.query, k=request.k)
    results = [SimilarQuestion(**hit) for hit in hits]
    return SearchResponse(query=request.query, results=results)
