"""FastAPI-приложение: поиск похожих (дублирующихся) вопросов.

Перед запуском подними Elasticsearch и проиндексируй данные:
    docker compose up -d
    python scripts/index_data.py

Запуск сервера (из корня проекта, при активном .venv):
    uvicorn app.api:app --reload

Веб-интерфейс:          http://localhost:8000/
Документация (Swagger): http://localhost:8000/docs
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.config import settings
from app.schemas import SearchRequest, SearchResponse, SimilarQuestion
from app.search import get_client, search_similar

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(
    title="StackOverflow Duplicate Finder",
    description="Поиск похожих вопросов по смыслу (эмбеддинги + Elasticsearch).",
    version="0.1.0",
)

client = get_client()


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """Отдаёт веб-страницу поиска."""
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    """Проверка, что сервис жив и Elasticsearch доступен."""
    return {"status": "ok", "elasticsearch": client.ping()}


@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    """Находит вопросы, похожие на заданный, по семантической близости."""
    hits = search_similar(client, request.query, k=request.k)
    results = [SimilarQuestion(**hit) for hit in hits]
    return SearchResponse(
        query=request.query,
        threshold=settings.similarity_threshold,
        results=results,
    )
